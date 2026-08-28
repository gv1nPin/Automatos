from enum import Enum

class BenefitLevel(Enum):
    """Справочник уровней финансирования для льгот

    Args:
        Enum (_type_): уровень льгот
    """
    FEDERAL = "Федеральный бюджет"
    REGIONAL = "Региональный бюджет"
    NONE = "Без льгот"

class VeteranRole(Enum):
    """Класс-справочник для категорий ветеранов(Enum)

    Args:
        Enum (_type_): список ролей
    """
    # категории ролей
    COMBAT_VETERAN = "Ветеран боевых действий"
    # Участник боевых действий(федеральные льготы)
    DISABLED_VETERAN = "Инвалид боевых действий"
    # Инвалидность в следствие травмы/контузии ранения(федеральные льготы)
    MILITARY_SERVICE_VETERAN = "Ветеран военной службы"
    # Стаж службы более 20 лет(региональные льготы)
    
    NON_VETERAN = "Гражданский пациент"

    def get_benefit_level(self) ->BenefitLevel:
        """Проверка 

        Returns:
            bool: проверка *уровня* роли
        """
        if self in (VeteranRole.COMBAT_VETERAN, VeteranRole.DISABLED_VETERAN):
            return BenefitLevel.FEDERAL
        if self == VeteranRole.MILITARY_SERVICE_VETERAN:
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
        if self == VeteranRole.DISABLED_VETERAN:
            return 10 # DISABLED_VETERAN допуск по строгим препаратам 10
        if self == VeteranRole.COMBAT_VETERAN:
            return 5 # COMBAT_VETERAN допуск по строгим препаратам 5
        else:
            return 2
        # Цикл перебора доступного лимита по подотчетным препаратам, цифры из головы не из доков

    def requires_additional_doc(self) ->list:
        """Контроль доп документов

        Returns:
            list: Список документов необходимый для выдачи лекарств
        """
        documents = ["Медицинский рецепт Для наркотических и психотропных веществ это форма № 107-1/у-НП, для сильнодействующих и комбинированных препаратов — форма № 148-1/у-88"]

        if self in (VeteranRole.COMBAT_VETERAN, VeteranRole.DISABLED_VETERAN):
            documents.append("Паспорт РФ")
            documents.append("Удостоверение ветерана боевых действий (УВБД)")
            documents.append("СНИЛС")

        elif self == VeteranRole.MILITARY_SERVICE_VETERAN:
            documents.append("Паспорт РФ")
            documents.append("Удостоверение ветерана боевых действий (УВБД)")
        else: # Блок для не ветерана
            documents.append("Паспорт РФ")

        return documents
