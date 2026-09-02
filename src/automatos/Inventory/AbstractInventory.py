from abc import ABC, abstractmethod

class AbstractInventory(ABC):
    # Базовый абстрактный класс для управления складскими запасами и ячейками хранения.
    def __init__(self, storage_id: str, is_locked: bool = False):
        self.storage_id = storage_id
        self.is_locked = is_locked
        self.stocks = {}

    def _get_stock_list(self, item_id: str) -> list:
        if item_id not in self.stocks:
            self.stocks[item_id] = []
        return self.stocks[item_id]

    def add_stock(self, stock) -> None:
        item_id = stock.item.item_id
        self._get_stock_list(item_id).append(stock)

    def find_item_stock(self, item_id: str) -> list:
        return self.stocks.get(item_id, [])

    def get_total_balance(self, item_id: str) -> int:
        total = 0
        for stock in self.find_item_stock(item_id):
            total += stock.quantity
        return total

    def reserve_and_withdraw(self, item_id: str, qty: int) -> None:
        if self.is_locked:
            raise PermissionError("Склад заблокирован, выдача невозможна.")
        if qty <= 0:
            raise ValueError("Количество для списания должно быть положительным")

        stocks_for_item = self.find_item_stock(item_id)
        if not stocks_for_item:
            raise ValueError(f"Препарат с ID {item_id} не найден на складе.")

        total_available = self.get_total_balance(item_id)
        if total_available < qty:
            raise ValueError(f"Недостаточно препарата {item_id}: требуется {qty}, доступно {total_available}")

        remaining = qty
        for stock in stocks_for_item:
            if remaining <= 0:
                break
            take = min(remaining, stock.quantity)
            if take > 0:
                stock.decrease(take)
                remaining -= take

        if remaining > 0:
            raise RuntimeError("Ошибка при списании: не удалось списать все количество.")

    def run_reconciliation(self, audit_log: list) -> bool:
        expected = {}
        for record in audit_log:
            item_id = record['item_id']
            change = record['change']
            expected[item_id] = expected.get(item_id, 0) + change

        for item_id, expected_qty in expected.items():
            actual_qty = self.get_total_balance(item_id)
            if actual_qty != expected_qty:
                return False
        for item_id in self.stocks:
            if item_id not in expected:
                return False
        return True

    @abstractmethod
    def is_in_stock(self, item_id: str, quantity: int) -> bool:
        pass

    @abstractmethod
    def deduct_item(self, item_id: str, quantity: int) -> None:
        pass

    @abstractmethod
    def add_item(self, item_id: str, quantity: int) -> None:
        pass
