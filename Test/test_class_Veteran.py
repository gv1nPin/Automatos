import pytest
from Main.enums import VeteranRole, BenefitLevel
from Main.class_Veteran import Veteran 

# Сводные дефолтные данные для тестов
TEST_ID = "U-999"
TEST_CL = 3

# =========================================================================
# 1. ТЕСТЫ ДЛЯ МЕТОДА get_benefit_level
# =========================================================================

def test_benefit_level_federal():
    """Проверка, что ветераны и инвалиды БД получают федеральный бюджет."""
    v1 = Veteran(TEST_ID, "Тест 1", TEST_CL, role=VeteranRole.COMBAT_VETERAN)
    v2 = Veteran(TEST_ID, "Тест 2", TEST_CL, role=VeteranRole.DISABLED_VETERAN)
    assert v1.get_benefit_level() == BenefitLevel.FEDERAL
    assert v2.get_benefit_level() == BenefitLevel.FEDERAL

def test_benefit_level_regional():
    """Проверка, что ветераны военной службы получают региональный бюджет."""
    v = Veteran(TEST_ID, "Тест 3", TEST_CL, role=VeteranRole.MILITARY_SERVICE_VETERAN)
    assert v.get_benefit_level() == BenefitLevel.REGIONAL

def test_benefit_level_none():
    """Проверка, что гражданские пациенты идут без льгот."""
    v = Veteran(TEST_ID, "Тест 4", TEST_CL, role=VeteranRole.NON_VETERAN)
    assert v.get_benefit_level() == BenefitLevel.NONE


# =========================================================================
# 2. ТЕСТЫ ДЛЯ МЕТОДА get_max_daily_allowed
# =========================================================================

@pytest.mark.parametrize("role_enum", list(VeteranRole))
def test_low_danger_level_allowance(role_enum):
    """Проверка, что для ЛЮБОЙ роли при низком danger_level (<=2) лимит равен 30."""
    v = Veteran(TEST_ID, "Тест лимита", TEST_CL, role=role_enum)
    assert v.get_max_daily_allowed(danger_level=1) == 30
    assert v.get_max_daily_allowed(danger_level=2) == 30

@pytest.mark.parametrize("danger_level", [3, 4, 5])  # ИСПРАВЛЕНО: добавлены значения [3, 4, 5]
def test_high_danger_level_allowance_disabled_veteran(danger_level):
    """Проверка лимита (10 шт) для инвалидов БД на строгие препараты."""
    v = Veteran(TEST_ID, "Игорь", TEST_CL, role=VeteranRole.DISABLED_VETERAN)
    assert v.get_max_daily_allowed(danger_level) == 10

@pytest.mark.parametrize("danger_level", [3, 4, 5])  # ИСПРАВЛЕНО: добавлены значения [3, 4, 5]
def test_high_danger_level_allowance_combat_veteran(danger_level):
    """Проверка лимита (5 шт) для ветеранов БД на строгие препараты."""
    v = Veteran(TEST_ID, "Олег", TEST_CL, role=VeteranRole.COMBAT_VETERAN)
    assert v.get_max_daily_allowed(danger_level) == 5

@pytest.mark.parametrize("role_enum", [VeteranRole.MILITARY_SERVICE_VETERAN, VeteranRole.NON_VETERAN])
@pytest.mark.parametrize("danger_level", [3, 4, 5])  # ИСПРАВЛЕНО: добавлены значения [3, 4, 5]
def test_high_danger_level_allowance_others(role_enum, danger_level):
    """Проверка базового лимита (2 шт) для остальных на строгие препараты."""
    v = Veteran(TEST_ID, "Пациент", TEST_CL, role=role_enum)
    assert v.get_max_daily_allowed(danger_level) == 2


# =========================================================================
# 3. ТЕСТЫ ДЛЯ МЕТОДА requires_additional_doc
# =========================================================================

def test_docs_for_combat_and_disabled_veterans():
    """Проверка пакета документов для федеральных льготников (4 документа)."""
    for role_enum in (VeteranRole.COMBAT_VETERAN, VeteranRole.DISABLED_VETERAN):
        v = Veteran(TEST_ID, "Ветеран боевых", TEST_CL, role=role_enum)
        docs = v.requires_additional_doc()
        assert len(docs) == 4
        assert "Паспорт РФ" in docs
        assert "Удостоверение ветерана боевых действий (УВБД)" in docs
        assert "СНИЛС" in docs

def test_docs_for_military_service_veteran():
    """Проверка пакета документов для ветеранов военной службы (3 документа)."""
    v = Veteran(TEST_ID, "Ветеран ВС", TEST_CL, role=VeteranRole.MILITARY_SERVICE_VETERAN)
    docs = v.requires_additional_doc()
    assert len(docs) == 3  
    assert "Паспорт РФ" in docs
    assert "Удостоверение ветерана военной службы (УВСС)" in docs

def test_docs_for_non_veteran():
    """Проверка пакета документов для гражданских (2 документа)."""
    v = Veteran(TEST_ID, "Гражданский", TEST_CL, role=VeteranRole.NON_VETERAN)
    docs = v.requires_additional_doc()
    assert len(docs) == 2
    assert "Паспорт РФ" in docs
