import pytest

# /Users/jackjack/pythonstart/PROJECT/Automatos/Test_automatos/test_class_Controlleditem.py
from ..class_ControlledItem import ControlledItem

def test_access_allowed():
    item = ControlledItem(
        drugs_legal_position="A",
        drugs_licensed_position="B",
        id_drugs_legal=1,
        id_drugs_licensed=2,
        licensed=True,
        unit=10,
        level_clearance=2,
    )
    # Пользователь с допуском 3 может получить лекарство (3 >= 2)
    assert item.access(3) is True
    # Пользователь с допуском 1 — не может (1 < 2)
    assert item.access(1) is False

def test_control_line():
    licensed_item = ControlledItem(
        drugs_legal_position="A",
        drugs_licensed_position="B",
        id_drugs_legal=3,
        id_drugs_licensed=4,
        licensed=True,
        unit=5,
        level_clearance=1,
    )
    non_licensed_item = ControlledItem(
        drugs_legal_position="C",
        drugs_licensed_position="D",
        id_drugs_legal=5,
        id_drugs_licensed=6,
        licensed=False,
        unit=7,
        level_clearance=0,
    )

    assert licensed_item.control_line() is True
    assert non_licensed_item.control_line() is False

def test_quantity_ok():
    item = ControlledItem(
        drugs_legal_position="E",
        drugs_licensed_position="F",
        id_drugs_legal=7,
        id_drugs_licensed=8,
        licensed=False,
        unit=3,
        level_clearance=0,
    )
    result = item.quantity(3)
    assert result == "Доступно 3 шт."

def test_quantity_error():
    item = ControlledItem(
        drugs_legal_position="G",
        drugs_licensed_position="H",
        id_drugs_legal=9,
        id_drugs_licensed=10,
        licensed=False,
        unit=0,
        level_clearance=0,
    )
    try:
        item.quantity(0)
        assert False, "Ожидалось исключение ValueError"
    except ValueError:
        pass  # Всё ок: исключение выброшено
