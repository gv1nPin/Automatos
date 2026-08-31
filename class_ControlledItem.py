
class Drugs:
    def __init__(self, drugs_legal_position:str, drugs_licensed_position:str, id_drugs_legal: int, id_drugs_licensed: int, licensed: bool, unit:int, level_clearance ) -> None:
        if not id_drugs_legal or not id_drugs_licensed:
            raise ValueError ("ID для всех категорий лекарств должен быть указан!")
        self.drugs_legal_position = drugs_legal_position
        self.drugs_licensed_position = drugs_licensed_position
        self.id_drugs_legal = id_drugs_legal
        self.id_drugs_licensed = id_drugs_licensed
        self.licensed = licensed
        self.unit = unit
        self.level_clearance = level_clearance
        self.history_give_drugs = []
        
    def access (self, user_clearance) -> bool:
    # допустима свободная выдача/выдача по рецепту
        return user_clearance >= self.level_clearance

    def control_line (self) -> bool:
        # контроль оборота рецептурных лекарств
        return self.level_clearance and self.licensed

    def quantity (self, unit) -> str:
        if unit <= 0:
            raise ValueError ("Лекарство отсутствует!")
