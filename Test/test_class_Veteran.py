import pytest
from src.Enums import VeteranRole, BenefitLevel
from src.class_Veteran import Veteran 

# Сводные дефолтные данные для тестов
TEST_ID = "U-999"
TEST_CL = 3

# =========================================================================
# 1. ТЕСТЫ ДЛЯ МЕТОДА get_benefit_level
# =========================================================================

@pytest.mark.parametrize("role, expected_benefit", [
    (VeteranRole.COMBAT_VETERAN, BenefitLevel.FEDERAL),
    (VeteranRole.DISABLED_VETERAN, BenefitLevel.FEDERAL),
    (VeteranRole.MILITARY_SERVICE_VETERAN, BenefitLevel.REGIONAL),
    (VeteranRole.NON_VETERAN, BenefitLevel.NONE)
])
def test_all_roles_benefit_levels(role, expected_benefit):
    """Сводный тест сверки: проверяет соответствие каждой роли её уровню бюджета."""
    v = Veteran(TEST_ID, "Тестовый Пациент", TEST_CL, role=role)
    assert v.get_benefit_level() == expected_benefit


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
def test_high_danger_level_allowance_military_service_veteran(danger_level):
    """Проверка лимита (2 шт) для ветеранов военной службы на строгие препараты."""
    v = Veteran(TEST_ID, "Пациент ВС", TEST_CL, role=VeteranRole.MILITARY_SERVICE_VETERAN)
    assert v.get_max_daily_allowed(danger_level) == 2

@pytest.mark.parametrize("danger_level", [3, 4, 5])
def test_high_danger_level_allowance_non_veteran(danger_level):
    """Проверка безопасности: для гражданских лиц лимит на опасные вещества равен 0."""
    v = Veteran(TEST_ID, "Гражданский Пациент", TEST_CL, role=VeteranRole.NON_VETERAN)
    assert v.get_max_daily_allowed(danger_level) == 0


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
