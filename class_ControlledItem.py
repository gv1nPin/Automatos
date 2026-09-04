
class ControlledItem:
    def __init__(
        self, 
         drugs_legal_position:str, 
         drugs_licensed_position:str, 
         id_drugs_legal: int|None, 
         id_drugs_licensed: int|None, 
         licensed: bool, 
         unit:int, 
         level_clearance:int,
    ) -> None:
        if id_drugs_legal is None or id_drugs_licensed is None:
            raise ValueError ("ID для всех категорий лекарств должен быть указан!")
        self.drugs_legal_position = drugs_legal_position
        self.drugs_licensed_position = drugs_licensed_position
        self.id_drugs_legal = id_drugs_legal
        self.id_drugs_licensed = id_drugs_licensed
        self.licensed = licensed
        self.unit = unit
        self.level_clearance = level_clearance
        self.history_give_drugs: list = []
        
    def access (self, user_clearance:int) -> bool:
    # допустима свободная выдача/выдача по рецепту
        return user_clearance >= self.level_clearance

    def control_line (self) -> bool:
        # контроль оборота рецептурных лекарств
        return  self.licensed

    def quantity (self, unit) -> str:
        if unit <= 0:
            raise ValueError ("Лекарство отсутствует!")
        return f"Доступно {unit} шт."
