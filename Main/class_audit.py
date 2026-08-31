# audit.py – журнал всех приходов и расходов

from decimal import Decimal

class AuditLog:
    def __init__(self):
        self.records = []   # список записей

    # Добавить запись
    def add_record(self, operation, item_id, qty, location, batch, timestamp):
        self.records.append({
            "operation": operation,   # "increase" или "decrease"
            "item_id": item_id,
            "quantity": Decimal(str(qty)),
            "location": location,
            "batch": batch,
            "timestamp": timestamp
        })

    # По записям вычислить ожидаемый остаток по партиям для одного препарата
    def get_expected_balances(self, item_id):
        balances = {}
        for rec in self.records:
            if rec["item_id"] != item_id:
                continue
            batch = rec["batch"]
            qty = rec["quantity"]
            if rec["operation"] == "increase":
                balances[batch] = balances.get(batch, Decimal(0)) + qty
            elif rec["operation"] == "decrease":
                balances[batch] = balances.get(batch, Decimal(0)) - qty
        return balances