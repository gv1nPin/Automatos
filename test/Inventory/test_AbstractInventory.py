from unittest.mock import Mock
import pytest
from src.automatos.Inventory.AbstractInventory import AbstractInventory 

# 1. Создаем минимальный рабочий класс-наследник для тестирования абстрактного класса
class MockInventory(AbstractInventory):
    def is_in_stock(self, item_id: str, quantity: int) -> bool:
        return self.get_total_balance(item_id) >= quantity

    def deduct_item(self, item_id: str, quantity: int) -> None:
        self.reserve_and_withdraw(item_id, quantity)

    def add_item(self, item_id: str, quantity: int) -> None:
        pass


# 2. Фикстуры для подготовки окружения
@pytest.fixture
def inventory():
    """Создает чистый объект склада перед каждым тестом."""
    return MockInventory(storage_id="WAR-01")


@pytest.fixture
def mock_stock_factory():
    """Фабрика для создания mock-объектов Stock с заданными параметрами."""
    def _create_mock_stock(item_id: str, quantity: int):
        stock = Mock()
        stock.item = Mock()
        stock.item.item_id = item_id
        stock.quantity = quantity
        # Метод decrease уменьшает внутренний quantity mock-объекта
        stock.decrease = lambda amt: setattr(stock, 'quantity', stock.quantity - amt)
        return stock
    return _create_mock_stock


# 3. Тесты инициализации и базовой структуры
def test_inventory_initialization(inventory):
    assert inventory.storage_id == "WAR-01"
    assert inventory.is_locked is False
    assert inventory.stocks == {}


def test_add_stock_and_find_item_stock(inventory, mock_stock_factory):
    stock1 = mock_stock_factory("T001", 10)
    stock2 = mock_stock_factory("T001", 5)
    stock3 = mock_stock_factory("T002", 20)

    inventory.add_stock(stock1)
    inventory.add_stock(stock2)
    inventory.add_stock(stock3)

    assert len(inventory.find_item_stock("T001")) == 2
    assert len(inventory.find_item_stock("T002")) == 1
    assert inventory.find_item_stock("T003") == []


def test_get_total_balance(inventory, mock_stock_factory):
    inventory.add_stock(mock_stock_factory("T001", 10))
    inventory.add_stock(mock_stock_factory("T001", 15))
    inventory.add_stock(mock_stock_factory("T002", 5))

    assert inventory.get_total_balance("T001") == 25
    assert inventory.get_total_balance("T002") == 5
    assert inventory.get_total_balance("T003") == 0


# 4. Тесты метода reserve_and_withdraw
def test_reserve_and_withdraw_success_single_stock(inventory, mock_stock_factory):
    stock = mock_stock_factory("T001", 10)
    inventory.add_stock(stock)

    inventory.reserve_and_withdraw("T001", 7)
    assert stock.quantity == 3
    assert inventory.get_total_balance("T001") == 3


def test_reserve_and_withdraw_success_multi_stock(inventory, mock_stock_factory):
    stock1 = mock_stock_factory("T001", 10)
    stock2 = mock_stock_factory("T001", 5)
    inventory.add_stock(stock1)
    inventory.add_stock(stock2)

    inventory.reserve_and_withdraw("T001", 12)
    # 12 списывается как: 10 из первой ячейки (остаток 0) и 2 из второй (остаток 3)
    assert stock1.quantity == 0
    assert stock2.quantity == 3
    assert inventory.get_total_balance("T001") == 3


def test_reserve_and_withdraw_locked_raises_error(inventory, mock_stock_factory):
    inventory.is_locked = True
    inventory.add_stock(mock_stock_factory("T001", 10))

    with pytest.raises(PermissionError, match="Склад заблокирован, выдача невозможна."):
        inventory.reserve_and_withdraw("T001", 5)


@pytest.mark.parametrize("invalid_qty", [0, -5])
def test_reserve_and_withdraw_invalid_qty_raises_error(inventory, invalid_qty):
    with pytest.raises(ValueError, match="Количество для списания должно быть положительным"):
        inventory.reserve_and_withdraw("T001", invalid_qty)


def test_reserve_and_withdraw_item_not_found_raises_error(inventory):
    with pytest.raises(ValueError, match="Препарат с ID T001 не найден на складе."):
        inventory.reserve_and_withdraw("T001", 5)


def test_reserve_and_withdraw_not_enough_balance_raises_error(inventory, mock_stock_factory):
    inventory.add_stock(mock_stock_factory("T001", 10))

    with pytest.raises(ValueError, match="Недостаточно препарата T001: требуется 15, доступно 10"):
        inventory.reserve_and_withdraw("T001", 15)


# 5. Тесты метода run_reconciliation (Сверка)
def test_run_reconciliation_success(inventory, mock_stock_factory):
    inventory.add_stock(mock_stock_factory("T001", 15))
    inventory.add_stock(mock_stock_factory("T002", 100))

    audit_log = [
        {"item_id": "T001", "change": 15},
        {"item_id": "T002", "change": 100}
    ]
    assert inventory.run_reconciliation(audit_log) is True


def test_run_reconciliation_failed_wrong_quantity(inventory, mock_stock_factory):
    inventory.add_stock(mock_stock_factory("T001", 15))

    audit_log = [{"item_id": "T001", "change": 10}]  # Ожидается 10, а по факту 15
    assert inventory.run_reconciliation(audit_log) is False


def test_run_reconciliation_failed_missing_in_log(inventory, mock_stock_factory):
    inventory.add_stock(mock_stock_factory("T001", 15))
    inventory.add_stock(mock_stock_factory("T002", 50))

    audit_log = [{"item_id": "T001", "change": 15}]  # T002 забыли внести в лог аудита
    assert inventory.run_reconciliation(audit_log) is False
