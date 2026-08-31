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
    return [
        transaction for transaction in transactions if transaction.get("state") == state
    ]
