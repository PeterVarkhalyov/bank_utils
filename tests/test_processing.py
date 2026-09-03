"""Pytest-тесты функций фильтрации и сортировки операций."""

from typing import Any

import pytest

from src.processing import Transaction, filter_by_state, sort_by_date


def test_filter_by_default_state(transactions: list[Transaction]) -> None:
    """По умолчанию возвращаются только выполненные операции."""
    result = filter_by_state(transactions)

    assert [transaction["id"] for transaction in result] == [41428829, 939719570]


@pytest.mark.parametrize(
    ("state", "expected_ids"),
    [
        ("EXECUTED", [41428829, 939719570]),
        ("CANCELED", [594226727, 615064591]),
        ("PENDING", [100000001]),
        ("UNKNOWN", []),
    ],
)
def test_filter_by_state(transactions: list[Transaction], state: str, expected_ids: list[int]) -> None:
    """Различные статусы фильтруются, а отсутствующий статус даёт пустой список."""
    result = filter_by_state(transactions, state)

    assert [transaction["id"] for transaction in result] == expected_ids


def test_filter_returns_new_list(transactions: list[Transaction]) -> None:
    """Фильтрация возвращает новый список и не изменяет исходный."""
    original = [transaction.copy() for transaction in transactions]

    result = filter_by_state(transactions)

    assert result is not transactions
    assert transactions == original


@pytest.mark.parametrize(
    ("descending", "expected_ids"),
    [
        (True, [100000001, 41428829, 615064591, 594226727, 939719570, 100000002]),
        (False, [100000002, 939719570, 594226727, 615064591, 41428829, 100000001]),
    ],
)
def test_sort_by_date(transactions: list[Transaction], descending: bool, expected_ids: list[int]) -> None:
    """Операции сортируются по дате в обоих направлениях."""
    original = [transaction.copy() for transaction in transactions]

    result = sort_by_date(transactions, descending=descending)

    assert [transaction["id"] for transaction in result] == expected_ids
    assert transactions == original


def test_sort_by_equal_dates_is_stable(
    transactions_with_equal_dates: list[Transaction],
) -> None:
    """Операции с одинаковыми датами сохраняют относительный порядок."""
    result = sort_by_date(transactions_with_equal_dates)

    assert [transaction["id"] for transaction in result] == [1, 2, 3]


def test_sort_by_nonstandard_date_strings(
    transactions_with_nonstandard_dates: list[Transaction],
) -> None:
    """Нестандартные строковые даты сортируются лексикографически."""
    result = sort_by_date(transactions_with_nonstandard_dates)

    assert [transaction["id"] for transaction in result] == [2, 1, 3]


def test_sort_without_date_raises_key_error(
    transactions_without_date: list[Transaction],
) -> None:
    """Отсутствующий ключ date вызывает KeyError."""
    with pytest.raises(KeyError, match="date"):
        sort_by_date(transactions_without_date)


def test_sort_mixed_date_types_raises_type_error(
    transactions_with_mixed_date_types: list[Transaction],
) -> None:
    """Несравнимые типы значений date вызывают TypeError."""
    with pytest.raises(TypeError):
        sort_by_date(transactions_with_mixed_date_types)


@pytest.mark.parametrize("transactions", [[], [{}]])
def test_filter_with_empty_or_incomplete_data(
    transactions: list[dict[str, Any]],
) -> None:
    """Пустые и неполные данные корректно дают пустой результат."""
    assert filter_by_state(transactions) == []
