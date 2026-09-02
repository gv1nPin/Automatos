import pytest
from src.automatos.User.RobotStaff import RobotStaff

# Сводные дефолтные данные для тестов
TEST_ID = "R-100"
TEST_NAME = "Автомат-Выдаватель"
TEST_CL = 4
TEST_MODEL = "Model-X"

# =========================================================================
# 1. ТЕСТЫ ДЛЯ КЛАССА ROBOTSTAFF (ПРАВА, СТАТУСЫ, ВЫДАЧА)
# =========================================================================

def test_robot_staff_initialization():
    """Проверка корректности инициализации всех полей робота."""
    robot = RobotStaff(TEST_ID, TEST_NAME, TEST_CL, TEST_MODEL)
    
    assert robot.user_id == TEST_ID
    assert robot.name == TEST_NAME
    assert robot.clearance_level == TEST_CL
    assert robot.model_version == TEST_MODEL
    assert robot.is_active is True
    assert robot.is_mechanical_ok is True
    assert robot.maintenance_reason is None


def test_robot_role_name_format():
    """Проверка правильности формирования строкового имени роли."""
    robot = RobotStaff(TEST_ID, TEST_NAME, TEST_CL, TEST_MODEL)
    assert robot.get_role_name() == f"Раздатчик (Модель: {TEST_MODEL})"


def test_robot_max_daily_allowed_always_zero():
    """Проверка, что лимит получения для робота всегда равен 0 при любом danger_level."""
    robot = RobotStaff(TEST_ID, TEST_NAME, TEST_CL, TEST_MODEL)
    assert robot.get_max_daily_allowed(danger_level=1) == 0
    assert robot.get_max_daily_allowed(danger_level=5) == 0


@pytest.mark.parametrize("is_active, is_mechanical, expected_result", [
    (True, True, True),    # Робот активен в системе и исправен физически
    (False, True, False),  # Робот деактивирован программно (например, заблокирован админом)
    (True, False, False),  # У робота заклинило манипулятор/механический сбой
    (False, False, False)  # Робот полностью отключен и сломан
])
def test_robot_can_operate_logic(is_active, is_mechanical, expected_result):
    """Проверка метода can_operate при различных комбинациях состояния софта и железа."""
    robot = RobotStaff(TEST_ID, TEST_NAME, TEST_CL, TEST_MODEL, is_mechanical=is_mechanical)
    robot.is_active = is_active
    assert robot.can_operate() == expected_result


def test_robot_dispense_flow():
    """Проверка метода физической выдачи в зависимости от работоспособности робота."""
    # Сценарий 1: Робот полностью исправен
    robot = RobotStaff(TEST_ID, TEST_NAME, TEST_CL, TEST_MODEL)
    assert robot.dispense(item_id="MED-01", quantity=5, recipient_name="Иван Петрович") is True

    # Сценарий 2: Робот сломался физически
    robot.is_mechanical_ok = False
    assert robot.dispense(item_id="MED-01", quantity=5, recipient_name="Иван Петрович") is False


def test_robot_verify_scanned_documents_flow():
    """Проверка метода верификации сканов документов."""
    robot = RobotStaff(TEST_ID, TEST_NAME, TEST_CL, TEST_MODEL)
    test_docs = ["Паспорт РФ", "Медицинский рецепт"]
    
    # Исправный робот одобряет прохождение проверки контракта документов
    assert robot.verify_scanned_documents(test_docs) is True

    # Заблокированный робот не может осуществлять верификацию
    robot.is_active = False
    assert robot.verify_scanned_documents(test_docs) is False
