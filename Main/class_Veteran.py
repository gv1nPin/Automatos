from enums import VeteranRole, BenefitLevel
from class_User import User

class Veteran(User):
    def __init__(self,user_id, name: str, role: VeteranRole, clearance_level: int):
        super().__init__(user_id, name, clearance_level)
        self.role = role

    def get_role_name(self) -> str:
        return self.role.value

    def get_benefit_level(self) ->BenefitLevel:
        """Проверка 

        Returns:
            bool: проверка *уровня* роли
        """
        if self.role in (VeteranRole.COMBAT_VETERAN, VeteranRole.DISABLED_VETERAN):
            return BenefitLevel.FEDERAL
        if self.role == VeteranRole.MILITARY_SERVICE_VETERAN:
            return BenefitLevel.REGIONAL
        return BenefitLevel.NONE

    def get_max_daily_allowed(self, danger_level: int) ->int:
        """Возвращает суточное значение лимита выданнанного препарата(unit предмета)

        Args:
            danger_level (int): уровень допуска по препарату, 1-2 низкий, 3-5 строгий

        Returns:
            int: Количество лимита
        """

        if danger_level <= 2:
            return 30 # если уровень контроля по препарату низкий, можно купить 30 штук за раз
        if self.role == VeteranRole.DISABLED_VETERAN:
            return 10 # DISABLED_VETERAN допуск по строгим препаратам 10
        if self.role == VeteranRole.COMBAT_VETERAN:
            return 5 # COMBAT_VETERAN допуск по строгим препаратам 5
        else:
            return 2
        # Цикл перебора доступного лимита по подотчетным препаратам, цифры из головы не из доков

    def requires_additional_doc(self) ->list[str]:
        """Контроль доп документов

        Returns:
            list: Список документов необходимый для выдачи лекарств
        """
        documents = ["Медицинский рецепт Для наркотических и психотропных веществ это форма № 107-1/у-НП, для сильнодействующих и комбинированных препаратов — форма № 148-1/у-88"]
        documents.append("Паспорт РФ")

        if self.role in (VeteranRole.COMBAT_VETERAN, VeteranRole.DISABLED_VETERAN):
            documents.append("Удостоверение ветерана боевых действий (УВБД)")
            documents.append("СНИЛС")

        elif self.role == VeteranRole.MILITARY_SERVICE_VETERAN:
            documents.append("Удостоверение ветерана военной службы (УВСС)")

        return documents
