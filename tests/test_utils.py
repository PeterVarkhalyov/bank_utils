"""Тесты загрузки транзакций из JSON-файла."""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.processing import Transaction
from src.utils import get_transactions_from_json


def test_get_transactions_from_json_returns_transactions() -> None:
    """Корректный JSON-список должен загружаться без изменений."""
    transactions: list[Transaction] = [
        {"id": 1, "state": "EXECUTED"},
        {"id": 2, "state": "CANCELED"},
    ]
    mocked_file = mock_open(read_data=json.dumps(transactions))

    with patch("builtins.open", mocked_file):
        result = get_transactions_from_json("data/operations.json")

    assert result == transactions
    mocked_file.assert_called_once_with("data/operations.json", encoding="utf-8")


@pytest.mark.parametrize("file_content", ["", "not-json", "{"])
def test_get_transactions_from_json_returns_empty_list_for_invalid_json(
    file_content: str,
) -> None:
    """Пустой или повреждённый JSON должен дать пустой список."""
    mocked_file = mock_open(read_data=file_content)

    with patch("builtins.open", mocked_file):
        result = get_transactions_from_json("operations.json")

    assert result == []


def test_get_transactions_from_json_returns_empty_list_for_missing_file() -> None:
    """Отсутствующий файл должен дать пустой список."""
    with patch("builtins.open", side_effect=FileNotFoundError) as mocked_file:
        result = get_transactions_from_json("missing.json")

    assert result == []
    mocked_file.assert_called_once_with("missing.json", encoding="utf-8")


@pytest.mark.parametrize(
    "json_value",
    [
        {"id": 1},
        "transaction",
        100,
        None,
    ],
)
def test_get_transactions_from_json_returns_empty_list_if_root_is_not_list(
    json_value: object,
) -> None:
    """Корневое значение JSON должно быть списком."""
    mocked_file = mock_open()

    with (
        patch("builtins.open", mocked_file),
        patch("src.utils.json.load", return_value=json_value) as mocked_load,
    ):
        result = get_transactions_from_json(Path("operations.json"))

    assert result == []
    mocked_load.assert_called_once()


def test_get_transactions_from_json_skips_non_dictionary_items() -> None:
    """В результате должны остаться только элементы-словари."""
    json_value = [{"id": 1}, None, "text", 100, ["nested"]]

    with (
        patch("builtins.open", mock_open()),
        patch("src.utils.json.load", return_value=json_value),
    ):
        result = get_transactions_from_json("operations.json")

    assert result == [{"id": 1}]


def test_get_transactions_from_json_handles_unicode_error() -> None:
    """Ошибка декодирования файла должна дать пустой список."""
    unicode_error = UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid byte")

    with (
        patch("builtins.open", mock_open()),
        patch("src.utils.json.load", side_effect=unicode_error),
    ):
        result = get_transactions_from_json("operations.json")

    assert result == []
