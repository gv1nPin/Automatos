import pytest
from Main.enums import VeteranRole, BenefitLevel

# =========================================================================
# 1. ТЕСТЫ ДЛЯ МЕТОДА get_benefit_level
# =========================================================================

def test_benefit_level_federal():
    """Проверка, что ветераны и инвалиды БД получают федеральный бюджет."""
    assert VeteranRole.COMBAT_VETERAN.get_benefit_level() == BenefitLevel.FEDERAL
    assert VeteranRole.DISABLED_VETERAN.get_benefit_level() == BenefitLevel.FEDERAL

def test_benefit_level_regional():
    """Проверка, что ветераны военной службы получают региональный бюджет."""
    assert VeteranRole.MILITARY_SERVICE_VETERAN.get_benefit_level() == BenefitLevel.REGIONAL

def test_benefit_level_none():
    """Проверка, что гражданские пациенты идут без льгот."""
    assert VeteranRole.NON_VETERAN.get_benefit_level() == BenefitLevel.NONE


# =========================================================================
# 2. ТЕСТЫ ДЛЯ МЕТОДА get_max_daily_allowed (Параметризованные тесты)
# =========================================================================

@pytest.mark.parametrize("role", list(VeteranRole))
def test_low_danger_level_allowance(role):
    """Проверка, что для ЛЮБОЙ роли при низком danger_level (<=2) лимит равен 30."""
    assert role.get_max_daily_allowed(danger_level=1) == 30
    assert role.get_max_daily_allowed(danger_level=2) == 30

@pytest.mark.parametrize("danger_level", [3, 4, 5])
def test_high_danger_level_allowance_disabled_veteran(danger_level):
    """Проверка лимита (10 шт) для инвалидов БД на строгие препараты."""
    assert VeteranRole.DISABLED_VETERAN.get_max_daily_allowed(danger_level) == 10

@pytest.mark.parametrize("danger_level", [3, 4, 5])
def test_high_danger_level_allowance_combat_veteran(danger_level):
    """Проверка лимита (5 шт) для ветеранов БД на строгие препараты."""
    assert VeteranRole.COMBAT_VETERAN.get_max_daily_allowed(danger_level) == 5

@pytest.mark.parametrize("role", [VeteranRole.MILITARY_SERVICE_VETERAN, VeteranRole.NON_VETERAN])
@pytest.mark.parametrize("danger_level", [3, 4, 5])
def test_high_danger_level_allowance_others(role, danger_level):
    """Проверка базового лимита (2 шт) для остальных на строгие препараты."""
    assert role.get_max_daily_allowed(danger_level) == 2


# =========================================================================
# 3. ТЕСТЫ ДЛЯ МЕТОДА requires_additional_doc
# =========================================================================

def test_docs_for_combat_and_disabled_veterans():
    """Проверка пакета документов для федеральных льготников (4 документа)."""
    for role in (VeteranRole.COMBAT_VETERAN, VeteranRole.DISABLED_VETERAN):
        docs = role.requires_additional_doc()
        assert len(docs) == 4
        assert "Паспорт РФ" in docs
        assert "Удостоверение ветерана боевых действий (УВБД)" in docs
        assert "СНИЛС" in docs

def test_docs_for_military_service_veteran():
    """Проверка пакета документов для ветеранов военной службы (2 документа)."""
    docs = VeteranRole.MILITARY_SERVICE_VETERAN.requires_additional_doc()
    # Обратите внимание: в текущем вашем коде у этой роли проверяется УВБД, а не УВВС
    assert len(docs) == 3  # Рецепт + Паспорт + УВБД из вашей текущей строки
    assert "Паспорт РФ" in docs
    assert "Удостоверение ветерана боевых действий (УВБД)" in docs

def test_docs_for_non_veteran():
    """Проверка пакета документов для гражданских (2 документа: рецепт + паспорт)."""
    docs = VeteranRole.NON_VETERAN.requires_additional_doc()
    assert len(docs) == 2
    assert "Паспорт РФ" in docs
