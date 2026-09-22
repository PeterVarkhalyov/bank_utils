"""Функции фильтрации, сортировки и поиска банковских операций."""

import logging
import re
from pathlib import Path
from typing import Any

from src.fields import get_field_value, load_fields

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("processing")
logger.setLevel(logging.DEBUG)
logger.propagate = False

file_handler = logging.FileHandler(
    LOG_DIR / "processing.log",
    mode="w",
    encoding="utf-8",
)
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

Transaction = dict[str, Any]

FIELD_ALIASES = load_fields("config/field_aliases.json")


def filter_by_state(transactions: list[Transaction], state: str = "EXECUTED") -> list[Transaction]:
    """Вернуть операции с указанным статусом.

    Args:
        transactions: Список словарей с данными банковских операций.
        state: Статус для фильтрации. По умолчанию ``EXECUTED``.

    Returns:
        Новый список операций, значение ключа ``state`` которых совпадает
        с запрошенным статусом. Операции без ключа ``state`` пропускаются.
    """
    logger.debug("Начало фильтрации для %s зваписей по статусу %s.", len(transactions), state)
    filtered_transactions = [
        transaction for transaction in transactions if get_field_value(transaction, "state", FIELD_ALIASES) == state
    ]
    logger.info("Получено записей %s со статусом %s.", len(filtered_transactions), state)

    return filtered_transactions


def filter_by_currency_code(
    transactions: list[Transaction],
    currency_code: str = "RUB",
) -> list[Transaction]:
    """Функция возвращает банковские операции с указанным кодом валюты.

    Код валюты извлекается из вложенного поля
    ``operationAmount.currency.code``. Операции с отсутствующей или
    некорректной структурой этого поля пропускаются.

    Args:
        transactions: Список словарей с данными банковских операций.
        currency_code: Код валюты для фильтрации. По умолчанию ``RUB``.

    Returns:
        Новый список операций с указанным кодом валюты.
    """
    logger.debug("Начата фильтрация для %s зваписей по валюте %s.", len(transactions), currency_code)
    filtered_transactions: list[Transaction] = []

    for transaction in transactions:
        if get_field_value(transaction, "currency_code", FIELD_ALIASES) == currency_code:
            filtered_transactions.append(transaction)
    logger.info("Получено записей %s для валюты %s.", len(filtered_transactions), currency_code)

    return filtered_transactions


def sort_by_date(transactions: list[Transaction], descending: bool = True) -> list[Transaction]:
    """Вернуть операции, отсортированные по дате.

    Пустые словари пропускаются. Даты ожидаются в ISO-формате,
    при котором строковая сортировка совпадает с хронологическим
    порядком.

    Args:
        transactions: Список словарей с банковскими операциями.
        descending: Сортировать по убыванию, если значение равно True.

    Returns:
        Новый список операций, отсортированный по значению ключа date.
        Пустые словари в результат не включаются.
        Если значения дат невозможно сравнить, возвращается пустой список.
    """
    logger.debug("Начата сортировка по дате для %s зваписей и направлению %s.", len(transactions), descending)
    valid_transactions = [transaction for transaction in transactions if transaction]

    try:
        sorted_transactions = sorted(
            valid_transactions,
            key=lambda transaction: get_field_value(
                transaction,
                "date",
                FIELD_ALIASES,
            ),
            reverse=descending,
        )
        logger.info("Отсортировано записей %s по направлению %s.", len(sorted_transactions), descending)
        return sorted_transactions
    except (KeyError, TypeError) as error:
        logger.error(
            "Не удалось отсортировать транзакции по дате: %s",
            error,
        )
        return []


def process_bank_search(transactions: list[Transaction], search_string: str) -> list[Transaction]:
    """Функция выбирает банковские операции по строке в описании.

    Поиск выполняется без учёта регистра. Строка поиска обрабатывается
    как обычный текст, поэтому специальные символы регулярных выражений
    не изменяют её смысл. Операции без строкового поля ``description``
    пропускаются.

    Args:
        transactions: Список банковских операций.
        search_string: Строка, которую нужно найти в описании операции.

    Returns:
        Новый список операций, описания которых содержат строку поиска.
        Для пустой строки поиска возвращается пустой список.
    """
    logger.debug(
        "Начата фильтрация транзакций по descriptions для %s записей и строкой поиска '%s'.",
        len(transactions),
        search_string,
    )
    if not search_string:
        logger.error("Фильтрация транзакций по descriptions невозможна, т.к. строка поиска не задана.")
        return []

    search_pattern = re.compile(re.escape(search_string), re.IGNORECASE)
    filtered_transactions: list[Transaction] = []
    for transaction in transactions:
        try:
            description = get_field_value(
                transaction,
                "description",
                FIELD_ALIASES,
            )
        except KeyError:
            continue

        if isinstance(description, str) and search_pattern.search(description):
            filtered_transactions.append(transaction)
    logger.info("Получено записей %s для строки поиска '%s'.", len(filtered_transactions), search_string)

    return filtered_transactions


def process_bank_operations(transactions: list[Transaction], categories: list[str]) -> dict[str, int]:
    """Функция производит расчет количества банковских операций по категориям.

    Название категории сравнивается с полем ``description`` операции.
    Категории, для которых операции не найдены, остаются в результате
    со значением ``0``.

    Args:
        transactions: Список банковских операций.
        categories: Список названий категорий операций.

    Returns:
        Словарь с количеством операций в каждой категории.
    """
    logger.debug("Начать анализ кол-ва descriptions для %s записей.", len(transactions))
    operation_counts = dict.fromkeys(categories, 0)

    for transaction in transactions:
        try:
            description = get_field_value(
                transaction,
                "description",
                FIELD_ALIASES,
            )
        except KeyError:
            continue

        if isinstance(description, str) and description in operation_counts:
            operation_counts[description] += 1

    return operation_counts
