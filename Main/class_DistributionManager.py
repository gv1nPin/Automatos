from .class_AbstractUser import AbstractUser
from .class_AbstractControlledItem import AbstractControlledItem

class DistributionManager:
    def __init__(self, inventory_service, auditlog):
        self.inventory = inventory_service
        self.auditlog = auditlog

    def process_distribution_request(
            self, 
            operator: AbstractUser,
            recipient: AbstractUser,
            item: AbstractControlledItem,
            quantity: int
            ) -> bool:

        if quantity <= 0:
            self.auditlog.log_system_error(operator.user_id, "Количество должно быть больше 0")
            return False

        if not recipient.is_active:
            reason = getattr(recipient, "block_reason", "Причина не указана")
            return self.reject_transaction(operator, recipient, item, quantity, f"{recipient.name} заблокирован. Причина: {reason}")
        
        max_daily_allowed = recipient.get_max_daily_allowed(item.danger_level)
        if quantity > max_daily_allowed:
            reason = f"Превышен лимит. Доступно {max_daily_allowed}, запрошено {quantity}"
            return self.reject_transaction(operator, recipient, item, quantity, reason)

        if not operator.is_active:
            reason = getattr(operator, "maintenance_reason", None) or getattr(operator, "block_reason", "Причина не указана")
            return self.reject_transaction(operator, recipient, item, quantity, f"{operator.name} не работает по причине {reason}")

        if operator.clearance_level < item.danger_level:
            reason = f"Недостаточный уровень допуска оператора {operator.name} ({operator.clearance_level}) для предмета с danger_level {item.danger_level}"
            return self.reject_transaction(operator, recipient, item, quantity, reason)

        if item.danger_level >= 3:
            required_docs = recipient.requires_additional_doc()
            try:
                if not operator.verify_scanned_documents(required_docs):
                    return self.reject_transaction(operator, recipient, item, quantity, "Документы не верифицированы оператором")
            except AttributeError:
                pass

        if not self.inventory.is_in_stock(item.item_id, quantity):
            reason = f"Отсутствует {item.name} на складе"
            return self.reject_transaction(operator, recipient, item, quantity, reason)

        try:
            self.inventory.deduct_item(item.item_id, quantity)
            try:
                hardware_success = operator.dispense(item.item_id, quantity)
                if not hardware_success:
                    self.inventory.add_item(item.item_id, quantity)
                    try:
                        operator.is_mechanical_ok = False
                    except AttributeError:
                        pass
                    operator.maintenance_reason = "Сбой манипулятора при физической выдаче"
                    return self.reject_transaction(operator, recipient, item, quantity, "Механический сбой устройства выдачи")
            except AttributeError:
                pass

            self.auditlog.log_success(
                operator_id = operator.user_id,
                recipient_id = recipient.user_id,
                item_id = item.item_id,
                quantity = quantity
            )
            return True

        except Exception as database_or_network_error:
            self.auditlog.log_system_error(operator.user_id, str(database_or_network_error))
            return False

    def reject_transaction(self, 
                            operator: AbstractUser, 
                            recipient: AbstractUser, 
                            item: AbstractControlledItem, 
                            quantity: int, 
                            reason: str
                            ) -> bool:
        self.auditlog.log_failure(
            operator_id = operator.user_id,
            recipient_id = recipient.user_id,
            item_id = item.item_id,
            quantity = quantity,
            reason = reason
        )
        return False
