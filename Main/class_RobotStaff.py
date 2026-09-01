from .class_AbctractUser import AbstractUser

class RobotStaff(AbstractUser):
    def __init__(self, user_id: str, name: str, clearance_level: int, model_version: str, is_mechanical: bool = True):
        # Робот — это тоже пользователь системы с точки зрения авторизации и безопасности
        super().__init__(user_id, name, clearance_level)
        self.model_version = model_version
        self.is_mechanical_ok = is_mechanical

    def get_role_name(self) -> str:
        return f"Раздатчик (Модель: {self.model_version})"

    def get_max_daily_allowed(self, danger_level: int) -> int:
        return 0

    def can_operate(self) -> bool:
        # Проверка, если она равно рабочим параметрам робота
        return self.is_active and self.is_mechanical_ok

    def dispense(self, item_id: str, quantity: int, recipient_name: str) -> bool:
        """Выдача"""
        if not self.can_operate():
            return False
        return True