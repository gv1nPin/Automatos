import os
import sys
import pytest

# 1. Динамическое добавление корневой директории и папки src в sys.path.
# Это гарантирует, что pytest найдет пакеты Item, User и utils из любой папки запуска.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

# Импортируем перечисления и классы для фикстур (теперь они импортируются без ошибок)
from src.utils.Enums import VeteranRole
from src.utils.AuditLog import AuditLog
from src.utils.DistributionManager import DistributionManager
from src.User.RobotStaff import RobotStaff
from src.User.Veteran import Veteran
from src.Item.MedicalItem import MedicalItem

# ==========================================
# ФИКСТУРЫ ДЛЯ ТЕСТИРОВАНИЯ (FIXTURES)
# ==========================================

@pytest.fixture(autouse=True)
def clean_audit_log():
    """Фикстура очистки AuditLog перед каждым тестом.
    Поскольку AuditLog — это Синглтон, его записи хранятся в памяти.
    Без принудительной очистки тесты будут зависеть друг от друга!
    """
    log = AuditLog()
    log.records.clear()  # Полностью очищаем историю транзакций перед каждым тестом
    return log

@pytest.fixture
def mock_inventory():
    """Имитация склада для тестов."""
    class TestInventory:
        def __init__(self):
            self.stock = {"MED-001": 100, "MED-999": 20}
        def is_in_stock(self, item_id: str, quantity: int) -> bool:
            return self.stock.get(item_id, 0) >= quantity
        def deduct_item(self, item_id: str, quantity: int) -> None:
            self.stock[item_id] -= quantity
        def add_item(self, item_id: str, quantity: int) -> None:
            self.stock[item_id] += quantity
    return TestInventory()

@pytest.fixture
def manager(mock_inventory, clean_audit_log):
    """Инициализация DistributionManager с чистыми зависимостями."""
    return DistributionManager(inventory_service=mock_inventory, auditlog=clean_audit_log)

@pytest.fixture
def robot_operator():
    """Исправный робот-оператор с максимальным допуском."""
    return RobotStaff(user_id="R-24", name="Валли-01", clearance_level=5, model_version="v2.1")

@pytest.fixture
def combat_veteran():
    """Пациент — боевой ветеран."""
    return Veteran(user_id="V-111", name="Иванов И.П.", clearance_level=3, role=VeteranRole.COMBAT_VETERAN)

@pytest.fixture
def aspirin():
    """Обычный препарат (низкий уровень опасности)."""
    return MedicalItem(item_id="MED-001", name="Аспирин", danger_level=1, unit="шт", dosage="500мг", form="Таблетки")
