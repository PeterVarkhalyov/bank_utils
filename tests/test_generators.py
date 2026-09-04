"""Тесты генераторов банковских данных."""

from collections.abc import Iterator

import pytest

from src.generators import MAX_CARD_NUMBER, card_number_generator, filter_by_currency, transaction_descriptions
from src.processing import Transaction


@pytest.mark.parametrize(
    ("currency", "expected_ids"),
    [
        ("USD", [939719570, 142264268, 895315941]),
        ("RUB", [873106923, 594226727]),
        ("CNY", []),
    ],
)
def test_filter_by_currency(generator_transactions: list[Transaction], currency: str, expected_ids: list[int],) -> None:
    """Фильтр выдаёт транзакции выбранной валюты в исходном порядке."""
    result = list(filter_by_currency(generator_transactions, currency))

    assert [transaction["id"] for transaction in result] == expected_ids


def test_filter_by_currency_returns_iterator(generator_transactions: list[Transaction],) -> None:
    """Фильтр возвращает ленивый итератор."""
    result = filter_by_currency(generator_transactions, "USD")

    assert isinstance(result, Iterator)
    assert iter(result) is result


def test_filter_by_currency_without_currency_data_raises_key_error() -> None:
    """Отсутствие данных о валюте вызывает KeyError при обходе генератора."""
    transactions: list[Transaction] = [{"id": 1}]

    with pytest.raises(KeyError, match="operationAmount"):
        next(filter_by_currency(transactions, "USD"))


def test_transaction_descriptions(generator_transactions: list[Transaction],) -> None:
    """Описания выдаются по одному в исходном порядке."""
    result = list(transaction_descriptions(generator_transactions))

    assert result == [
        "Перевод организации",
        "Перевод со счета на счет",
        "Перевод со счета на счет",
        "Перевод с карты на карту",
        "Перевод организации",
    ]


def test_transaction_descriptions_empty_list() -> None:
    """Для пустого списка генератор не выдаёт значений."""
    assert list(transaction_descriptions([])) == []


def test_transaction_without_description_raises_key_error() -> None:
    """Отсутствие description вызывает KeyError при обходе генератора."""
    transactions: list[Transaction] = [{"id": 1}]

    with pytest.raises(KeyError, match="description"):
        next(transaction_descriptions(transactions))


@pytest.mark.parametrize(
    ("start", "stop", "expected"),
    [
        (
            1,
            3,
            [
                "0000 0000 0000 0001",
                "0000 0000 0000 0002",
                "0000 0000 0000 0003",
            ],
        ),
        (1234567890123456, 1234567890123456, ["1234 5678 9012 3456"]),
        (
            MAX_CARD_NUMBER - 1,
            MAX_CARD_NUMBER,
            ["9999 9999 9999 9998", "9999 9999 9999 9999"],
        ),
    ],
)
def test_card_number_generator(start: int, stop: int, expected: list[str]) -> None:
    """Генератор форматирует номера и включает обе границы диапазона."""
    assert list(card_number_generator(start, stop)) == expected


def test_card_number_generator_is_lazy() -> None:
    """Большой диапазон не вычисляется целиком при создании генератора."""
    generator = card_number_generator(1, MAX_CARD_NUMBER)

    assert next(generator) == "0000 0000 0000 0001"
    assert next(generator) == "0000 0000 0000 0002"


@pytest.mark.parametrize(
    ("start", "stop"),
    [
        (0, 1),
        (-1, 1),
        (2, 1),
        (1, MAX_CARD_NUMBER + 1),
    ],
)
def test_card_number_generator_invalid_range(start: int, stop: int) -> None:
    """Некорректные границы вызывают ValueError при обходе генератора."""
    with pytest.raises(ValueError, match="Диапазон"):
        next(card_number_generator(start, stop))
