# controlledItem_stock.py – описываем препараты и ячейки

from decimal import Decimal   # библиотека для точных расчётов (чтобы не было ошибок с дробями)

# Класс "Препарат" – просто хранит ID, название и описание
class ControlledItem:
    def __init__(self, item_id, name, description=""):
        self.id = item_id          # уникальный артикул, например "DRUG001"
        self.name = name           # "Аспирин"
        self.description = description

# Класс "Ячейка" – одно место хранения с определённым препаратом, количеством, партией и местом
class Stock:
    def __init__(self, item, quantity, batch_or_lot, location_code):
        self.item = item                    # ссылка на препарат (объект ControlledItem)
        self.quantity = Decimal(str(quantity))  # количество (преобразуем в Decimal)
        self.batch_or_lot = batch_or_lot    # номер партии, например "BATCH-001"
        self.location_code = location_code  # код места, например "Шкаф-А1"

    # Метод для увеличения количества
    def increase(self, qty):
        if qty <= 0:
            raise ValueError("Количество должно быть положительным")
        self.quantity += Decimal(str(qty))

    # Метод для уменьшения количества
    def decrease(self, qty):
        if qty <= 0:
            raise ValueError("Количество должно быть положительным")
        if not self.is_available(qty):
            raise ValueError(f"В ячейке {self.location_code} недостаточно товара")
        self.quantity -= Decimal(str(qty))

    # Проверка, хватит ли товара
    def is_available(self, qty):
        return self.quantity >= Decimal(str(qty))