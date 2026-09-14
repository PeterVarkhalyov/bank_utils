"""Тесты функций модуля external_api."""

from unittest.mock import Mock, patch

import pytest

from src.external_api import (
    EXCHANGE_RATES_URL,
    Transaction,
    _extract_transaction_date,
    get_response,
    transaction_amount_convert,
)


def make_transaction(
    amount: object = "100.00",
    currency: object = "USD",
    transaction_date: object = "2019-08-26T10:50:58.294041",
) -> Transaction:
    """Создать транзакцию с заданными суммой и валютой."""
    return {
        "date": transaction_date,
        "operationAmount": {
            "amount": amount,
            "currency": {"code": currency},
        },
    }


def test_get_response_returns_api_error_as_dictionary() -> None:
    """JSON с ошибкой должен возвращаться вызывающей функции."""
    error_response = {
        "error": {
            "code": "base_currency_access_restricted",
            "message": "Access restricted",
        }
    }
    mocked_response = Mock()
    mocked_response.json.return_value = error_response

    with (
        patch("src.external_api.get_api_key", return_value="test-key"),
        patch("src.external_api.requests.get", return_value=mocked_response),
    ):
        result = get_response("https://example.com", {"amount": 100.0})

    assert result == error_response
    mocked_response.raise_for_status.assert_not_called()


def test_transaction_amount_convert_raises_detailed_api_error() -> None:
    """Ошибка API должна содержать исходные код и сообщение."""
    error_response = {
        "error": {
            "code": "base_currency_access_restricted",
            "message": "Access restricted",
        }
    }

    with patch("src.external_api.get_response", return_value=error_response):
        with pytest.raises(
            RuntimeError,
            match=r"Ошибка API \[base_currency_access_restricted\]: Access restricted",
        ):
            transaction_amount_convert(make_transaction())


def test_transaction_amount_convert_uses_historical_date_and_rounds_result() -> None:
    """Конвертация должна передавать дату и округлять результат."""
    api_response = {"success": True, "result": "9200.126"}

    with patch("src.external_api.get_response", return_value=api_response) as mocked_get:
        result = transaction_amount_convert(make_transaction())

    assert result == 9200.13
    mocked_get.assert_called_once_with(
        EXCHANGE_RATES_URL,
        {
            "from": "USD",
            "to": "RUB",
            "amount": 100.0,
            "date": "2019-08-26",
        },
    )


def test_empty_target_currency_is_replaced_with_rub() -> None:
    """Пустая целевая валюта должна заменяться на RUB."""
    with patch("src.external_api.get_response", return_value={"result": 9200.126}) as mocked_get:
        result = transaction_amount_convert(make_transaction(), "   ")

    assert result == 9200.13
    assert mocked_get.call_args.args[1]["to"] == "RUB"
    assert mocked_get.call_args.args[1]["date"] == "2019-08-26"


def test_same_currency_does_not_request_api() -> None:
    """Для одинаковых валют должен возвращаться исходный amount."""
    with patch("src.external_api.get_response") as mocked_get:
        result = transaction_amount_convert(make_transaction("100.256", "rub"), "")

    assert result == 100.26
    mocked_get.assert_not_called()


@pytest.mark.parametrize(
    "transaction",
    [
        {"date": "2019-08-26", "operationAmount": "100 USD"},
        {
            "date": "2019-08-26",
            "operationAmount": {"amount": "100", "currency": "USD"},
        },
        {
            "date": "2019-08-26",
            "operationAmount": {"amount": "100", "currency": {"code": 840}},
        },
    ],
)
def test_invalid_transaction_structure_raises_type_error(transaction: Transaction) -> None:
    """Неправильная структура транзакции должна вызывать TypeError."""
    with pytest.raises(TypeError):
        transaction_amount_convert(transaction)


@pytest.mark.parametrize("amount", [None, True, "not-a-number"])
def test_invalid_amount_raises_value_error(amount: object) -> None:
    """Некорректная сумма должна вызывать ValueError."""
    with pytest.raises(ValueError, match="Сумма транзакции должна быть числом"):
        transaction_amount_convert(make_transaction(amount=amount))


def test_boolean_api_result_is_rejected() -> None:
    """Логическое значение result не должно приниматься за число."""
    with patch("src.external_api.get_response", return_value={"result": True}):
        with pytest.raises(RuntimeError, match="корректное поле result"):
            transaction_amount_convert(make_transaction())


@pytest.mark.parametrize(
    ("api_response", "expected_message"),
    [
        ({"success": False, "message": "Rate unavailable"}, "Rate unavailable"),
        ({"error": "Access denied"}, "Access denied"),
        ({"success": False}, "Неизвестная ошибка"),
    ],
)
def test_transaction_amount_convert_handles_other_api_errors(
    api_response: dict[str, object], expected_message: str
) -> None:
    """Разные форматы ошибки API должны преобразовываться в RuntimeError."""
    with patch("src.external_api.get_response", return_value=api_response):
        with pytest.raises(RuntimeError, match=expected_message):
            transaction_amount_convert(make_transaction())


@pytest.mark.parametrize("result", [None, True, [], {}, object()])
def test_transaction_amount_convert_rejects_invalid_result(result: object) -> None:
    """Поле result должно содержать число или числовую строку."""
    with patch("src.external_api.get_response", return_value={"result": result}):
        with pytest.raises(RuntimeError, match="корректное поле result"):
            transaction_amount_convert(make_transaction())


def test_transaction_amount_convert_rejects_non_numeric_result() -> None:
    """Нечисловая строка result должна приводить к RuntimeError."""
    with patch("src.external_api.get_response", return_value={"result": "invalid"}):
        with pytest.raises(RuntimeError, match="невозможно преобразовать"):
            transaction_amount_convert(make_transaction())


def test_transaction_amount_convert_rejects_empty_source_currency() -> None:
    """Код исходной валюты не должен быть пустым."""
    with pytest.raises(ValueError, match="не должен быть пустым"):
        transaction_amount_convert(make_transaction(currency="   "))


def test_transaction_amount_convert_rejects_non_string_target_currency() -> None:
    """Код целевой валюты должен быть строкой."""
    with pytest.raises(TypeError, match="Валюта конвертации должна быть строкой"):
        transaction_amount_convert(make_transaction(), 123)  # type: ignore[arg-type]


@pytest.mark.parametrize("transaction_date", [None, 20190826])
def test_non_string_transaction_date_raises_type_error(transaction_date: object) -> None:
    """Дата транзакции должна быть строкой."""
    with pytest.raises(TypeError, match="Дата транзакции должна быть строкой"):
        transaction_amount_convert(make_transaction(transaction_date=transaction_date))


def test_invalid_transaction_date_raises_value_error() -> None:
    """Некорректная ISO-дата должна вызывать ValueError."""
    with pytest.raises(ValueError, match="Дата транзакции должна быть в формате ISO"):
        transaction_amount_convert(make_transaction(transaction_date="26.08.2019"))


@pytest.mark.parametrize(
    ("date_format", "expected"),
    [
        ("YYYY-MM-DD", "2019-08-26"),
        ("YYYY-MM-DD HH:MM:SS", "2019-08-26 10:50:58"),
    ],
)
def test_extract_transaction_date_supports_requested_formats(
    date_format: str,
    expected: str,
) -> None:
    """Дата должна возвращаться в переданном формате."""
    assert _extract_transaction_date(make_transaction(), date_format) == expected


def test_extract_transaction_date_rejects_unknown_format() -> None:
    """Неизвестный формат даты должен приводить к ValueError."""
    with pytest.raises(ValueError, match="Неподдерживаемый формат даты"):
        _extract_transaction_date(make_transaction(), "DD.MM.YYYY")


@pytest.mark.parametrize(
    "transaction",
    [
        {},
        {"operationAmount": {}},
        {"operationAmount": {"amount": "100"}},
        {"operationAmount": {"amount": "100", "currency": {}}},
    ],
)
def test_missing_transaction_fields_raise_key_error(transaction: Transaction) -> None:
    """Отсутствие обязательных полей должно приводить к KeyError."""
    with pytest.raises(KeyError):
        transaction_amount_convert(transaction)
