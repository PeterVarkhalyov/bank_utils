"""Генераторы для последовательной обработки банковских данных."""

from collections.abc import Iterator
from typing import cast

from src.processing import Transaction

MIN_CARD_NUMBER = 1
MAX_CARD_NUMBER = 9_999_999_999_999_999


def filter_by_currency(transactions: list[Transaction], currency: str) -> Iterator[Transaction]:
    """Поочерёдно выдавать транзакции в указанной валюте.

    Args:
        transactions: Список транзакций с информацией о валюте операции.
        currency: Код валюты, например ``USD``.

    Yields:
        Транзакции, код валюты которых совпадает с аргументом ``currency``.

    Raises:
        KeyError: Если транзакция не содержит данных о валюте.
    """
    for transaction in transactions:
        if transaction["operationAmount"]["currency"]["code"] == currency:
            yield transaction


def transaction_descriptions(transactions: list[Transaction]) -> Iterator[str]:
    """Поочерёдно выдавать описания транзакций.

    Args:
        transactions: Список транзакций с ключом ``description``.

    Yields:
        Описание очередной транзакции.

    Raises:
        KeyError: Если транзакция не содержит ключ ``description``.
    """
    for transaction in transactions:
        yield cast(str, transaction["description"])


def card_number_generator(start: int, stop: int) -> Iterator[str]:
    """Генерировать номера банковских карт в заданном диапазоне.

    Обе границы диапазона включаются в результат.

    Args:
        start: Первый номер диапазона.
        stop: Последний номер диапазона.

    Yields:
        Номер карты в формате ``XXXX XXXX XXXX XXXX``.

    Raises:
        ValueError: Если границы выходят за допустимый диапазон или начальное
            значение больше конечного.
    """
    if not MIN_CARD_NUMBER <= start <= stop <= MAX_CARD_NUMBER:
        raise ValueError(
            "Диапазон должен находиться между 1 и 9999999999999999, " "а start не должен быть больше stop"
        )

    for card_number in range(start, stop + 1):
        number = f"{card_number:016d}"
        yield " ".join(number[index : index + 4] for index in range(0, 16, 4))
