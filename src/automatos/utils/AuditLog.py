import datetime
import json
from typing import Optional, List, Dict, Any

class AuditLog:
    _instance: Optional['AuditLog'] = None #

    def __new__(cls, *args, **kwargs):
        # Гарантирует, что в системе будет существовать только один общий журнал.
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.records = []  # Список для хранения словарей-транзакций
        return cls._instance

    def log_transaction(self, operator: Any, recipient: Any, item: Any, quantity: int, status: str, details: str = "") -> None:
        # Основной метод записи. Принимает объекты классов, 
        # забирает у них нужные свойства и сохраняет в список records.
        item_id = getattr(item, "item_id", "UNKNOWN") if item else "UNKNOWN"
        item_name = getattr(item, "name", "UNKNOWN") if item else "UNKNOWN"
        batch_or_lot = getattr(item, "batch_or_lot", "NOT_SPECIFIED") if item else "NOT_SPECIFIED"

        transaction_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            
            # Данные выдающего (Робот или Сотрудник)
            "operator_card": getattr(operator, "user_id", "UNKNOWN") if operator else "SYSTEM",
            "operator_name": getattr(operator, "name", "SYSTEM") if operator else "SYSTEM",
            "operator_role": operator.get_role_name() if operator and hasattr(operator, "get_role_name") else "SYSTEM",
            
            # Данные получателя (Ветеран)
            "recipient_card": getattr(recipient, "user_id", "UNKNOWN") if recipient else "SYSTEM",
            "recipient_name": getattr(recipient, "name", "SYSTEM") if recipient else "SYSTEM",
            "recipient_role": recipient.get_role_name() if recipient and hasattr(recipient, "get_role_name") else "SYSTEM",
            
            # Данные предмета и операции
            "item_id": item_id,
            "item_name": item_name,
            "batch_or_lot": batch_or_lot,
            "qty": quantity,
            "status": status,  # SUCCESS, REJECTED, SYSTEM_ERROR
            "details": details
        }
        
        self.records.append(transaction_record)
        print(f" [AuditLog - {status}]: {item_name} (x{quantity}) | Выдал: {transaction_record['operator_name']} | Получил: {transaction_record['recipient_name']}")

    def log_success(self, operator_id: str, recipient_id: str, item_id: str, quantity: int) -> None:
        class MockObj:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)
            def get_role_name(self):
                return getattr(self, "role_name", "UNKNOWN")

        op = MockObj(user_id=operator_id, name=f"Робот_{operator_id}", role_name="Автомат-Выдаватель")
        rec = MockObj(user_id=recipient_id, name=f"Пациент_{recipient_id}", role_name="Ветеран")
        it = MockObj(item_id=item_id, name=f"Препарат_{item_id}", batch_or_lot="Лот-001")
        
        self.log_transaction(operator=op, recipient=rec, item=it, quantity=quantity, status="SUCCESS", details="Выдано успешно")

    def log_failure(self, operator_id: str, recipient_id: str, item_id: str, quantity: int, reason: str) -> None:
        class MockObj:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)
            def get_role_name(self):
                return getattr(self, "role_name", "UNKNOWN")

        op = MockObj(user_id=operator_id, name=f"Робот_{operator_id}", role_name="Автомат-Выдаватель")
        rec = MockObj(user_id=recipient_id, name=f"Пациент_{recipient_id}", role_name="Ветеран")
        it = MockObj(item_id=item_id, name=f"Препарат_{item_id}", batch_or_lot="Лот-001")
        
        self.log_transaction(operator=op, recipient=rec, item=it, quantity=quantity, status="REJECTED", details=reason)

    def log_system_error(self, user_id: str, error_msg: str) -> None:
        class MockObj:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        op = MockObj(user_id=user_id, name=f"Робот_{user_id}")
        self.log_transaction(operator=op, recipient=None, item=None, quantity=0, status="SYSTEM_ERROR", details=error_msg)

    def get_recipient_total_received(self, card_id: str, item_id: str, time_window_hours: int = 24) -> int:
        total = 0
        now = datetime.datetime.now()
        cutoff_time = now - datetime.timedelta(hours=time_window_hours)

        for r in self.records:
            if r["status"] == "SUCCESS" and r["recipient_card"] == card_id and r["item_id"] == item_id:
                record_time = datetime.datetime.fromisoformat(r["timestamp"])
                if record_time >= cutoff_time:
                    total += r["qty"]
        return total

    def get_all_records_by_item(self, item_id: str) -> List[Dict[str, Any]]:
        filtered_records = []
        for r in self.records:
            if r["item_id"] == item_id:
                filtered_records.append(r)
        return filtered_records

    def export_to_file(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.records, f, ensure_ascii=False, indent=4)
        print(f" [AuditLog] Данные экспортированы в: {file_path}")
        
    def load_from_file(self, file_path: str) -> None:
        """ДОБАВЛЕНО: загружает ранее сохраненные логи с диска в память."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.records = json.load(f)
            print(f" [AuditLog] Журнал успешно восстановлен из файла: {file_path}")
        except FileNotFoundError:
            print(f" [AuditLog] Файл {file_path} не найден. Начинаем с чистого листа.")
