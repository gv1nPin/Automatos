from unittest.mock import Mock
import pytest
from src.automatos.Inventory.MedicalInventory import MedicalInventory

@pytest.fixture
def inventory():
    """Фикстура для создания свежего объекта склада перед каждым тестом."""
    return MedicalInventory(storage_id="MED-WAR-123")


@pytest.fixture
def mock_stock_factory():
    """Фабрика для генерации mock-объектов Stock с возможностью изменения остатка."""
    def _create_mock_stock(item_id: str, quantity: int):
        stock = Mock()
        stock.item = Mock()
        stock.item.item_id = item_id
        stock.quantity = quantity
        
        # Имитируем поведение уменьшения и увеличения остатка ячейки
        stock.decrease = lambda amt: setattr(stock, 'quantity', stock.quantity - amt)
        stock.increase = lambda amt: setattr(stock, 'quantity', stock.quantity + amt)
        return stock
    return _create_mock_stock


# ==========================================
# ТЕСТЫ МЕТОДА is_in_stock
# ==========================================

def test_is_in_stock_success(inventory, mock_stock_factory):
    # Добавляем 2 партии одного препарата суммой 15 единиц
    inventory.add_stock(mock_stock_factory("MED001", 10))
    inventory.add_stock(mock_stock_factory("MED001", 5))

    assert inventory.is_in_stock("MED001", 12) is True
    assert inventory.is_in_stock("MED001", 15) is True
    assert inventory.is_in_stock("MED001", 16) is False


def test_is_in_stock_when_locked(inventory, mock_stock_factory):
    inventory.add_stock(mock_stock_factory("MED001", 10))
    inventory.is_locked = True

    # Если склад заблокирован, метод всегда должен возвращать False, вне зависимости от остатка
    assert inventory.is_in_stock("MED001", 5) is False


# ==========================================
# ТЕСТЫ МЕТОДА deduct_item
# ==========================================

def test_deduct_item_success(inventory, mock_stock_factory):
    stock1 = mock_stock_factory("MED001", 10)
    stock2 = mock_stock_factory("MED001", 5)
    inventory.add_stock(stock1)
    inventory.add_stock(stock2)

    # Метод должен вызвать базовый reserve_and_withdraw и последовательно списать 12 штук
    inventory.deduct_item("MED001", 12)

    assert stock1.quantity == 0
    assert stock2.quantity == 3
    assert inventory.get_total_balance("MED001") == 3


def test_deduct_item_raises_error_when_locked(inventory, mock_stock_factory):
    inventory.add_stock(mock_stock_factory("MED001", 10))
    inventory.is_locked = True

    with pytest.raises(PermissionError, match="Склад заблокирован, выдача невозможна."):
        inventory.deduct_item("MED001", 5)


# ==========================================
# ТЕСТЫ МЕТОДА add_item
# ==========================================

def test_add_item_success_adds_to_first_stock(inventory, mock_stock_factory):
    stock1 = mock_stock_factory("MED001", 10)
    stock2 = mock_stock_factory("MED001", 5)
    inventory.add_stock(stock1)
    inventory.add_stock(stock2)

    # Добавляем 8 единиц. По логике кода они должны прибавиться к ПЕРВОЙ ячейке списка (index 0)
    inventory.add_item("MED001", 8)

    assert stock1.quantity == 18
    assert stock2.quantity == 5  # Вторая ячейка остается без изменений
    assert inventory.get_total_balance("MED001") == 23


@pytest.mark.parametrize("invalid_qty", [0, -10])
def test_add_item_invalid_quantity_raises_error(inventory, invalid_qty):
    with pytest.raises(ValueError, match="Количество для возврата должно быть положительным"):
        inventory.add_item("MED001", invalid_qty)


def test_add_item_missing_nomenclature_raises_error(inventory):
    with pytest.raises(ValueError, match="Критическая ошибка: номенклатура MED999 отсутствует на складе."):
        inventory.add_item("MED999", 10)
