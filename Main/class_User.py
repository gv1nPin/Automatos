from abc import ABC, abstractmethod

class User(ABC):
    def __init__(self,user_id: str,  name: str, clearance_level: int, is_active: bool = True ):
        # Блок идентификации
        self.user_id = user_id
        self.name = name
        self.clearance_level = clearance_level
        # Блок контроля
        self.is_active = is_active
        self.is_blocked = False
        self.block_reason = None

    def block_user(self, reason: str):
        self.is_active = False
        self.is_blocked = True
        self.block_reason = reason

    def unblock_user(self,):
        self.is_active = True
        self.is_blocked = False
        self.block_reason = None

    @abstractmethod
    def get_max_daily_allowed(self, danger_level: int) ->int:
        pass

    @abstractmethod
    def get_role_name(self) -> str:
        pass