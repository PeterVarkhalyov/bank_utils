"""Получение информации через внешний API."""

import os
from datetime import datetime
from typing import Any, cast

import requests
from dotenv import load_dotenv

Transaction = dict[str, Any]
ApiResponse = dict[str, Any]

EXCHANGE_RATES_URL = "https://api.apilayer.com/exchangerates_data/convert"
API_TIMEOUT_SECONDS = 10
DATE_FORMATS = {
    "YYYY-MM-DD HH:MM:SS": "%Y-%m-%d %H:%M:%S",
    "YYYY-MM-DD": "%Y-%m-%d",
}

load_dotenv()


def get_api_key() -> str:
    """Функция возвращает API ключ"""
    api_key = os.getenv("EXCHANGE_RATES_API_KEY")
    if not api_key:
        raise RuntimeError("Не задана переменная EXCHANGE_RATES_API_KEY")

    return api_key


def get_response(url: str, params: dict[str, str | float]) -> ApiResponse:
    """Функция возвращает ответ API в виде словаря.

    Args:
        url: URL метода API.
        params: Параметры запроса.

    Returns:
        Ответ API в виде словаря.

    Raises:
        RuntimeError: Если API вернул ошибку или данные
            неожиданного формата.
        requests.HTTPError: Если API вернул ошибочный
            HTTP-статус без описания в JSON.
    """
    api_key = get_api_key()

    response = requests.get(
        url,
        headers={"apikey": api_key},
        params=params,
        timeout=API_TIMEOUT_SECONDS,
    )

    try:
        response_data: Any = response.json()
    except requests.exceptions.JSONDecodeError as error:
        response.raise_for_status()

        raise RuntimeError("API вернул ответ не в формате JSON") from error

    if not isinstance(response_data, dict):
        response.raise_for_status()

        raise RuntimeError("API вернул ответ в неожиданном формате")

    api_response = cast(ApiResponse, response_data)

    return api_response


def _raise_api_error(api_response: ApiResponse) -> None:
    """Функция возвращает исключения с кодом и сообщением об ошибке API."""
    error_data = api_response.get("error")

    if api_response.get("success") is not False and error_data is None:
        return

    if isinstance(error_data, dict):
        error_code = error_data.get("code", "unknown_error")
        error_message = error_data.get("message", "Описание ошибки отсутствует")
        raise RuntimeError(f"Ошибка API [{error_code}]: {error_message}")

    error_message = api_response.get("message") or error_data or "Неизвестная ошибка"
    raise RuntimeError(f"Ошибка API: {error_message}")


def _normalize_target_currency(to_currency: str) -> str:
    """Функция возвращает нормализированный код целевой валюты.

    Args:
        to_currency: код целевой валюты.

    Returns:
        Код целевой валюты без пробелов и в верхнем регистре.
        Если целевая валюта передана пустой - возвращает RUB.
    """
    if not isinstance(to_currency, str):
        raise TypeError("Валюта конвертации должна быть строкой")

    normalized_currency = to_currency.strip().upper()
    return normalized_currency or "RUB"


def _extract_amount(operation_amount: ApiResponse) -> float:
    """Функция проверяет тип данных суммы транзакции."""

    amount_data = operation_amount["amount"]
    if isinstance(amount_data, bool) or not isinstance(amount_data, (str, int, float)):
        raise ValueError("Сумма транзакции должна быть числом")

    try:
        return float(amount_data)
    except ValueError as error:
        raise ValueError("Сумма транзакции должна быть числом") from error


def _extract_currency_code(operation_amount: ApiResponse) -> str:
    """Функция проверяет тип данных кода валюты транзакции."""
    currency_data = operation_amount["currency"]
    if not isinstance(currency_data, dict):
        raise TypeError("Поле currency должно быть словарём")

    currency_code = currency_data["code"]
    if not isinstance(currency_code, str):
        raise TypeError("Код валюты транзакции должен быть строкой")

    currency_code = currency_code.strip().upper()
    if not currency_code:
        raise ValueError("Код валюты транзакции не должен быть пустым")

    return currency_code


def _extract_transaction_date(
    transaction: Transaction,
    date_format: str = "YYYY-MM-DD",
) -> str:
    """Функция преобразует дату транзакции в переданный формат."""
    transaction_date = transaction["date"]
    if not isinstance(transaction_date, str):
        raise TypeError("Дата транзакции должна быть строкой")

    try:
        output_format = DATE_FORMATS[date_format]
    except KeyError as error:
        raise ValueError(f"Неподдерживаемый формат даты: {date_format}") from error

    try:
        parsed_date = datetime.fromisoformat(transaction_date)
    except ValueError as error:
        raise ValueError("Дата транзакции должна быть в формате ISO") from error

    return parsed_date.strftime(output_format)


def _extract_transaction_data(transaction: Transaction) -> tuple[float, str, str]:
    """Функция извлекает и осуществляет проверку суммы, кода валюты и даты транзакции."""
    operation_amount = transaction["operationAmount"]
    if not isinstance(operation_amount, dict):
        raise TypeError("Поле operationAmount должно быть словарём")

    operation_data = cast(ApiResponse, operation_amount)

    return (
        _extract_amount(operation_data),
        _extract_currency_code(operation_data),
        _extract_transaction_date(transaction),
    )


def _extract_conversion_result(api_response: ApiResponse) -> float:
    """Функция извлекает и проверяет результат конвертации из ответа API."""
    _raise_api_error(api_response)

    result = api_response.get("result")
    if isinstance(result, bool) or not isinstance(result, (int, float, str)):
        raise RuntimeError("В ответе API отсутствует корректное поле result")

    try:
        return float(result)
    except ValueError as error:
        raise RuntimeError("Поле result невозможно преобразовать в число") from error


def transaction_amount_convert(transaction: Transaction, to_currency: str = "RUB") -> float:
    """Вернуть сумму транзакции в целевой валюте ``to_currency``.

    Для транзакций в целевой валюте возвращается исходная сумма. Суммы для валют, отличных от
    целевой валюты ``to_currency`` конвертируются через Exchange Rates Data API.

    Args:
        transaction: Транзакция с суммой и кодом валюты в ``operationAmount``.
        to_currency: Целевая валюта.

    Returns:
        Сумма транзакции в целевой валюте ``to_currency``.

    Raises:
        KeyError: Если в транзакции отсутствуют обязательные ключи.
        TypeError: Если ``operationAmount`` или ``currency`` не являются
            словарями либо код валюты не является строкой.
        ValueError: Если сумма некорректна или валюта не поддерживается.
        RuntimeError: Если отсутствует API-ключ или API вернул некорректный
            результат.
        requests.HTTPError: Если API вернул ошибочный HTTP-статус.
    """
    to_currency = _normalize_target_currency(to_currency)
    amount, currency_code, transaction_date = _extract_transaction_data(transaction)

    if currency_code == to_currency:
        return round(amount, 2)

    request_params: dict[str, str | float] = {
        "from": currency_code,
        "to": to_currency,
        "amount": amount,
        "date": transaction_date,
    }

    response = get_response(EXCHANGE_RATES_URL, request_params)
    return round(_extract_conversion_result(response), 2)
