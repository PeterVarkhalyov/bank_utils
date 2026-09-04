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


@pytest.fixture
def generator_transactions() -> list[Transaction]:
    """Вернуть транзакции с разными валютами и описаниями."""
    return [
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
            "operationAmount": {
                "amount": "9824.07",
                "currency": {
                    "name": "USD",
                    "code": "USD"
                }
            },
            "description": "Перевод организации",
            "from": "Счет 75106830613657916952",
            "to": "Счет 11776614605963066702"
        },
        {
            "id": 142264268,
            "state": "EXECUTED",
            "date": "2019-04-04T23:20:05.206878",
            "operationAmount": {
                "amount": "79114.93",
                "currency": {
                    "name": "USD",
                    "code": "USD"
                }
            },
            "description": "Перевод со счета на счет",
            "from": "Счет 19708645243227258542",
            "to": "Счет 75651667383060284188"
        },
        {
            "id": 873106923,
            "state": "EXECUTED",
            "date": "2019-03-23T01:09:46.296404",
            "operationAmount": {
                "amount": "43318.34",
                "currency": {
                    "name": "руб.",
                    "code": "RUB"
                }
            },
            "description": "Перевод со счета на счет",
            "from": "Счет 44812258784861134719",
            "to": "Счет 74489636417521191160"
        },
        {
            "id": 895315941,
            "state": "EXECUTED",
            "date": "2018-08-19T04:27:37.904916",
            "operationAmount": {
                "amount": "56883.54",
                "currency": {
                    "name": "USD",
                    "code": "USD"
                }
            },
            "description": "Перевод с карты на карту",
            "from": "Visa Classic 6831982476737658",
            "to": "Visa Platinum 8990922113665229"
        },
        {
            "id": 594226727,
            "state": "CANCELED",
            "date": "2018-09-12T21:27:25.241689",
            "operationAmount": {
                "amount": "67314.70",
                "currency": {
                    "name": "руб.",
                    "code": "RUB"
                }
            },
            "description": "Перевод организации",
            "from": "Visa Platinum 1246377376343588",
            "to": "Счет 14211924144426031657"
        },
    ]
