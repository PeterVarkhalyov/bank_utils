"""Pytest-тесты функций подготовки банковских данных к отображению."""

import pytest

from src.widget import get_date, mask_account_card


@pytest.mark.parametrize(
    ("account_card", "expected"),
    [
        ("Visa Platinum 7000792289606361", "Visa Platinum 7000 79** **** 6361"),
        ("Mastercard 1234567890123456", "Mastercard 1234 56** **** 3456"),
        ("МИР Gold 0000000000000000", "МИР Gold 0000 00** **** 0000"),
        ("Счет 73654108430135874305", "Счет **4305"),
        ("Счёт 73654108430135874305", "Счёт **4305"),
        ("Account 73654108430135874305", "Account **4305"),
        ("сЧеТ 73654108430135874305", "сЧеТ **4305"),
        ("ACCOUNT 73654108430135874305", "ACCOUNT **4305"),
    ],
)
def test_mask_account_card(account_card: str, expected: str) -> None:
    """Функция выбирает нужную маску для разных карт и счетов."""
    assert mask_account_card(account_card) == expected


@pytest.mark.parametrize("account_card", ["", " ", "Visa", "Счёт", "Account"])
def test_mask_account_card_without_number(account_card: str) -> None:
    """Отсутствие номера вызывает ValueError."""
    with pytest.raises(ValueError) as exc_info:
        mask_account_card(account_card)

    """Для строки без номера возвращается понятное сообщение."""
    assert str(exc_info.value) == "Укажите тип и номер карты или счёта"


@pytest.mark.parametrize(
    "account_card",
    [
        "Visa 1234",
        "Visa 700079228960636a",
        "Visa 7000-7922-8960636",
        "Счёт 123",
        "Account ",
    ],
)
def test_mask_account_card_invalid_number(account_card: str) -> None:
    """Отсутствие номера вызывает ValueError."""
    with pytest.raises(ValueError) as exc_info:
        mask_account_card(account_card)

    """Для некорректного номера возвращается сообщение вместо исключения."""
    expected = (
        "Укажите тип и номер карты или счёта" if account_card == "Account " else "Некорректный номер карты или счёта"
    )
    assert str(exc_info.value) == expected


@pytest.mark.parametrize(
    ("date_string", "expected"),
    [
        ("2024-03-11T02:26:18.671407", "11.03.2024"),
        ("2024-03-11T02:26:18", "11.03.2024"),
        ("2024-03-11", "11.03.2024"),
        ("2024-02-29T23:59:59", "29.02.2024"),
        ("1999-12-31T23:59:59+03:00", "31.12.1999"),
    ],
)
def test_get_date(date_string: str, expected: str) -> None:
    """Допустимые варианты ISO-даты преобразуются в ДД.ММ.ГГГГ."""
    assert get_date(date_string) == expected


@pytest.mark.parametrize(
    "date_string",
    [
        "",
        " ",
        "not-a-date",
        "2024-99-99",
        "2023-02-29T00:00:00",
        "11.03.2024",
    ],
)
def test_get_date_invalid_input(date_string: str) -> None:
    """Пустые и некорректные даты вызывают ValueError."""
    with pytest.raises(ValueError):
        get_date(date_string)
