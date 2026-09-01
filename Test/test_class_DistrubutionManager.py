import pytest
from Main.class_AbstractUser import AbstractUser
from Main.class_DistributionManager import DistributionManager

# =====================================================================
# МОК-ОБЪЕКТЫ ДЛЯ ИЗОЛЯЦИИ ТЕСТИРОВАНИЯ (БЕЗ РЕАЛЬНЫХ БД)
# =====================================================================

class MockInventory:
    """Имитация сервиса склада."""
    def __init__(self, in_stock=True):
        self.in_stock_flag = in_stock
        self.deducted_items = []
        self.added_items = []

    def is_in_stock(self, item_id: str, quantity: int) -> bool:
        return self.in_stock_flag

    def deduct_item(self, item_id: str, quantity: int) -> None:
        self.deducted_items.append((item_id, quantity))

    def add_item(self, item_id: str, quantity: int) -> None:
        self.added_items.append((item_id, quantity))


class MockAuditLog:
    """Имитация синглтона логов с методами-адаптерами."""
    def __init__(self):
        self.success_logs = []
        self.failure_logs = []
        self.system_errors = []

    def log_success(self, operator_id: str, recipient_id: str, item_id: str, quantity: int):
        self.success_logs.append((operator_id, recipient_id, item_id, quantity))

    def log_failure(self, operator_id: str, recipient_id: str, item_id: str, quantity: int, reason: str):
        self.failure_logs.append((operator_id, recipient_id, item_id, quantity, reason))

    def log_system_error(self, user_id: str, error_msg: str):
        self.system_errors.append((user_id, error_msg))


# Объект-заглушка для контролируемого предмета
class DummyItem:
    def __init__(self, item_id: str, name: str, danger_level: int):
        self.item_id = item_id
        self.name = name
        self.danger_level = danger_level


# Универсальный объект-заглушка для пользователей (Ветеран/Робот)
class DummyUser:
    def __init__(self, user_id: str, name: str, clearance_level: int, is_active: bool = True, max_allowed: int = 10):
        self.user_id = user_id
        self.name = name
        self.clearance_level = clearance_level
        self.is_active = is_active
        self.max_allowed = max_allowed
        self.block_reason = "Причина блокировки тестовая"
        self.maintenance_reason = None
        self.is_mechanical_ok = True
        self.docs_verified = True
        self.dispense_success = True

    def get_max_daily_allowed(self, danger_level: int) -> int:
        return self.max_allowed

    def requires_additional_doc(self) -> list[str]:
        return ["Паспорт", "Рецепт"]

    def verify_scanned_documents(self, documents: list[str]) -> bool:
        return self.docs_verified

    def dispense(self, item_id: str, quantity: int) -> bool:
        return self.dispense_success


# =====================================================================
# ФИКСТУРЫ ТЕСТИРОВАНИЯ
# =====================================================================

@pytest.fixture
def mock_services():
    """Фикстура для инициализации лога и инвентаря."""
    inventory = MockInventory()
    auditlog = MockAuditLog()
    return inventory, auditlog


# =====================================================================
# ТЕСТ-КЕЙСЫ КЛАССА DISTRIBUTION MANAGER
# =====================================================================

def test_quantity_less_or_equal_zero(mock_services):
    """Проверка guard clause: количество выдачи меньше или равно 0."""
    inventory, auditlog = mock_services
    from Main.class_DistributionManager import DistributionManager
    manager = DistributionManager(inventory, auditlog)

    operator = DummyUser("OP-1", "Робот", 3)
    recipient = DummyUser("REC-1", "Ветеран", 1)
    item = DummyItem("MED-1", "Препарат", 2)

    result = manager.process_distribution_request(operator, recipient, item, quantity=0)

    assert result is False
    assert len(auditlog.system_errors) == 1
    assert auditlog.system_errors[0][0] == "OP-1"


def test_recipient_inactive(mock_services):
    """Проверка guard clause: получатель (Ветеран) заблокирован/неактивен."""
    inventory, auditlog = mock_services
    from Main.class_DistributionManager import DistributionManager
    manager = DistributionManager(inventory, auditlog)

    operator = DummyUser("OP-1", "Робот", 3)
    recipient = DummyUser("REC-1", "Ветеран", 1, is_active=False)
    item = DummyItem("MED-1", "Препарат", 2)

    result = manager.process_distribution_request(operator, recipient, item, quantity=5)

    assert result is False
    assert len(auditlog.failure_logs) == 1
    assert "заблокирован" in auditlog.failure_logs[0][4]


def test_quantity_exceeds_max_daily_allowed(mock_services):
    """Проверка guard clause: запрашиваемое количество превышает суточный лимит ветерана."""
    inventory, auditlog = mock_services
    from Main.class_DistributionManager import DistributionManager
    manager = DistributionManager(inventory, auditlog)

    operator = DummyUser("OP-1", "Робот", 3)
    recipient = DummyUser("REC-1", "Ветеран", 1, max_allowed=3)  # Разрешено только 3
    item = DummyItem("MED-1", "Препарат", 2)

    result = manager.process_distribution_request(operator, recipient, item, quantity=5)  # Просят 5

    assert result is False
    assert len(auditlog.failure_logs) == 1
    assert "Превышен лимит" in auditlog.failure_logs[0][4]


def test_operator_inactive(mock_services):
    """Проверка guard clause: оператор (Робот) отключен или на обслуживании."""
    inventory, auditlog = mock_services
    from Main.class_DistributionManager import DistributionManager
    manager = DistributionManager(inventory, auditlog)

    operator = DummyUser("OP-1", "Робот", 3, is_active=False)
    recipient = DummyUser("REC-1", "Ветеран", 1)
    item = DummyItem("MED-1", "Препарат", 2)

    result = manager.process_distribution_request(operator, recipient, item, quantity=2)

    assert result is False
    assert len(auditlog.failure_logs) == 1
    assert "не работает по причине" in auditlog.failure_logs[0][4]


def test_operator_insufficient_clearance(mock_services):
    """Проверка guard clause: уровень допуска оператора ниже уровня опасности предмета."""
    inventory, auditlog = mock_services
    from Main.class_DistributionManager import DistributionManager
    manager = DistributionManager(inventory, auditlog)

    operator = DummyUser("OP-1", "Робот", clearance_level=1)  # Допуск 1
    recipient = DummyUser("REC-1", "Ветеран", 1)
    item = DummyItem("MED-1", "Опасный Препарат", danger_level=3)  # Требуется 3

    result = manager.process_distribution_request(operator, recipient, item, quantity=1)

    assert result is False
    assert len(auditlog.failure_logs) == 1
    assert "Недостаточный уровень допуска" in auditlog.failure_logs[0][4]


def test_strict_item_documents_verification_failed(mock_services):
    """Проверка guard clause: строгий предмет (danger_level >= 3), документы ветерана не прошли верификацию роботом."""
    inventory, auditlog = mock_services
    from Main.class_DistributionManager import DistributionManager
    manager = DistributionManager(inventory, auditlog)

    operator = DummyUser("OP-1", "Робот", 4)
    operator.docs_verified = False  # Сканер робота заблокировал документы
    recipient = DummyUser("REC-1", "Ветеран", 1)
    item = DummyItem("MED-1", "Строгий Наркотический Препарат", danger_level=4)

    result = manager.process_distribution_request(operator, recipient, item, quantity=1)

    assert result is False
    assert len(auditlog.failure_logs) == 1
    assert "Документы не верифицированы" in auditlog.failure_logs[0][4]


def test_item_not_in_stock(mock_services):
    """Проверка guard clause: товара физически нет на складе."""
    inventory, auditlog = mock_services
    inventory.in_stock_flag = False  # Склад пуст
    
    from Main.class_DistributionManager import DistributionManager
    manager = DistributionManager(inventory, auditlog)

    operator = DummyUser("OP-1", "Робот", 3)
    recipient = DummyUser("REC-1", "Ветеран", 1)
    item = DummyItem("MED-1", "Препарат", 2)

    result = manager.process_distribution_request(operator, recipient, item, quantity=1)

    assert result is False
    assert len(auditlog.failure_logs) == 1
    assert "Отсутствует" in auditlog.failure_logs[0][4]


def test_hardware_dispense_mechanical_error_triggers_rollback(mock_services):
    """Тестирование транзакции: сбой при выдаче (dispense=False) вызывает откат (add_item) на склад."""
    inventory, auditlog = mock_services
    from Main.class_DistributionManager import DistributionManager
    manager = DistributionManager(inventory, auditlog)

    operator = DummyUser("OP-1", "Робот", 3)
    operator.dispense_success = False  # Робот заклинил в момент выдачи
    recipient = DummyUser("REC-1", "Ветеран", 1)
    item = DummyItem("MED-1", "Препарат", 2)

    result = manager.process_distribution_request(operator, recipient, item, quantity=2)

    assert result is False
    # Проверка транзакционности
    assert len(inventory.deducted_items) == 1  # Сначала списали
    assert len(inventory.added_items) == 1     # Потом вернули (Откат!)
    assert inventory.deducted_items[0] == inventory.added_items[0]
    
    # Проверка изменения аварийного статуса робота
    assert operator.is_mechanical_ok is False
    assert operator.maintenance_reason == "Сбой при физической выдаче"
    assert len(auditlog.failure_logs) == 1
    assert "Механический сбой устройства" in auditlog.failure_logs[0][4]


def test_successful_distribution_flow(mock_services):
    """Тестирование идеального сценария: все проверки пройдены, склад списал, робот выдал, лог зафиксировал успех."""
    inventory, auditlog = mock_services
    from Main.class_DistributionManager import DistributionManager
    manager = DistributionManager(inventory, auditlog)

    operator = DummyUser("OP-1", "Робот", 3)
    recipient = DummyUser("REC-1", "Иван Петрович", 1)
    item = DummyItem("MED-1", "Аспирин", 2)

