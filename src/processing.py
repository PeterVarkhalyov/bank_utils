"""Функции фильтрации, сортировки и поиска банковских операций."""

import re
from typing import Any

Transaction = dict[str, Any]


def filter_by_state(transactions: list[Transaction], state: str = "EXECUTED") -> list[Transaction]:
    """Вернуть операции с указанным статусом.

    Args:
        transactions: Список словарей с данными банковских операций.
        state: Статус для фильтрации. По умолчанию ``EXECUTED``.

    Returns:
        Новый список операций, значение ключа ``state`` которых совпадает
        с запрошенным статусом. Операции без ключа ``state`` пропускаются.
    """
    return [transaction for transaction in transactions if transaction.get("state") == state]


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
    filtered_transactions: list[Transaction] = []

    for transaction in transactions:
        operation_amount = transaction.get("operationAmount")
        if not isinstance(operation_amount, dict):
            continue

        currency = operation_amount.get("currency")
        if not isinstance(currency, dict):
            continue

        if currency.get("code") == currency_code:
            filtered_transactions.append(transaction)

    return filtered_transactions


def sort_by_date(transactions: list[Transaction], descending: bool = True) -> list[Transaction]:
    """Вернуть операции, отсортированные по дате.

    Даты ожидаются в ISO-формате, при котором строковая сортировка совпадает
    с хронологическим порядком.

    Args:
        transactions: Список словарей с ключом ``date``.
        descending: Сортировать по убыванию, если значение равно ``True``.

    Returns:
        Новый список операций, отсортированный по значению ключа ``date``.

    Raises:
        KeyError: Если хотя бы в одной операции отсутствует ключ ``date``.
    """
    return sorted(
        transactions,
        key=lambda transaction: transaction["date"],
        reverse=descending,
    )


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
    if not search_string:
        return []

    search_pattern = re.compile(re.escape(search_string), re.IGNORECASE)

    return [
        transaction
        for transaction in transactions
        if isinstance((description := transaction.get("description")), str) and search_pattern.search(description)
    ]


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
    operation_counts = dict.fromkeys(categories, 0)

    for transaction in transactions:
        description = transaction.get("description")
        if isinstance(description, str) and description in operation_counts:
            operation_counts[description] += 1

    return operation_counts
