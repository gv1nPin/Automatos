from .class_AbstractControlledItem import AbstractControlledItem

class MedicalItem(AbstractControlledItem):
    """ Производный класс для медицинских препаратов (лекарств).

    Args:
        AbstractControlledItem (_type_): _description_
    """
    def __init__(self, item_id: str, name: str, danger_level: int, unit: str, is_restricted: bool = False):
        super().__init__(item_id, name, danger_level, unit, is_restricted)

        self.batch_or_lot = "Лот-001" # Дефолтное свойство партии для интеграции с инвентарем и AuditLog

    def get_full_spec(self) -> str:
        restricted_status = "ТРЕБУЕТСЯ ОСОБЫЙ КОНТРОЛЬ" if self.is_restricted else "Стандартный контроль"
        return f" {self.name} [{self.form}, {self.dosage}] | ID: {self.item_id} | Опасность: {self.danger_level} | Ед.изм: {self.unit} | Статус: {restricted_status}"
