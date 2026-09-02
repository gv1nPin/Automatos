import pytest
import datetime
from src.automatos.utils.AuditLog import AuditLog
from src.automatos.utils.Enums import VeteranRole
class DummyUser:
    def __init__(self, user_id: str, name: str, role_name: str):
        self.user_id = user_id
        self.name = name
        self.role_name = role_name

    def get_role_name(self) -> str:
        return self.role_name

class DummyItem:
    def __init__(self, item_id: str, name: str, batch_or_lot: str):
        self.item_id = item_id
        self.name = name
        self.batch_or_lot = batch_or_lot

@pytest.fixture(autouse=True)
def clean_log():
    """Фикстура гарантирует чистоту синглтона перед каждым тестом."""
    log = AuditLog()
    log.records.clear()
    return log


# =====================================================================
# UNIT-ТЕСТЫ ДЛЯ КЛАССА AUDITLOG (ПАТТЕРНЫ, СОХРАНЕНИЕ, ФИЛЬТРАЦИЯ)
# =====================================================================

def test_audit_log_is_singleton():
    """Проверка, что повторные вызовы возвращают один и тот же объект в памяти."""
    log1 = AuditLog()
    log2 = AuditLog()
    assert log1 is log2


def test_log_transaction_parses_objects_correctly():
    """Проверка, что основной метод правильно извлекает свойства из переданных объектов."""
    log = AuditLog()
    
    operator = DummyUser(user_id="R-01", name="Робот-4", role_name="Автомат")
    recipient = DummyUser(user_id="V-77", name="Сергей Петрович", role_name="Ветеран")
    item = DummyItem(item_id="MED-55", name="Аспирин", batch_or_lot="Партия-A")

    log.log_transaction(
        operator=operator,
        recipient=recipient,
        item=item,
        quantity=3,
        status="SUCCESS",
        details="Выдано штатно"
    )

    assert len(log.records) == 1
    record = log.records[0]
    
    assert record["operator_card"] == "R-01"
    assert record["operator_name"] == "Робот-4"
    assert record["operator_role"] == "Автомат"
    assert record["recipient_card"] == "V-77"
    assert record["recipient_name"] == "Сергей Петрович"
    assert record["item_id"] == "MED-55"
    assert record["item_name"] == "Аспирин"
    assert record["batch_or_lot"] == "Партия-A"
    assert record["qty"] == 3
    assert record["status"] == "SUCCESS"
    assert record["details"] == "Выдано штатно"
    assert "timestamp" in record


def test_adapter_log_success():
    """Проверка работы метода-адаптера log_success, вызываемого менеджером."""
    log = AuditLog()
    
    log.log_success(operator_id="ROB-1", recipient_id="VET-2", item_id="ITM-3", quantity=10)
    
    assert len(log.records) == 1
    record = log.records[0]
    assert record["status"] == "SUCCESS"
    assert record["operator_card"] == "ROB-1"
    assert record["recipient_card"] == "VET-2"
    assert record["item_id"] == "ITM-3"
    assert record["qty"] == 10


def test_adapter_log_failure():
    """Проверка работы метода-адаптера log_failure с фиксацией причины отказа."""
    log = AuditLog()
    
    log.log_failure(operator_id="ROB-1", recipient_id="VET-2", item_id="ITM-3", quantity=5, reason="Превышен лимит")
    
    assert len(log.records) == 1
    record = log.records[0]
    assert record["status"] == "REJECTED"
    assert record["details"] == "Превышен лимит"


def test_adapter_log_system_error():
    """Проверка работы адаптера системных ошибок (получатель и предмет отсутствуют)."""
    log = AuditLog()
    
    log.log_system_error(user_id="ROB-1", error_msg="Падение БД")
    
    assert len(log.records) == 1
    record = log.records[0]
    assert record["status"] == "SYSTEM_ERROR"
    assert record["operator_card"] == "ROB-1"
    assert record["recipient_card"] == "SYSTEM"
    assert record["item_id"] == "UNKNOWN"
    assert record["details"] == "Падение БД"


def test_get_recipient_total_received_time_window():
    """Проверка фильтрации и подсчета количества выданного товара во временном окне."""
    log = AuditLog()
    
    # Эмулируем историческую запись: успешная выдача ветерану V-10
    log.log_success(operator_id="R-1", recipient_id="V-10", item_id="MED-01", quantity=5)
    # Эмулируем историческую запись: отклоненная выдача ветерану V-10 (не должна суммироваться)
    log.log_failure(operator_id="R-1", recipient_id="V-10", item_id="MED-01", quantity=2, reason="Отказ")
    # Эмулируем историческую запись: успешная выдача другому ветерану (не должна суммироваться)
    log.log_success(operator_id="R-1", recipient_id="V-99", item_id="MED-01", quantity=15)
    
    # Считаем количество за последние 24 часа
    total = log.get_recipient_total_received(card_id="V-10", item_id="MED-01", time_window_hours=24)
    assert total == 5


def test_get_recipient_total_received_excludes_expired_records():
    """Проверка, что записи за пределами временного окна игнорируются при подсчете."""
    log = AuditLog()
    
    log.log_success(operator_id="R-1", recipient_id="V-10", item_id="MED-01", quantity=10)
    
    # Искусственно переписываем время первой записи на 5 часов назад
    five_hours_ago = datetime.datetime.now() - datetime.timedelta(hours=5)
    log.records[0]["timestamp"] = five_hours_ago.isoformat()
    
    # Запрашиваем данные во временном окне 2 часа (запись должна отсечься)
    total_short_window = log.get_recipient_total_received(card_id="V-10", item_id="MED-01", time_window_hours=2)
    assert total_short_window == 0
    
    # Запрашиваем данные во временном окне 6 часов (запись должна войти)
    total_long_window = log.get_recipient_total_received(card_id="V-10", item_id="MED-01", time_window_hours=6)
    assert total_long_window == 10


def test_get_all_records_by_item():
    """Проверка фильтрации записей по конкретному идентификатору предмета."""
    log = AuditLog()
    
    log.log_success(operator_id="R-1", recipient_id="V-1", item_id="TARGET-ID", quantity=1)
    log.log_success(operator_id="R-1", recipient_id="V-1", item_id="OTHER-ID", quantity=2)
    log.log_success(operator_id="R-1", recipient_id="V-1", item_id="TARGET-ID", quantity=3)
    
    filtered = log.get_all_records_by_item("TARGET-ID")
    assert len(filtered) == 2
    assert filtered[0]["qty"] == 1
    assert filtered[1]["qty"] == 3


def test_export_to_file(tmp_path):
    """Проверка корректности экспорта внутренней структуры в физический JSON-файл."""
    log = AuditLog()
    log.log_success(operator_id="R-1", recipient_id="V-1", item_id="MED-1", quantity=1)
    
    # Создаем временный путь к файлу средствами pytest (tmp_path)
    file_path = tmp_path / "test_audit.json"
    
    log.export_to_file(str(file_path))
    
    # Проверяем, что файл физически создан на диске и содержит текст
    assert file_path.exists()
    file_content = file_path.read_text(encoding="utf-8")
    assert "TARGET-ID" not in file_content  # Убеждаемся в отсутствии мусора
    assert '"status": "SUCCESS"' in file_content
