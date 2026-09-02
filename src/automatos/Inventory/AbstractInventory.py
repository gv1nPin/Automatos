# inventory.py – класс склада, который управляет ячейками
from abc import ABC, abstractmethod

class AbstractInventory(ABC):
    """
    Склад, управляющий множеством ячеек (Stock).
    Хранит список ячеек в виде словаря: {item_id: [Stock1, Stock2, ...]}.
    """
    def __init__(self, storage_id: str, is_locked: bool = False):
        """
        :param storage_id: идентификатор склада (например, 'СКЛАД-1')
        :param is_locked: заблокирован ли склад для выдачи (по умолчанию False)
        """
        self.storage_id = storage_id
        self.is_locked = is_locked
        # Словарь, где ключ — item_id (строка), значение — список объектов Stock
        self.stocks = {}

    def _get_stock_list(self, item_id: str) -> list:
        """Вспомогательный метод: возвращает список ячеек для данного item_id (создаёт, если нет)."""
        if item_id not in self.stocks:
            self.stocks[item_id] = []
        return self.stocks[item_id]

    def add_stock(self, stock: Stock) -> None:
        """Добавить новую ячейку (Stock) на склад."""
        item_id = stock.item.item_id
        self._get_stock_list(item_id).append(stock)

    def find_item_stock(self, item_id: str) -> list:
        """Вернуть все ячейки (Stock) для данного артикула."""
        return self.stocks.get(item_id, [])

    def get_total_balance(self, item_id: str) -> int:
        """Подсчитать общее количество препарата по всем ячейкам."""
        total = 0
        for stock in self.find_item_stock(item_id):
            total += stock.quantity
        return total

    def reserve_and_withdraw(self, item_id: str, qty: int) -> None:
        """
        Умное списание: забираем нужное количество из нескольких ячеек по порядку.
        Если не хватает во всех ячейках — выбрасываем исключение.
        """
        if self.is_locked:
            raise PermissionError("Склад заблокирован, выдача невозможна.")
        if qty <= 0:
            raise ValueError("Количество для списания должно быть положительным")

        stocks_for_item = self.find_item_stock(item_id)
        if not stocks_for_item:
            raise ValueError(f"Препарат с ID {item_id} не найден на складе.")

        # Сначала проверяем, хватает ли суммарно
        total_available = self.get_total_balance(item_id)
        if total_available < qty:
            raise ValueError(f"Недостаточно препарата {item_id}: требуется {qty}, доступно {total_available}")

        # Списываем, проходя по ячейкам по порядку (например, по сериям)
        remaining = qty
        for stock in stocks_for_item:
            if remaining <= 0:
                break
            # Сколько можно взять из этой ячейки
            take = min(remaining, stock.quantity)
            if take > 0:
                stock.decrease(take)   # метод decrease сам проверит наличие
                remaining -= take

        # Если после цикла осталось > 0 (теоретически не должно, т.к. мы проверили общее количество)
        if remaining > 0:
            raise RuntimeError("Ошибка при списании: не удалось списать всё количество.")

    def run_reconciliation(self, audit_log: list) -> bool:
        """
        Сверка остатков с журналом аудита (audit_log).
        audit_log — это список словарей с записями вида:
        {'item_id': 'ABC', 'change': +10} или {'item_id': 'ABC', 'change': -5}
        Предполагаем, что в логе учтены все операции (начальный остаток считается нулевым).
        Возвращает True, если фактические остатки совпадают с расчётными по логу, иначе False.
        """
        # Строим расчётный баланс из лога
        expected = {}  # item_id -> расчётное количество
        for record in audit_log:
            item_id = record['item_id']
            change = record['change']
            expected[item_id] = expected.get(item_id, 0) + change

        # Сравниваем с фактическими остатками на складе
        for item_id, expected_qty in expected.items():
            actual_qty = self.get_total_balance(item_id)
            if actual_qty != expected_qty:
                # Можно также логировать несоответствие, но пока просто возвращаем False
                return False
        # Проверяем, нет ли на складе препаратов, которых нет в логе (возможно, лишние)
        for item_id in self.stocks:
            if item_id not in expected:
                # Если на складе есть препарат, но в логе он не отражён — это ошибка
                return False
        return True