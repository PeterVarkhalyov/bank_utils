"""Тесты загрузки и получения полей банковских операций."""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.fields import get_by_path, get_field_value, load_fields


def test_load_fields_returns_dictionary() -> None:
    """Корректный JSON-объект должен возвращаться без изменений."""
    aliases = {"currency_code": ["currency_code", "operationAmount.currency.code"]}
    mocked_file = mock_open()

    with (
        patch("builtins.open", mocked_file),
        patch("src.fields.json.load", return_value=aliases) as mocked_load,
    ):
        result = load_fields(Path("config/field_aliases.json"))

    assert result == aliases
    mocked_file.assert_called_once_with(Path("config/field_aliases.json"), encoding="utf-8")
    mocked_load.assert_called_once_with(mocked_file.return_value.__enter__.return_value)


@pytest.mark.parametrize(
    "error",
    [
        FileNotFoundError("Файл не найден"),
        PermissionError("Нет доступа к файлу"),
    ],
    ids=["missing-file", "permission-error"],
)
def test_load_fields_returns_empty_list_for_open_errors(error: OSError) -> None:
    """Ошибки открытия справочника должны приводить к пустому списку."""
    with patch("builtins.open", side_effect=error):
        result = load_fields("aliases.json")

    assert result == []


@pytest.mark.parametrize(
    "error",
    [
        UnicodeDecodeError("utf-8", b"\xff", 0, 1, "Некорректный байт"),
        json.JSONDecodeError("Некорректный JSON", "{", 0),
    ],
    ids=["decode-error", "json-error"],
)
def test_load_fields_returns_empty_list_for_parsing_errors(error: Exception) -> None:
    """Ошибки декодирования справочника должны дать пустой список."""
    with (
        patch("builtins.open", mock_open()),
        patch("src.fields.json.load", side_effect=error),
    ):
        result = load_fields("aliases.json")

    assert result == []


@pytest.mark.parametrize("json_value", [[], "aliases", 100, None])
def test_load_fields_rejects_non_dictionary_root(json_value: object) -> None:
    """Корневой JSON-элемент должен быть объектом."""
    with (
        patch("builtins.open", mock_open()),
        patch("src.fields.json.load", return_value=json_value),
    ):
        result = load_fields("aliases.json")

    assert result == []


def test_get_by_path_prefers_literal_key() -> None:
    """Полный буквальный ключ должен иметь приоритет над вложенным путём."""
    item = {
        "currency.code": "USD",
        "currency": {"code": "RUB"},
    }

    assert get_by_path(item, "currency.code") == "USD"


def test_get_by_path_returns_nested_value() -> None:
    """Значение должно извлекаться по вложенному пути через точку."""
    item = {"operationAmount": {"currency": {"code": "RUB"}}}

    assert get_by_path(item, "operationAmount.currency.code") == "RUB"


@pytest.mark.parametrize(
    "item",
    [
        {},
        {"operationAmount": None},
    ],
    ids=["missing-key", "non-mapping-intermediate-value"],
)
def test_get_by_path_raises_key_error_for_missing_path(item: dict[str, object]) -> None:
    """Отсутствующий или недоступный путь должен вызвать KeyError."""
    with pytest.raises(KeyError, match="operationAmount.currency.code"):
        get_by_path(item, "operationAmount.currency.code")


def test_get_field_value_returns_first_available_alias() -> None:
    """Первый существующий алиас должен определить значение поля."""
    transaction = {
        "currency_code": "USD",
        "operationAmount": {"currency": {"code": "RUB"}},
    }
    aliases = {"currency_code": ["currency_code", "operationAmount.currency.code"]}

    assert get_field_value(transaction, "currency_code", aliases) == "USD"


def test_get_field_value_uses_next_alias() -> None:
    """После отсутствующего пути должен проверяться следующий алиас."""
    transaction = {"operationAmount": {"currency": {"code": "RUB"}}}
    aliases = {"currency_code": ["currency_code", "operationAmount.currency.code"]}

    assert get_field_value(transaction, "currency_code", aliases) == "RUB"


@pytest.mark.parametrize(
    ("field_name", "aliases"),
    [
        ("date", {}),
        ("date", {"date": []}),
        ("date", {"date": ["date", "operation.date"]}),
    ],
)
def test_get_field_value_returns_empty_list_when_value_is_unavailable(
    field_name: str,
    aliases: dict[str, list[str]],
) -> None:
    """Неизвестное или отсутствующее поле должно дать пустой список."""
    assert get_field_value({}, field_name, aliases) == []
