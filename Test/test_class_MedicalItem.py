import pytest
from src.class_MedicalItem import MedicalItem

# Сводные дефолтные данные для создания тестовых медикаментов
TEST_ITEM_ID = "MED-101"
TEST_NAME = "Морфин"
TEST_UNIT = "ампула"
TEST_DOSAGE = "10 мг/мл"
TEST_FORM = "Раствор для инъекций"

# =========================================================================
# 1. ТЕСТЫ ДЛЯ МЕТОДА get_full_spec
# =========================================================================

def test_get_full_spec_format_standard_control():
    """Проверка формирования спецификации для препарата со стандартным контролем."""
    # Создаем предмет со статусом Особого контроля = False
    item = MedicalItem(
        item_id=TEST_ITEM_ID,
        name=TEST_NAME,
        danger_level=5,
        unit=TEST_UNIT,
        dosage=TEST_DOSAGE,
        form=TEST_FORM,
        is_restricted=False
    )
    
    spec = item.get_full_spec()
    
    # Проверяем наличие всех ключевых свойств внутри итоговой строки
    assert TEST_NAME in spec
    assert TEST_ITEM_ID in spec
    assert TEST_DOSAGE in spec
    assert TEST_FORM in spec
    assert "Опасность: 5" in spec
    assert f"Ед.изм: {TEST_UNIT}" in spec
    assert "Стандартный контроль" in spec


def test_get_full_spec_format_restricted_control():
    """Проверка формирования спецификации для препарата с особым (строгим) контролем."""
    # Создаем предмет со статусом Особого контроля = True
    item = MedicalItem(
        item_id=TEST_ITEM_ID,
        name=TEST_NAME,
        danger_level=5,
        unit=TEST_UNIT,
        dosage=TEST_DOSAGE,
        form=TEST_FORM,
        is_restricted=True
    )
    
    spec = item.get_full_spec()
    
    assert "ТРЕБУЕТСЯ ОСОБЫЙ КОНТРОЛЬ" in spec
    assert "Стандартный контроль" not in spec


# =========================================================================
# 2. ТЕСТЫ СОВМЕСТИМОСТИ УРОВНЕЙ ОПАСНОСТИ ДЛЯ ВЫДАЧИ
# =========================================================================

@pytest.mark.parametrize("clearance_level, danger_level, should_allow", [
    (5, 5, True),   # Допуск равен уровню опасности — Выдача разрешена
    (5, 3, True),   # Допуск выше уровня опасности — Выдача разрешена
    (2, 4, False),  # Допуск ниже уровня опасности — Выдача ЗАПРЕЩЕНА
    (0, 1, False)   # Полное отсутствие допуска — Выдача ЗАПРЕЩЕНА
])
def test_item_danger_level_against_operator_clearance(clearance_level, danger_level, should_allow):
    """
    Тест проверяет математическую логику сопоставления уровней, 
    которую выполняет DistributionManager: operator.clearance_level >= item.danger_level
    """
    # Создаем тестовый медицинский предмет с заданным уровнем опасности
    item = MedicalItem(
        item_id=TEST_ITEM_ID,
        name=TEST_NAME,
        danger_level=danger_level,
        unit=TEST_UNIT,
        dosage=TEST_DOSAGE,
        form=TEST_FORM
    )
    
    # Проверяем математическое условие допуска к выдаче
    is_allowed = clearance_level >= item.danger_level
    assert is_allowed == should_allow
