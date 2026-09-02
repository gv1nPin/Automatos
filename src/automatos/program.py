import sys
from .User.AbstractUser import AbstractUser
from .Item.AbstractControlledItem import AbstractControlledItem
from .User.RobotStaff import RobotStaff
from .User.Veteran import Veteran
from .Item.MedicalItem import MedicalItem
from .utils.AuditLog import AuditLog
from .utils.DistributionManager import DistributionManager
from .utils.Enums import VeteranRole
from .Inventory.AbstractInventory import AbstractInventory

# === ГЛАВНЫЙ СКРИПТ ЗАПУСКА (ИНТЕРФЕЙС) ===
def main():
    # 1. Инициализируем сервисы
    audit_log = AuditLog()  # Синглтон журнал
    inventory = AbstractInventory()
    manager = DistributionManager(inventory_service=inventory, auditlog=audit_log)

    # 2. Создаем тестовые объекты
    # Робот-раздатчик (clearance_level = 5, может выдавать всё)
    robot = RobotStaff(user_id="R-24", name="Валли-01", clearance_level=5, model_version="v2.1")
    
    # Пациенты-ветераны
    combat_veteran = Veteran(user_id="V-111", name="Иванов Иван Петрович", clearance_level=3, role=VeteranRole.COMBAT_VETERAN)
    non_veteran = Veteran(user_id="V-000", name="Петров Сидор", clearance_level=1, role=VeteranRole.NON_VETERAN)

    # Лекарства
    aspirin = MedicalItem(item_id="MED-001", name="Аспирин", danger_level=1, unit="шт", dosage="500мг", form="Таблетки")
    morphine = MedicalItem(item_id="MED-999", name="Морфин Сульфат", danger_level=4, unit="ампула", dosage="10мг/мл", form="Ампулы", is_restricted=True)

    print("=" * 60)
    print(" СИСТЕМА УПРАВЛЕНИЯ ВЫДАЧЕЙ ПРЕПАРАТОВ ЗАПУЩЕНА")
    print("=" * 60)

    while True:
        print("\n--- Доступные операции (Мордочка) ---")
        print("1. Успешная выдача (Аспирин боевому ветерану, 5 шт)")
        print("2. Проверка накопительного лимита (Попытка взять Морфин частями: 4 шт, затем еще 3 шт)")
        print("3. Проверка блокировки по роли (Попытка выдать Морфин НЕ ветерану)")
        print("4. Симуляция механического сбоя робота (Робот ломается при выдаче)")
        print("5. Показать текущую историю AuditLog")
        print("6. Выйти из программы")
        
        choice = input("\nВыберите номер действия: ").strip()

        if choice == "1":
            print("\n Сценарий 1: Выдача Аспирина (Уровень опасности: 1)...")
            success = manager.process_distribution_request(
                operator=robot, recipient=combat_veteran, item=aspirin, quantity=5
            )
            print(f"Результат операции: {'УСПЕХ' if success else 'ОТКАЗ'}")

        elif choice == "2":
            print("\n Сценарий 2: Тест суточного накопительного лимита (Лимит Ветерана на Морфин = 5 шт)...")
            print("--- Шаг A: Просим 4 ампулы Морфина (Разрешено, так как 4 <= 5) ---")
            step_1 = manager.process_distribution_request(
                operator=robot, recipient=combat_veteran, item=morphine, quantity=4
            )
            print(f"Шаг А выполнен: {'УСПЕХ' if step_1 else 'ОТКАЗ'}")

            print("\n--- Шаг Б: Тот же ветеран просит ЕЩЕ 3 ампулы в тот же день (Итого будет 7. Должно заблокировать!) ---")
            step_2 = manager.process_distribution_request(
                operator=robot, recipient=combat_veteran, item=morphine, quantity=3
            )
            print(f"Шаг Б выполнен: {'УСПЕХ' if step_2 else 'ОТКАЗ'}")

        elif choice == "3":
            print("\n Сценарий 3: Проверка жестких ограничений роли...")
            print(f"Пациент: {non_veteran.name} (Роль: {non_veteran.get_role_name()}) хочет получить Морфин.")
            success = manager.process_distribution_request(
                operator=robot, recipient=non_veteran, item=morphine, quantity=1
            )
            print(f"Результат операции: {'УСПЕХ' if success else 'ОТКАЗ'}")

        elif choice == "4":
            print("\n Сценарий 4: Механическая поломка робота...")
            print("Специально заставляем метод dispense робота вернуть False...")
            
            # Временно ломаем метод dispense у нашего робота для этого теста
            original_dispense = robot.dispense
            robot.dispense = lambda item_id, qty, rec_name: False 

            success = manager.process_distribution_request(
                operator=robot, recipient=combat_veteran, item=aspirin, quantity=2
            )
            print(f"Результат операции: {'УСПЕХ' if success else 'ОТКАЗ'}")
            print(f"Статус робота после сбоя: is_mechanical_ok = {robot.is_mechanical_ok}, Причина: {robot.maintenance_reason}")
            
            # Чиним робота обратно для других тестов
            robot.is_mechanical_ok = True
            robot.maintenance_reason = None
            robot.dispense = original_dispense

        elif choice == "5":
            print("\n --- ИСТОРИЯ ОПЕРАЦИЙ (ЗАПИСИ ИЗ AUDIT LOG) ---")
            if not audit_log.records:
                print("Журнал пуст.")
            else:
                for idx, record in enumerate(audit_log.records, 1):
                    print(f"[{idx}] {record['timestamp'][:19]} | Статус: {record['status']} | "
                          f"Предмет: {record['item_name']} (x{record['qty']}) | "
                          f"Детали: {record['details']}")

        elif choice == "6":
            print("\nВыход из программы. Всего доброго!")
            sys.exit(0)
        else:
            print("\n Неверный ввод! Пожалуйста, выберите число от 1 до 6.")


if __name__ == "__main__":
    main()
