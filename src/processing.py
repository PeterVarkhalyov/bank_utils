"""Функции фильтрации и сортировки банковских операций."""

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
