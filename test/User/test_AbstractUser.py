import pytest
# Абсолютный импорт по структуре пакета src.automatos
from src.automatos.User.AbstractUser import AbstractUser 

# =========================================================================
# ВСПОМОГАТЕЛЬНЫЙ КЛАСС-НАСЛЕДНИК ДЛЯ ТЕСТИРОВАНИЯ АБСТРАКЦИИ
# =========================================================================

class MockUser(AbstractUser):
    def get_max_daily_allowed(self, danger_level: int) -> int:
        return 30

    def get_role_name(self) -> str:
        return "Тестовый пользователь"

    def requires_additional_doc(self) -> list[str]:
        """Заглушка метода контроля документов для успешной сборки абстракции."""
        return []


@pytest.fixture
def active_user():
    """Фикстура для создания чистого тестового пользователя перед каждым тестом."""
    return MockUser(user_id="U-001", name="Иван Иванов", clearance_level=3)


# =========================================================================
# ТЕСТЫ ПРАВИЛ АБСТРАКЦИИ И ИНИЦИАЛИЗАЦИИ
# =========================================================================

def test_cannot_instantiate_abstract_user_directly():
    """Проверка правила Абстракции: напрямую создать объект AbstractUser нельзя."""
    with pytest.raises(TypeError) as exc_info:
        AbstractUser(user_id="U-000", name="Абстракт", clearance_level=1)
    
    error_msg = str(exc_info.value)
    assert "abstract class" in error_msg.lower()


def test_initial_user_state(active_user):
    """Проверка начального (здорового) состояния пользователя и инкапсуляции конструктора."""
    assert active_user.user_id == "U-001"
    assert active_user.name == "Иван Иванов"
    assert active_user.clearance_level == 3
    assert active_user.is_active is True
    assert active_user.is_blocked is False
    assert active_user.block_reason is None


# =========================================================================
# ТЕСТЫ БЛОКА КОНТРОЛЯ СОСТОЯНИЯ (БИЗНЕС-ЛОГИКА СТАТУСОВ)
# =========================================================================

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
    assert active_user.block_reason is None  # Данные успешно зачищены


@pytest.mark.parametrize("reason", [
    "Подозрительная активность",
    "Увольнение сотрудника",
    "Технические работы"
])
def test_multiple_block_reasons(active_user, reason):
    """Параметризованный тест для проверки различных текстовых причин блокировки."""
    active_user.block_user(reason)
    assert active_user.block_reason == reason
