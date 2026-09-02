class MedicalInventory(AbstractInventory):
    # Высокоуровневый адаптер склада для интеграции с DistributionManager.
    def __init__(self, storage_id: str, is_locked: bool = False):
        super().__init__(storage_id, is_locked)

    def is_in_stock(self, item_id: str, quantity: int) -> bool:
        if self.is_locked:
            return False
        return self.get_total_balance(item_id) >= quantity

    def deduct_item(self, item_id: str, quantity: int) -> None:
        self.reserve_and_withdraw(item_id, quantity)

    def add_item(self, item_id: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Количество для возврата должно быть положительным")

        stocks_for_item = self.find_item_stock(item_id)
        if not stocks_for_item:
            raise ValueError(f"Критическая ошибка: номенклатура {item_id} отсутствует на складе.")

        stocks_for_item[0].increase(quantity)