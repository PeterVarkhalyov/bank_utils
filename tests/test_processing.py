"""Pytest-тесты функций фильтрации и сортировки операций."""

from typing import Any

import pytest

from src.processing import (
    Transaction,
    filter_by_state,
    process_bank_operations,
    process_bank_search,
    sort_by_date,
)


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


@pytest.fixture
def transactions_with_descriptions() -> list[Transaction]:
    """Вернуть операции с разными описаниями."""
    return [
        {"id": 1, "description": "Перевод организации"},
        {"id": 2, "description": "Перевод со счета на счет"},
        {"id": 3, "description": "ПЕРЕВОД ОРГАНИЗАЦИИ"},
        {"id": 4, "description": "Открытие вклада"},
        {"id": 5, "description": "Оплата заказа (ООО Ромашка)"},
        {"id": 6},
        {"id": 7, "description": None},
    ]


@pytest.mark.parametrize(
    ("search_string", "expected_ids"),
    [
        ("перевод", [1, 2, 3]),
        ("организации", [1, 3]),
        ("ВКЛАД", [4]),
        ("несуществующая операция", []),
        ("", []),
    ],
)
def test_process_bank_search(
    transactions_with_descriptions: list[Transaction],
    search_string: str,
    expected_ids: list[int],
) -> None:
    """Поиск должен находить строку в описании без учёта регистра."""
    result = process_bank_search(transactions_with_descriptions, search_string)

    assert [transaction["id"] for transaction in result] == expected_ids


def test_process_bank_search_treats_special_characters_as_text(
    transactions_with_descriptions: list[Transaction],
) -> None:
    """Специальные символы регулярных выражений должны искаться буквально."""
    result = process_bank_search(transactions_with_descriptions, "(ООО Ромашка)")

    assert [transaction["id"] for transaction in result] == [5]


def test_process_bank_search_returns_new_list(
    transactions_with_descriptions: list[Transaction],
) -> None:
    """Результат поиска должен быть новым списком."""
    result = process_bank_search(transactions_with_descriptions, "перевод")

    assert result is not transactions_with_descriptions


def test_process_bank_operations_counts_requested_categories(
    transactions_with_descriptions: list[Transaction],
) -> None:
    """Для каждой запрошенной категории должно возвращаться число операций."""
    categories = [
        "Перевод организации",
        "Перевод со счета на счет",
        "Открытие вклада",
        "Закрытие вклада",
    ]

    result = process_bank_operations(transactions_with_descriptions, categories)

    assert result == {
        "Перевод организации": 1,
        "Перевод со счета на счет": 1,
        "Открытие вклада": 1,
        "Закрытие вклада": 0,
    }


@pytest.mark.parametrize(
    ("transactions", "categories", "expected"),
    [
        ([], ["Перевод организации"], {"Перевод организации": 0}),
        ([{"id": 1}], ["Перевод организации"], {"Перевод организации": 0}),
        ([{"description": None}], ["Перевод организации"], {"Перевод организации": 0}),
        ([{"description": "Перевод организации"}], [], {}),
    ],
)
def test_process_bank_operations_handles_empty_or_incomplete_data(
    transactions: list[Transaction],
    categories: list[str],
    expected: dict[str, int],
) -> None:
    """Пустые и неполные данные должны обрабатываться без ошибок."""
    assert process_bank_operations(transactions, categories) == expected
