import pytest
from src.class_AbstractUser import AbstractUser 

# 1. Создаем заглушку дочернего класса, чтобы протестировать логику базового класса User
class MockUser(AbstractUser):
    def get_max_daily_allowed(self, danger_level: int) -> int:
        return 30

    def get_role_name(self) -> str:
        return "Тестовый пользователь"

    # ДОБАВЛЕНО: удовлетворяем новый контракт абстрактного класса AbstractUser
    def requires_additional_doc(self) -> list[str]:
        """Заглушка метода контроля документов для успешной сборки абстракции."""
        return []


# Все остальные тесты ниже оставляем БЕЗ ИЗМЕНЕНИЙ
@pytest.fixture
def active_user():
    return MockUser(user_id="U-001", name="Иван Иванов", clearance_level=3)


# =========================================================================
# ТЕСТЫ БЛОКА КОНТРОЛЯ СОСТОЯНИЯ
# =========================================================================

def test_initial_user_state(active_user):
    """Проверка начального (здорового) состояния пользователя."""
    assert active_user.is_active is True
    assert active_user.is_blocked is False
    assert active_user.block_reason is None


def test_block_user_changes_all_statuses(active_user):
    """Проверка синхронного изменения статусов при блокировке."""
    reason_text = "Нарушение правил безопасности"
    
    active_user.block_user(reason=reason_text)
    
    assert active_user.is_active is False
    assert active_user.is_blocked is True
    assert active_user.block_reason == reason_text


def test_unblock_user_clears_reason(active_user):
    """Проверка, что разблокировка возвращает исходный статус и зачищает причину в None."""
    # Сначала блокируем
    active_user.block_user("Временный бан")
    
    # Затем разблокируем
    active_user.unblock_user()
    
    assert active_user.is_active is True
    assert active_user.is_blocked is False
    assert active_user.block_reason is None  # Блок самопроверки успешно зачистил данные


@pytest.mark.parametrize("reason", [
    "Подозрительная активность",
    "Увольнение сотрудника",
    "Технические работы"
])
def test_multiple_block_reasons(active_user, reason):
    """Параметризованный тест для проверки разных текстовых причин блокировки."""
    active_user.block_user(reason)
    assert active_user.block_reason == reason
