# inventory.py – класс склада, который управляет ячейками

from decimal import Decimal
from src.controlledItem_stock import Stock   # импортируем класс Stock из соседнего файла

class Inventory:
    def __init__(self, storage_id, is_locked=False):
        self.storage_id = storage_id          # название склада
        self.stocks = {}                      # словарь: ключ – ID препарата, значение – список ячеек Stock
        self.is_locked = is_locked            # заблокирован ли склад для выдачи

    # Добавить ячейку на склад
    def add_stock(self, stock):
        item_id = stock.item.id
        if item_id not in self.stocks:
            self.stocks[item_id] = []
        self.stocks[item_id].append(stock)

    # Найти все ячейки с данным препаратом
    def find_item_stock(self, item_id):
        return self.stocks.get(item_id, [])

    # Посчитать общее количество препарата на всех ячейках
    def get_total_balance(self, item_id):
        total = Decimal(0)
        for stock in self.find_item_stock(item_id):
            total += stock.quantity
        return total

    # Умная выдача: если в одной ячейке не хватает, берёт из других
    def reserve_and_withdraw(self, item_id, qty):
        if self.is_locked:
            raise PermissionError("Склад заблокирован")

        requested = Decimal(str(qty))
        if requested <= 0:
            raise ValueError("Количество должно быть положительным")

        stocks_for_item = self.find_item_stock(item_id)
        if not stocks_for_item:
            raise ValueError(f"Препарат {item_id} не найден")

        remaining = requested
        withdrawn = []   # список, откуда и сколько взяли

        for stock in stocks_for_item:
            if remaining == 0:
                break
            available = stock.quantity
            if available == 0:
                continue

            if available >= remaining:
                # в этой ячейке достаточно – берём всё остальное
                stock.decrease(remaining)
                withdrawn.append({
                    "location": stock.location_code,
                    "batch": stock.batch_or_lot,
                    "quantity": remaining,
                    "item_id": item_id
                })
                remaining = Decimal(0)
            else:
                # в этой ячейке не хватает – берём всё, что есть
                stock.decrease(available)
                withdrawn.append({
                    "location": stock.location_code,
                    "batch": stock.batch_or_lot,
                    "quantity": available,
                    "item_id": item_id
                })
                remaining -= available

        if remaining > 0:
            raise ValueError(f"Не хватает препарата {item_id}. Доступно: {self.get_total_balance(item_id)}")

        return withdrawn

    # Сверка фактических остатков с данными из аудит-лога
    def un_reconciliation(self, audit_log):
        discrepancies = {}
        for item_id, stocks in self.stocks.items():
            # Фактические остатки по партиям
            actual = {}
            for stock in stocks:
                batch = stock.batch_or_lot
                actual[batch] = actual.get(batch, Decimal(0)) + stock.quantity

            # Ожидаемые остатки из лога
            expected = audit_log.get_expected_balances(item_id)

            # Сравниваем все партии
            all_batches = set(actual.keys()) | set(expected.keys())
            for batch in all_batches:
                act = actual.get(batch, Decimal(0))
                exp = expected.get(batch, Decimal(0))
                if act != exp:
                    if item_id not in discrepancies:
                        discrepancies[item_id] = {}
                    discrepancies[item_id][batch] = act - exp   # разница (положительная – излишек, отрицательная – недостача)
        return discrepancies