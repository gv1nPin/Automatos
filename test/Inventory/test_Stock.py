from unittest.mock import Mock
import pytest
from src.automatos.Inventory.Stock import Stock

@pytest.fixture
def mock_item():
    """Фикстура для создания mock-объекта препарата."""
    item = Mock()
    item.item_id = "MED-001"
    item.name = "Тестовый препарат"
    return item


@pytest.fixture
def stock(mock_item):
    """Фикстура для создания свежего объекта ячейки хранения (10 штук)."""
    return Stock(item=mock_item, quantity=10, batch_or_lot="BATCH123", location_code="A1")


# ==========================================
# ТЕСТЫ ИНИЦИАЛИЗАЦИИ
# ==========================================

def test_stock_initialization(stock, mock_item):
    """Проверка корректности создания объекта и присвоения атрибутов."""
    assert stock.item == mock_item
    assert stock.quantity == 10
    assert stock.batch_or_lot == "BATCH123"
    assert stock.location_code == "A1"


# ==========================================
# ТЕСТЫ МЕТОДА is_available
# ==========================================

@pytest.mark.parametrize("requested_qty, expected_result", [
    (5, True),    # Запрос меньше, чем есть
    (10, True),   # Запрос ровно столько, сколько есть
    (11, False),  # Запрос больше, чем есть
])
def test_is_available(stock, requested_qty, expected_result):
    """Проверка доступности запрашиваемого количества."""
    assert stock.is_available(requested_qty) is expected_result


# ==========================================
# ТЕСТЫ МЕТОДА increase
# ==========================================

def test_increase_success(stock):
    """Успешное увеличение остатка товара."""
    stock.increase(5)
    assert stock.quantity == 15


@pytest.mark.parametrize("invalid_qty", [0, -5])
def test_increase_invalid_quantity_raises_error(stock, invalid_qty):
    """Попытка передать некорректное число на добавление должна вызвать ошибку."""
    with pytest.raises(ValueError, match="Количество для добавления должно быть положительным"):
        stock.increase(invalid_qty)


# ==========================================
# ТЕСТЫ МЕТОДА decrease
# ==========================================

def test_decrease_success(stock):
    """Успешное частичное списание товара."""
    stock.decrease(4)
    assert stock.quantity == 6


def test_decrease_to_zero_success(stock):
    """Успешное списание в ноль (забираем весь доступный остаток)."""
    stock.decrease(10)
    assert stock.quantity == 0


@pytest.mark.parametrize("invalid_qty", [0, -3])
def test_decrease_invalid_quantity_raises_error(stock, invalid_qty):
    """Попытка передать некорректное число на списание должна вызвать ошибку."""
    with pytest.raises(ValueError, match="Количество для списания должно быть положительным"):
        stock.decrease(invalid_qty)


def test_decrease_not_enough_stock_raises_error(stock):
    """Попытка списать больше, чем есть в ячейке, должна вызвать ошибку с остатком."""
    with pytest.raises(ValueError, match="Недостаточно товара: требуется 15, доступно 10"):
        stock.decrease(15)
