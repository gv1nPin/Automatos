from abc import ABC, abstractmethod

class AbstractControlledItem(ABC):
    """ Базовый абстрактный класс для всех контролируемых предметов в системе.
        Задает общий контракт (Инкапсуляция и Наследование).

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


class MedicalItem(AbstractControlledItem):
    """ Производный класс для медицинских препаратов (лекарств).
        Наследует все свойства базового контролируемого предмета и добавляет свои.

    Args:
        AbstractControlledItem (_type_): _description_
    """
    def __init__(self, item_id: str, name: str, danger_level: int, unit: str, is_restricted: bool = False):
        # Вызываем конструктор родительского класса через super()
        super().__init__(item_id, name, danger_level, unit, is_restricted)

        self.batch_or_lot = "Лот-001" # Дефолтное свойство партии для интеграции с инвентарем и AuditLog

    def get_full_spec(self) -> str:
        """Реализация абстрактного метода (Полиморфизм)."""
        restricted_status = "ТРЕБУЕТСЯ ОСОБЫЙ КОНТРОЛЬ" if self.is_restricted else "Стандартный контроль"
        return f"💊 {self.name} [{self.form}, {self.dosage}] | ID: {self.item_id} | Опасность: {self.danger_level} | Ед.изм: {self.unit} | Статус: {restricted_status}"
