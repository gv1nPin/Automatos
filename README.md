# Automatos
```text
src/
└── automatos/
    ├── Inventory/
    │   ├── AbstractInventory.py       # Абстрактная логика склада и сверки
    │   └── MedicalInventory.py        # Реализация адаптера под DistributionManager
    ├── Item/
    │   ├── AbstractControlledItem.py  # Спецификация контролируемого объекта
    │   ├── MedicalItem.py             # Производный класс медицинского препарата
    │   └── Stock.py                   # Модель физической ячейки / партии товара
    ├── User/
    │   ├── AbstractUser.py            # Базовые параметры субъекта безопасности
    │   ├── RobotStaff.py              # Логика роботизированного раздатчика
    │   └── Veteran.py                 # Логика расчета лимитов и доп. документов
    ├── utils/
    │   └── Enums.py                   # Хранение перечислений (VeteranRole, BenefitLevel)
    ├── AuditLog.py                    # Потокобезопасный центральный журнал операций
    └── DistributionManager.py         # Менеджер бизнес-логики распределения ресурсов
```