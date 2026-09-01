from class_AbstractUser import AbstractUser

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

        if quantity <=0:
            self.auditlog_err(operator.user_id)
            return False

        if not recipient.is_active:
            # тут проверка на блокировку юзера, получателя
            return self.reject_transaction(recipient, f"{recipient.name} причина {reason}")
        
        max_daily_allowed = recipient.get_max_daily_allowed(item.danger_level)
        if quantity > max_daily_allowed:
            return self.reject_transaction(operator, recipient, item, quantity)

        if not operator.is_active:
            # reason - он должен как-то получать причину из логов, от AudtitLog
            return self.reject_transaction(operator, f"{operator.name} не работает по причине {reason}")

        if operator.clearance_level < item.danger_level:
            # reason - причина из логов в отказе, 
            # по идее у оператора тоже должен быть допуск на выдачу опасных лекарств
            return self.reject_transaction(operator, reason)

        