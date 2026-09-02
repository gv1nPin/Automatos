# test_class_Inventory.py
import pytest
from class_Inventory import ControlledItem, Stock, Inventory

@pytest.fixture
def sample_item():
    return ControlledItem("T001", "Тестовый препарат")

@pytest.fixture
def sample_stock(sample_item):
    return Stock(sample_item, 10, "BATCH1", "LOC1")

@pytest.fixture
def inventory(sample_item):
    inv = Inventory("TEST-1")
    # Добавим несколько ячеек для тестов
    inv.add_stock(Stock(sample_item, 10, "BATCH1", "LOC1"))
    inv.add_stock(Stock(sample_item, 5, "BATCH2", "LOC2"))
    # Добавим другой препарат для проверки
    other = ControlledItem("T002", "Другой")
    inv.add_stock(Stock(other, 100, "BATCH3", "LOC3"))
    return inv

def test_stock_increase(sample_stock):
    sample_stock.increase(5)
    assert sample_stock.quantity == 15

def test_stock_decrease(sample_stock):
    sample_stock.decrease(3)
    assert sample_stock.quantity == 7

def test_stock_decrease_too_much(sample_stock):
    with pytest.raises(ValueError, match="Недостаточно товара"):
        sample_stock.decrease(20)

def test_stock_is_available(sample_stock):
    assert sample_stock.is_available(5) is True
    assert sample_stock.is_available(15) is False

def test_inventory_find_item_stock(inventory, sample_item):
    stocks = inventory.find_item_stock(sample_item.item_id)
    assert len(stocks) == 2
    assert all(s.item.item_id == sample_item.item_id for s in stocks)

def test_inventory_total_balance(inventory, sample_item):
    assert inventory.get_total_balance(sample_item.item_id) == 15

def test_inventory_reserve_and_withdraw(inventory, sample_item):
    inventory.reserve_and_withdraw(sample_item.item_id, 12)
    # Проверяем остатки в каждой ячейке
    stocks = inventory.find_item_stock(sample_item.item_id)
    # Первая ячейка была 10, вторая 5. Списано 12 -> первая стала 0, вторая 3
    assert stocks[0].quantity == 0
    assert stocks[1].quantity == 3
    assert inventory.get_total_balance(sample_item.item_id) == 3

def test_reserve_and_withdraw_not_enough(inventory, sample_item):
    with pytest.raises(ValueError, match="Недостаточно препарата"):
        inventory.reserve_and_withdraw(sample_item.item_id, 20)

def test_reserve_and_withdraw_locked(inventory):
    inventory.is_locked = True
    with pytest.raises(PermissionError, match="Склад заблокирован"):
        inventory.reserve_and_withdraw("T001", 5)

def test_run_reconciliation(inventory):
    # Создаём лог, соответствующий текущим остаткам:
    # Было добавлено: T001 - 15, T002 - 100
    # Операций списания нет
    audit_log = [
        {'item_id': 'T001', 'change': 15},
        {'item_id': 'T002', 'change': 100},
    ]
    assert inventory.run_reconciliation(audit_log) is True

    # Если лог не соответствует
    bad_log = [
        {'item_id': 'T001', 'change': 10},  # должно быть 15
        {'item_id': 'T002', 'change': 100},
    ]
    assert inventory.run_reconciliation(bad_log) is False

def test_run_reconciliation_extra_item(inventory):
    # Если в логе нет T002, но на складе он есть
    audit_log = [
        {'item_id': 'T001', 'change': 15},
    ]
    assert inventory.run_reconciliation(audit_log) is False