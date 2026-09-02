import pytest
from Main.class_AbstractControlledItem import AbstractControlledItem

# =========================================================================
# ВСПОМОГАТЕЛЬНЫЙ КЛАСС-НАСЛЕДНИК ДЛЯ ТЕСТИРОВАНИЯ АБСТРАКЦИИ
# =========================================================================

class ConcreteTestItem(AbstractControlledItem):
    """Минимальный рабочий подкласс, чтобы обойти запрет создания абстрактного класса."""
    def get_full_spec(self) -> str:
        return f"Тест: {self.name}"


# =========================================================================
# UNIT-ТЕСТЫ ДЛЯ КЛАССА ABSTRACTCONTROLLEDITEM
# =========================================================================

def test_cannot_instantiate_abstract_class_directly():
    """Проверка правила Абстракции: напрямую создать объект базового класса нельзя."""
    # Блок try/except проверяет, что Python выбросит TypeError при попытке вызова
    with pytest.raises(TypeError) as exc_info:
        AbstractControlledItem(item_id="1", name="Тест", danger_level=1, unit="шт")
    
    # Проверяем, что в тексте ошибки написано про абстрактный класс
    assert "Can't instantiate abstract class" in str(exc_info.value)


def test_abstract_class_constructor_initializes_fields_correctly():
    """Проверка Инкапсуляции: родительский конструктор правильно записывает свойства."""
    # Создаем объект через наш тестовый подкласс
    item = ConcreteTestItem(
        item_id="FMJ-99",
        name="Патроны",
        danger_level=3,
        unit="пачка",
        is_restricted=True
    )
    
    # Проверяем, что базовые поля, описанные в ТЗ Руслана, созданы корректно
    assert item.item_id == "ITM-99"
    assert item.name == "Патроны"
    assert item.danger_level == 3
    assert item.unit == "пачка"
    assert item.is_restricted is True


def test_abstract_class_default_fields():
    """Проверка, что флаг контроля по умолчанию всегда равен False."""
    item = ConcreteTestItem(
        item_id="ITM-01",
        name="Бинт",
        danger_level=1,
        unit="шт"
        # Аргумент is_restricted не передаем, должен сработать дефолт из конструктора
    )
    assert item.is_restricted is False


def test_subclass_must_implement_abstract_methods():
    """Проверка жесткого контракта: если подкласс не реализует get_full_spec, он тоже будет абстрактным."""
    # Создаем заведомо сломанный класс, забыв написать метод get_full_spec
    class BrokenItem(AbstractControlledItem):
        pass

    # Проверяем, что Python запретит создать объект такого подкласса
    with pytest.raises(TypeError) as exc_info:
        BrokenItem(item_id="2", name="Ошибка", danger_level=1, unit="шт")
        
    assert "get_full_spec" in str(exc_info.value)
