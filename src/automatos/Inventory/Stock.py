from src.automatos.Item.AbstractControlledItem import AbstractControlledItem

class Stock:
    """
    Класс для одной ячейки (партии) препарата.
    Хранит ссылку на препарат, количество, серию и местоположение.
    """
    def __init__(self, item: AbstractControlledItem, quantity: int, batch_or_lot: str, location_code: str):
        """
        :param item: объект ControlledItem (ссылка на препарат)
        :param quantity: начальное количество (целое число)
        :param batch_or_lot: номер серии/партии
        :param location_code: код места хранения (например, 'A1')
        """
        self.item = item
        self.quantity = quantity
        self.batch_or_lot = batch_or_lot
        self.location_code = location_code

    def increase(self, qty: int) -> None:
        """Увеличить количество на qty."""
        if qty <= 0:
            raise ValueError("Количество для добавления должно быть положительным")
        self.quantity += qty

    def decrease(self, qty: int) -> None:
        """Уменьшить количество на qty (если хватает)."""
        if qty <= 0:
            raise ValueError("Количество для списания должно быть положительным")
        if not self.is_available(qty):
            raise ValueError(f"Недостаточно товара: требуется {qty}, доступно {self.quantity}")
        self.quantity -= qty

    def is_available(self, qty: int) -> bool:
        """Проверить, достаточно ли количества в ячейке."""
        return self.quantity >= qty