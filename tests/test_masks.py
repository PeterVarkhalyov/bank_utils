"""Pytest-тесты функций маскировки банковских данных."""

import pytest

from src.masks import get_mask_account, get_mask_card_number


@pytest.mark.parametrize(
    ("card_number", "expected"),
    [
        ("7000792289606361", "7000 79** **** 6361"),
        ("1234567890123456", "1234 56** **** 3456"),
        ("0000000000000000", "0000 00** **** 0000"),
        ("1234 5678 9012 3456", "1234 56** **** 3456"),
    ],
)
def test_get_mask_card_number(card_number: str, expected: str) -> None:
    """Корректные 16-значные номера маскируются по заданному шаблону."""
    assert get_mask_card_number(card_number) == expected


@pytest.mark.parametrize(
    "card_number",
    [
        "",
        "1",
        "123456789012345",
        "12345678901234567",
        "700079228960636a",
        "7000 7922 8960636",
        "7000-7922-8960636",
        "                ",
    ],
)
def test_get_mask_card_number_invalid_input(card_number: str) -> None:
    """Пустые, нестандартные и некорректные номера возвращают None."""
    assert get_mask_card_number(card_number) is None


@pytest.mark.parametrize(
    ("account_number", "expected"),
    [
        ("1234", "**1234"),
        ("73654108430135874305", "**4305"),
        ("00000000000000000000", "**0000"),
        ("1234567890123456789012345", "**2345"),
        ("1234567890123456789012 345", "**2345"),
    ],
)
def test_get_mask_account(account_number: str, expected: str) -> None:
    """Счета допустимой длины маскируются по последним четырём символам."""
    assert get_mask_account(account_number) == expected


@pytest.mark.parametrize("account_number", ["", "1", "12", "123", "      ", "123 ", " 123", "1 23"])
def test_get_mask_account_too_short(account_number: str) -> None:
    """Номер счёта короче четырёх символов возвращает None."""
    assert get_mask_account(account_number) is None
