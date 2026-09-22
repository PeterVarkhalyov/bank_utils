"""Тесты консольного интерфейса приложения."""

from collections.abc import Iterator
from unittest.mock import patch

import pytest

import main
from src.processing import Transaction

FIELD_ALIASES = {
    "date": ["date"],
    "description": ["description"],
    "from": ["from"],
    "to": ["to"],
    "amount": ["amount"],
    "currency_code": ["currency_code"],
    "currency_name": ["currency_name"],
}

TRANSACTION: Transaction = {
    "id": 1,
    "state": "EXECUTED",
    "date": "2024-03-11T02:26:18.671407",
    "description": "Перевод организации",
    "from": "Visa Platinum 7000792289606361",
    "to": "Счет 73654108430135874305",
    "amount": "100.00",
    "currency_code": "RUB",
    "currency_name": "руб.",
}


def input_values(values: list[str]) -> Iterator[str]:
    """Создать итератор ответов пользователя."""
    return iter(values)


def test_main_processes_json_with_all_filters(capsys: pytest.CaptureFixture[str]) -> None:
    """Основной сценарий должен применить все выбранные операции."""
    answers = input_values(
        [
            "1",
            "executed",
            "yes",
            "по возрастанию",
            "да",
            "yes",
            "перевод",
        ]
    )

    with (
        patch("builtins.input", side_effect=lambda: next(answers)),
        patch("main.get_transactions_from_json", return_value=[TRANSACTION]) as mocked_json,
        patch("main.filter_by_state", return_value=[TRANSACTION]) as mocked_state,
        patch("main.sort_by_date", return_value=[TRANSACTION]) as mocked_sort,
        patch("main.filter_by_currency_code", return_value=[TRANSACTION]) as mocked_currency,
        patch("main.process_bank_search", return_value=[TRANSACTION]) as mocked_search,
        patch("main.process_bank_operations") as mocked_operations,
        patch("main.load_fields", return_value=FIELD_ALIASES),
    ):
        main.main()

    output = capsys.readouterr().out
    mocked_json.assert_called_once_with(main.JSON_PATH)
    mocked_state.assert_called_once_with([TRANSACTION], "EXECUTED")
    mocked_sort.assert_called_once_with([TRANSACTION], False)
    mocked_currency.assert_called_once_with([TRANSACTION])
    mocked_search.assert_called_once_with([TRANSACTION], "перевод")
    mocked_operations.assert_called_once_with([TRANSACTION], ["перевод"])
    assert "Для обработки выбран JSON-файл." in output
    assert "Пользователь: ПО ВОЗРАСТАНИЮ" in output
    assert "11.03.2024 Перевод организации" in output
    assert "Visa Platinum 7000 79** **** 6361 -> Счет **4305" in output
    assert "100.00 RUB (руб.)" in output
    assert "Всего банковских операций в выборке: 1" in output


def test_main_repeats_invalid_answers_and_processes_csv(capsys: pytest.CaptureFixture[str]) -> None:
    """Ошибочные ответы должны запрашиваться повторно, а фильтры можно пропустить."""
    csv_transaction = {
        **TRANSACTION,
        "state": "CANCELED",
        "from": "",
    }
    answers = input_values(
        [
            "9",
            "2",
            "unknown",
            "canceled",
            "maybe",
            "no",
            "не знаю",
            "нет",
            "later",
            "no",
        ]
    )

    with (
        patch("builtins.input", side_effect=lambda: next(answers)),
        patch("main.get_transactions_from_csv", return_value=[csv_transaction]) as mocked_csv,
        patch("main.filter_by_state", return_value=[csv_transaction]),
        patch("main.sort_by_date") as mocked_sort,
        patch("main.filter_by_currency_code") as mocked_currency,
        patch("main.process_bank_search") as mocked_search,
        patch("main.load_fields", return_value=FIELD_ALIASES),
    ):
        main.main()

    output = capsys.readouterr().out
    mocked_csv.assert_called_once_with(main.CSV_PATH)
    mocked_sort.assert_not_called()
    mocked_currency.assert_not_called()
    mocked_search.assert_not_called()
    assert "Не верный пункт меню! Повторите выбор." in output
    assert "Статус операции UNKNOWN недоступен." in output
    assert "MAYBE недоступно." in output
    assert "НЕ ЗНАЮ недоступно." in output
    assert "LATER недоступно." in output
    assert "Счет **4305" in output


def test_main_processes_xlsx_and_stops_for_empty_result(capsys: pytest.CaptureFixture[str]) -> None:
    """При отсутствии совпадений программа должна вывести сообщение и завершиться."""
    answers = input_values(
        [
            "3",
            "pending",
            "да",
            "неверное направление",
            "по убыванию",
            "yes",
            "да",
            "зарплата",
        ]
    )

    with (
        patch("builtins.input", side_effect=lambda: next(answers)),
        patch("main.get_transactions_from_xls", return_value=[TRANSACTION]) as mocked_xlsx,
        patch("main.filter_by_state", return_value=[TRANSACTION]),
        patch("main.sort_by_date", return_value=[TRANSACTION]) as mocked_sort,
        patch("main.filter_by_currency_code", return_value=[TRANSACTION]),
        patch("main.process_bank_search", return_value=[]),
        patch("main.process_bank_operations") as mocked_operations,
        patch("main._print_transactions") as mocked_print,
    ):
        main.main()

    output = capsys.readouterr().out
    mocked_xlsx.assert_called_once_with(main.XLSX_PATH)
    mocked_sort.assert_called_once_with([TRANSACTION], True)
    mocked_operations.assert_not_called()
    mocked_print.assert_not_called()
    assert "НЕВЕРНОЕНАПРАВЛЕНИЕ недоступно." in output
    assert "Не найдено ни одной транзакции" in output


def test_print_transactions_handles_invalid_aliases(capsys: pytest.CaptureFixture[str]) -> None:
    """Некорректный справочник полей должен завершить печать сообщением."""
    with patch("main.load_fields", return_value=[]):
        main._print_transactions([TRANSACTION])

    assert "Не удалось загрузить справочник полей" in capsys.readouterr().out


def test_format_transaction_keeps_invalid_values() -> None:
    """Некорректные дата и реквизиты должны выводиться без преобразования."""
    transaction = {
        **TRANSACTION,
        "date": "неизвестная дата",
        "from": "неверные реквизиты",
        "to": None,
        "currency_name": [],
    }

    result = main._format_transaction(transaction, FIELD_ALIASES)

    assert result == {
        "operation": "неизвестная дата Перевод организации",
        "route": "неверные реквизиты -> ",
        "amount": "100.00 RUB ()",
    }
