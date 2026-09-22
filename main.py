"""Консольный интерфейс приложения для работы с банковскими операциями."""

from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from src.fields import get_field_value, load_fields
from src.processing import (
    Transaction,
    filter_by_currency_code,
    filter_by_state,
    process_bank_operations,
    process_bank_search,
    sort_by_date,
)
from src.readers import get_transactions_from_csv, get_transactions_from_xls
from src.utils import get_transactions_from_json
from src.widget import get_date, mask_account_card

JSON_PATH = Path("data/operations.json")
CSV_PATH = Path("data/transactions.csv")
XLSX_PATH = Path("data/transactions_excel.xlsx")
FIELD_ALIASES_PATH = Path("config/field_aliases.json")

AVAILABLE_STATUSES = {"EXECUTED", "CANCELED", "PENDING"}
YES_ANSWERS = {"ДА", "YES"}
NO_ANSWERS = {"НЕТ", "NO"}

WELCOME_MESSAGE = """Привет! Добро пожаловать в программу работы с банковскими транзакциями.
Выберите необходимый пункт меню:
1. Получить информацию о транзакциях из JSON-файла
2. Получить информацию о транзакциях из CSV-файла
3. Получить информацию о транзакциях из XLSX-файла"""

STATUS_MESSAGE = """Введите статус, по которому необходимо выполнить фильтрацию.
Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING"""


def _select_data_source() -> list[Transaction]:
    """Запросить формат исходного файла и загрузить операции."""
    while True:
        print(WELCOME_MESSAGE)
        menu_item = input().strip()
        print(f"Пользователь: {menu_item}")

        if menu_item == "1":
            print("Для обработки выбран JSON-файл.")
            return get_transactions_from_json(JSON_PATH)
        if menu_item == "2":
            print("Для обработки выбран CSV-файл.")
            return get_transactions_from_csv(CSV_PATH)
        if menu_item == "3":
            print("Для обработки выбран XLSX-файл.")
            return get_transactions_from_xls(XLSX_PATH)

        print("Не верный пункт меню! Повторите выбор.")


def _select_status() -> str:
    """Запросить один из доступных статусов операции."""
    while True:
        print(STATUS_MESSAGE)
        status = input().strip().upper()
        print(f"Пользователь: {status}")

        if status in AVAILABLE_STATUSES:
            return status

        print(f"Статус операции {status} недоступен.")


def _ask_yes_no(question: str) -> bool:
    """Получить от пользователя ответ «да» или «нет»."""
    while True:
        print(question)
        answer = input().strip().upper()

        if answer in YES_ANSWERS:
            print("Пользователь: ДА")
            return True
        if answer in NO_ANSWERS:
            print("Пользователь: НЕТ")
            return False

        print(f"Пользователь: {answer}")
        print(f"{answer} недоступно.")


def _select_sort_direction() -> bool:
    """Вернуть направление сортировки для параметра ``descending``."""
    while True:
        print("Отсортировать по возрастанию или по убыванию? по возрастанию/по убыванию")
        answer = "".join(input().split()).upper()

        if answer == "ПОВОЗРАСТАНИЮ":
            print("Пользователь: ПО ВОЗРАСТАНИЮ")
            return False
        if answer == "ПОУБЫВАНИЮ":
            print("Пользователь: ПО УБЫВАНИЮ")
            return True

        print(f"Пользователь: {answer}")
        print(f"{answer} недоступно.")


def _as_text(value: Any) -> str:
    """Преобразовать значение поля транзакции в строку для вывода."""
    if value is None or isinstance(value, list) and not value:
        return ""
    return str(value)


def _mask_requisites(value: str) -> str:
    """Замаскировать реквизиты, сохранив некорректное значение как есть."""
    if not value:
        return ""

    try:
        return mask_account_card(value)
    except ValueError:
        return value


def _format_transaction(
    transaction: Transaction,
    field_aliases: Mapping[str, list[str]],
) -> dict[str, str]:
    """Подготовить три строки с информацией о банковской операции."""
    raw_date = _as_text(get_field_value(transaction, "date", field_aliases))
    description = _as_text(get_field_value(transaction, "description", field_aliases))

    try:
        formatted_date = get_date(raw_date)
    except ValueError:
        formatted_date = raw_date

    source = _mask_requisites(_as_text(get_field_value(transaction, "from", field_aliases)))
    destination = _mask_requisites(_as_text(get_field_value(transaction, "to", field_aliases)))
    route = f"{source} -> {destination}" if source else destination

    amount = _as_text(get_field_value(transaction, "amount", field_aliases))
    currency_code = _as_text(get_field_value(transaction, "currency_code", field_aliases))
    currency_name = _as_text(get_field_value(transaction, "currency_name", field_aliases))

    return {
        "operation": f"{formatted_date} {description}".strip(),
        "route": route,
        "amount": f"{amount} {currency_code} ({currency_name})".strip(),
    }


def _print_transactions(transactions: list[Transaction]) -> None:
    """Сформировать и вывести итоговый список операций."""
    raw_aliases = load_fields(FIELD_ALIASES_PATH)
    if not isinstance(raw_aliases, Mapping):
        print("Программа: Не удалось загрузить справочник полей транзакций")
        return

    field_aliases = cast(Mapping[str, list[str]], raw_aliases)
    formatted_transactions = [_format_transaction(transaction, field_aliases) for transaction in transactions]

    print("Распечатываю итоговый список транзакций...")
    print(f"Программа: Всего банковских операций в выборке: {len(formatted_transactions)}")

    for transaction in formatted_transactions:
        print()
        print(transaction["operation"])
        print(transaction["route"])
        print(transaction["amount"])


def main() -> None:
    """Запустить последовательную обработку банковских операций."""
    transactions = _select_data_source()

    status = _select_status()
    transactions = filter_by_state(transactions, status)

    if _ask_yes_no("Программа: Отсортировать операции по дате? Да/Нет"):
        descending = _select_sort_direction()
        transactions = sort_by_date(transactions, descending)

    if _ask_yes_no("Программа: Выводить только рублевые транзакции? Да/Нет"):
        transactions = filter_by_currency_code(transactions)

    if _ask_yes_no("Программа: Отфильтровать список транзакций по определенному слову в описании? Да/Нет"):
        print("Введите слово, по которому необходимо отфильтровать транзакции:")
        search_string = input().strip()
        source_transactions = transactions
        transactions = process_bank_search(source_transactions, search_string)

        if transactions:
            process_bank_operations(source_transactions, [search_string])

    if not transactions:
        print("Программа: Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        return

    _print_transactions(transactions)


if __name__ == "__main__":  # pragma: no cover
    main()
