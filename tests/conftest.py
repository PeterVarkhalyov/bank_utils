"""Общие фикстуры с данными банковских операций."""

import pytest

from src.processing import Transaction


@pytest.fixture
def transactions() -> list[Transaction]:
    """Вернуть операции с разными статусами и датами."""
    return [
        {
            "id": 41428829,
            "state": "EXECUTED",
            "date": "2019-07-03T18:35:29.512364",
        },
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
        },
        {
            "id": 594226727,
            "state": "CANCELED",
            "date": "2018-09-12T21:27:25.241689",
        },
        {
            "id": 615064591,
            "state": "CANCELED",
            "date": "2018-10-14T08:21:33.419441",
        },
        {
            "id": 100000001,
            "state": "PENDING",
            "date": "2020-01-01T00:00:00.000000",
        },
        {
            "id": 100000002,
            "date": "2017-01-01T00:00:00.000000",
        },
    ]


@pytest.fixture
def transactions_with_equal_dates() -> list[Transaction]:
    """Вернуть операции, две из которых имеют одинаковую дату."""
    return [
        {"id": 1, "state": "EXECUTED", "date": "2024-03-11T10:00:00"},
        {"id": 2, "state": "CANCELED", "date": "2024-03-11T10:00:00"},
        {"id": 3, "state": "PENDING", "date": "2023-01-01T00:00:00"},
    ]


@pytest.fixture
def transactions_with_nonstandard_dates() -> list[Transaction]:
    """Вернуть операции с датами в нестандартных строковых форматах."""
    return [
        {"id": 1, "state": "EXECUTED", "date": "31.12.2023"},
        {"id": 2, "state": "EXECUTED", "date": "not-a-date"},
        {"id": 3, "state": "EXECUTED", "date": ""},
    ]


@pytest.fixture
def transactions_without_date() -> list[Transaction]:
    """Вернуть список с операцией без обязательного ключа date."""
    return [
        {"id": 1, "state": "EXECUTED", "date": "2024-01-01T00:00:00"},
        {"id": 2, "state": "CANCELED"},
    ]


@pytest.fixture
def transactions_with_mixed_date_types() -> list[Transaction]:
    """Вернуть операции с несравнимыми типами значений date."""
    return [
        {"id": 1, "state": "EXECUTED", "date": "2024-01-01T00:00:00"},
        {"id": 2, "state": "EXECUTED", "date": None},
    ]
