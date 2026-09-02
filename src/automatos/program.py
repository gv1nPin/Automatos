import sys
from typing import List, NoReturn, Dict, Any

from src.automatos.utils.Enums import VeteranRole, BenefitLevel
from src.automatos.User.Veteran import Veteran
from src.automatos.User.RobotStaff import RobotStaff
from src.automatos.Item.MedicalItem import MedicalItem
from src.automatos.utils.AuditLog import AuditLog
from src.automatos.utils.DistributionManager import DistributionManager
from src.automatos.Inventory.Stock import Stock
from src.automatos.Inventory.AbstractInventory import AbstractInventory
from src.automatos.Inventory.MedicalInventory import MedicalInventory


_global_entity_registry: Dict[str, Any] = {}

original_log_transaction = AuditLog.log_transaction

def smart_log_transaction(self, operator, recipient, item, quantity, status, details=""):
    op_id = getattr(operator, "user_id", operator)
    rec_id = getattr(recipient, "user_id", recipient)
    it_id = getattr(item, "item_id", item)

    real_op = _global_entity_registry.get(op_id, operator)
    real_rec = _global_entity_registry.get(rec_id, recipient)
    real_it = _global_entity_registry.get(it_id, item)

    inventory = _global_entity_registry.get("CURRENT_INVENTORY")
    if inventory and it_id in inventory.stocks:
        cells = inventory.find_item_stock(it_id)
        if cells:
            setattr(real_it, "batch_or_lot", cells[0].batch_or_lot)

    original_log_transaction(self, real_op, real_rec, real_it, quantity, status, details)

AuditLog.log_transaction = smart_log_transaction


def print_header(title: str) -> None:
    print(f"\n{'=' * 15} {title} {'=' * 15}")


def display_scenario_result(success: bool) -> None:
    status = "ТРАНЗАКЦИЯ ОДОБРЕНА БИЗНЕС-ЛОГИКОЙ" if success else "ТРАНЗАКЦИЯ ОТКЛОНЕНА АВТОМАТИКОЙ КОНТРОЛЯ"
    print(f"Статус на панели мониторинга: [{status}]")


def run_scenario_1(manager: DistributionManager, operator: RobotStaff, recipient: Veteran, item: MedicalItem) -> None:
    print_header("Сценарий 1: Успешный отпуск легкого препарата (Аспирин)")
    print(f"Запрос: {recipient.name} ({recipient.get_role_name()}) -> 5 {item.unit}.")
    print(f"Спецификация: {item.get_full_spec()}")
    
    success = manager.process_distribution_request(
        operator=operator, recipient=recipient, item=item, quantity=5
    )
    display_scenario_result(success)


def run_scenario_2(manager: DistributionManager, operator: RobotStaff, recipient: Veteran, item: MedicalItem) -> None:
    print_header("Сценарий 2: Контроль суточного накопительного лимита")
    print(f"Пациент: {recipient.name} | Лимит на опасные вещества: {recipient.get_max_daily_allowed(item.danger_level)} {item.unit}.")
    
    print(f"\n[Шаг А]: Запрос на 4 {item.unit} (Разрешено, так как 4 <= 5):")
    step_1 = manager.process_distribution_request(operator=operator, recipient=recipient, item=item, quantity=4)
    print(f"Результат Шага А: {'УСПЕХ' if step_1 else 'ОТКАЗ'}")

    print(f"\n[Шаг Б]: Повторный запрос на 3 {item.unit} в те же 24 часа (Итого 7 > 5. Ожидается отмена):")
    step_2 = manager.process_distribution_request(operator=operator, recipient=recipient, item=item, quantity=3)
    print(f"Результат Шага Б: {'УСПЕХ' if step_2 else 'ОТКАЗ'}")
    display_scenario_result(step_2)


def run_scenario_3(manager: DistributionManager, operator: RobotStaff, recipient: Veteran, item: MedicalItem) -> None:
    print_header("Сценарий 3: Защита от выдачи наркотических средств гражданским лицам")
    print(f"Пациент: {recipient.name} ({recipient.get_role_name()}) | Лимит по коду: {recipient.get_max_daily_allowed(item.danger_level)} шт.")
    
    success = manager.process_distribution_request(operator=operator, recipient=recipient, item=item, quantity=1)
    display_scenario_result(success)


def run_scenario_4(manager: DistributionManager, operator: RobotStaff, recipient: Veteran, item: MedicalItem) -> None:
    print_header("Сценарий 4: Сбой оборудования робота (Проверка отката остатков в ячейку Stock)")
    print(f"Запрос: выдача {item.name} (х2) пациенту {recipient.name}.")
    
    original_dispense = operator.dispense
    operator.dispense = lambda item_id, qty, rec_name: False

    success = manager.process_distribution_request(operator=operator, recipient=recipient, item=item, quantity=2)
    display_scenario_result(success)
    
    print(f"Текущие параметры автомата: is_mechanical_ok = {operator.is_mechanical_ok}")
    print(f"Причина остановки линии: {operator.maintenance_reason}")
    
    operator.is_mechanical_ok = True
    operator.maintenance_reason = None
    operator.dispense = original_dispense


def run_warehouse_reconciliation(inventory: AbstractInventory, audit_log: AuditLog) -> None:
    print_header("СИСТЕМНЫЙ КОНТРОЛЬ: Инспекция и сверка остатков с AuditLog")
    
    formatted_changes = []
    for r in audit_log.records:
        if r["status"] == "SUCCESS":
            formatted_changes.append({"item_id": r["item_id"], "change": -r["qty"]})
            
    reconciliation_log = [
        {"item_id": "MED-001", "change": 200},
        {"item_id": "MED-999", "change": 10}
    ]
    reconciliation_log.extend(formatted_changes)

    is_matching = inventory.run_reconciliation(reconciliation_log)
    
    if is_matching:
        print("СТАТУС: Сверка успешна. Фактические остатки в ячейках Stock полностью соответствуют журналу.")
    else:
        print("СТАТУС: Критическая ошибка. Обнаружено расхождение между физическим балансом ячеек и AuditLog!")


def run_cross_verification(patients: List[Veteran], inventory: AbstractInventory, items: List[MedicalItem]) -> None:
    print_header("МАТРИЦА СОВМЕСТИМОСТИ ДОМЕННЫХ ДАННЫХ")
    
    print("\n[Адресное состояние зон хранения (Ячейки Stock)]")
    print(f"{'Препарат':<16} | {'Адрес ячейки':<12} | {'Серия/Партия':<16} | {'Текущий баланс'}")
    print("-" * 65)
    for item in items:
        cells = inventory.find_item_stock(item.item_id)
        for cell in cells:
            print(f"{cell.item.name:<16} | {cell.location_code:<12} | {cell.batch_or_lot:<16} | {cell.quantity} {item.unit}.")
            
    print("\n[Профиль документов и финансирования пациентов]")
    for p in patients:
        print(f"User: {p.name:<18} | {p.get_role_name():<25} | Льготы: {p.get_benefit_level().value}")
        print(f"   Пакет документов (Danger >= 3): {', '.join(p.requires_additional_doc())}")


def show_audit_log(audit_log: AuditLog) -> None:
    print_header("Системный журнал транзакций (Audit Log)")
    if not audit_log.records:
        print("Журнал пуст.")
        return

    print(f"{'Время':<8} | {'Статус':<10} | {'Серия/Партия':<15} | {'Оператор' :<10} | {'Пациент':<16} | {'Препарат (Кол-во)'}")
    print("-" * 95)
    for r in audit_log.records:
        time_str = r["timestamp"][11:19]
        status = r["status"]
        print(f"{time_str} | {status:<10} | {r.get('batch_or_lot', 'Н/Д'):<15} | {r['operator_name']:<10} | {r['recipient_name']:<16} | {r['item_name']} (x{r['qty']})")
        if status != "SUCCESS" and r.get("details"):
            print(f"    └─ Сообщение системы контроля: {r['details']}")
    print("-" * 95)


def main() -> NoReturn:
    global _global_entity_registry
    
    audit_log = AuditLog()
    inventory = MedicalInventory(storage_id = "ЦЕНТРАЛЬНЫЙ_СКЛАД-1", is_locked = False)
    manager = DistributionManager(inventory_service = inventory, auditlog = audit_log)

    aspirin = MedicalItem(item_id = "MED-001", name = "Аспирин", danger_level = 1, unit = "шт", dosage = "500мг", form = "Таблетки")
    morphine = MedicalItem(item_id = "MED-999", name = "Морфин Сульфат", danger_level = 4, unit="амп", dosage = "10мг/мл", form="Ампулы", is_restricted=True)
    all_items = [aspirin, morphine]

    inventory.add_stock(Stock(item=aspirin, quantity=200, batch_or_lot="BAT-ASP-2026", location_code = "A-10"))
    inventory.add_stock(Stock(item=morphine, quantity=10, batch_or_lot="BAT-MOR-9999", location_code = "B-04"))

    robot = RobotStaff(user_id="R-24", name="Валли-01", clearance_level=5, model_version="v2.6_Ultimate")
    robot.is_active = True

    combat_veteran = Veteran(user_id = "V-111", name = "Иванов И. П.", clearance_level = 3, role = VeteranRole.COMBAT_VETERAN)
    disabled_veteran = Veteran(user_id = "V-222", name = "Петров О. Н.", clearance_level = 4, role = VeteranRole.DISABLED_VETERAN)
    civilian_patient = Veteran(user_id = "V-000", name = "Васин Д. А.", clearance_level = 1, role = VeteranRole.NON_VETERAN)

    for p in [combat_veteran, disabled_veteran, civilian_patient]:
        p.is_active = True

    all_patients = [combat_veteran, disabled_veteran, civilian_patient]

    _global_entity_registry = {
        robot.user_id: robot,
        combat_veteran.user_id: combat_veteran,
        disabled_veteran.user_id: disabled_veteran,
        civilian_patient.user_id: civilian_patient,
        aspirin.item_id: aspirin,
        morphine.item_id: morphine,
        "CURRENT_INVENTORY": inventory
    }

    print("=" * 70)
    print("  МОНИТОР УПРАВЛЕНИЯ РАСПРЕДЕЛЕНИЕМ МЕДИКАМЕНТОВ")
    print("=" * 70)

    while True:
        print("\n--- Интерактивное меню ---")
        print("1. Выдать нестрогий препарат (Аспирин ветерану боевых действий)")
        print("2. Проверить суточный накопительный лимит (Морфин порциями: 4 шт -> 3 шт)")
        print("3. Выдать контролируемое вещество гражданскому лицу (Лимит = 0)")
        print("4. Имитировать аппаратный сбой робота (Проверка транзакционного отката)")
        print("5. Запустить сверку остатков ячеек склада с AuditLog (Reconciliation)")
        print("6. Вывести полную матрицу соответствия льгот, доков и ячеек")
        print("7. Показать историю транзакций AuditLog")
        print("8. Завершить работу")

        choice = input("\nВыберите номер действия (1-8): ").strip()

        if choice == "1":
            run_scenario_1(manager, robot, combat_veteran, aspirin)
        elif choice == "2":
            run_scenario_2(manager, robot, combat_veteran, morphine)
        elif choice == "3":
            run_scenario_3(manager, robot, civilian_patient, morphine)
        elif choice == "4":
            run_scenario_4(manager, robot, combat_veteran, aspirin)
        elif choice == "5":
            run_warehouse_reconciliation(inventory, audit_log)
        elif choice == "6":
            run_cross_verification(all_patients, inventory, all_items)
        elif choice == "7":
            show_audit_log(audit_log)
        elif choice == "8":
            print("\nСессия закрыта. Программа завершила работу.")
            sys.exit(0)
        else:
            print("\nОшибка: Команда не распознана. Введите число от 1 до 8.")


if __name__ == "__main__":
    main()
