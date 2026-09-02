from abc import ABC, abstractmethod

class AbstractControlledItem(ABC):
    """ Базовый абстрактный класс для всех контролируемых предметов в системе.

    Args:
        ABC (_type_): абстракция
    """
    def __init__(self, item_id: str, name: str, danger_level: int, unit: str, is_restricted: bool = False):
        self.item_id = item_id              # ID (str) уникальный код в системе
        self.name = name                    # name (str) наименование предмета
        self.danger_level = danger_level    # danger_level (int) уровень опасности для сопоставления с clearance_level
        self.unit = unit                    # unit (str) единица измерения (например, "шт", "ампула", "мл")
        self.is_restricted = is_restricted  # is_restricted (bool) флаг особого контроля / допподписи

    @abstractmethod
    def get_full_spec(self) -> str:
        pass
