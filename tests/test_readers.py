"""Тесты функций чтения транзакций из CSV- и Excel-файлов."""

import csv
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch
from zipfile import BadZipFile

import pytest

from src.processing import Transaction
from src.readers import get_transactions_from_csv, get_transactions_from_xls


@pytest.fixture
def reader_transactions() -> list[Transaction]:
    """Вернуть транзакции в формате, получаемом при чтении таблицы."""
    return [
        {"id": "1", "state": "EXECUTED", "amount": "100.00"},
        {"id": "2", "state": "CANCELED", "amount": "200.00"},
    ]


def test_get_transactions_from_csv_returns_records_and_skips_empty_rows(
    reader_transactions: list[Transaction],
) -> None:
    """CSV-функция должна вернуть записи и пропустить пустые строки."""
    empty_row = {"id": " ", "state": "", "amount": None}
    mocked_reader = MagicMock()
    mocked_reader.fieldnames = ["id", "state", "amount"]
    mocked_reader.__iter__.return_value = iter([reader_transactions[0], empty_row, reader_transactions[1]])
    mocked_file = mock_open()

    with (
        patch("builtins.open", mocked_file),
        patch("src.readers.csv.DictReader", return_value=mocked_reader) as mocked_dict_reader,
        patch("src.readers.logger.warning") as mocked_warning,
    ):
        result = get_transactions_from_csv(Path("data/transactions.csv"))

    assert result == reader_transactions
    mocked_file.assert_called_once_with(
        Path("data/transactions.csv"),
        encoding="utf-8-sig",
        newline="",
    )
    mocked_dict_reader.assert_called_once_with(
        mocked_file.return_value.__enter__.return_value,
        delimiter=";",
    )
    mocked_warning.assert_called_once_with(
        "В файле %s пропущено некорректных элементов: %d",
        Path("data/transactions.csv"),
        1,
    )


def test_get_transactions_from_csv_returns_empty_list_without_headers() -> None:
    """CSV-файл без заголовка должен дать пустой список."""
    mocked_reader = MagicMock()
    mocked_reader.fieldnames = None

    with (
        patch("builtins.open", mock_open()),
        patch("src.readers.csv.DictReader", return_value=mocked_reader),
    ):
        result = get_transactions_from_csv("empty.csv")

    assert result == []
    mocked_reader.__iter__.assert_not_called()


def test_get_transactions_from_csv_returns_empty_list_without_records() -> None:
    """CSV-файл только с заголовком должен дать пустой список."""
    mocked_reader = MagicMock()
    mocked_reader.fieldnames = ["id", "state"]
    mocked_reader.__iter__.return_value = iter([])

    with (
        patch("builtins.open", mock_open()),
        patch("src.readers.csv.DictReader", return_value=mocked_reader),
        patch("src.readers.logger.warning") as mocked_warning,
    ):
        result = get_transactions_from_csv("headers-only.csv")

    assert result == []
    mocked_warning.assert_not_called()


@pytest.mark.parametrize(
    "error",
    [
        FileNotFoundError("Файл не найден"),
        PermissionError("Нет доступа к файлу"),
        UnicodeDecodeError("utf-8", b"\xff", 0, 1, "Некорректный байт"),
    ],
    ids=["missing-file", "permission-error", "decode-error"],
)
def test_get_transactions_from_csv_handles_file_errors(error: OSError | UnicodeDecodeError) -> None:
    """Ошибки открытия и декодирования CSV должны дать пустой список."""
    with patch("builtins.open", side_effect=error) as mocked_file:
        result = get_transactions_from_csv("transactions.csv")

    assert result == []
    mocked_file.assert_called_once_with(
        "transactions.csv",
        encoding="utf-8-sig",
        newline="",
    )


def test_get_transactions_from_csv_handles_csv_error() -> None:
    """Ошибка разбора CSV должна дать пустой список."""
    mocked_reader = MagicMock()
    mocked_reader.fieldnames = ["id", "state"]
    mocked_reader.__iter__.side_effect = csv.Error("Некорректный CSV")

    with (
        patch("builtins.open", mock_open()),
        patch("src.readers.csv.DictReader", return_value=mocked_reader),
    ):
        result = get_transactions_from_csv("invalid.csv")

    assert result == []


def test_get_transactions_from_xls_returns_records_and_skips_empty_rows(
    reader_transactions: list[Transaction],
) -> None:
    """Excel-функция должна вернуть записи и пропустить пустые строки."""
    empty_row = {"id": None, "state": " ", "amount": float("nan")}
    mocked_data_frame = Mock()
    mocked_data_frame.empty = False
    mocked_data_frame.to_dict.return_value = [reader_transactions[0], empty_row, reader_transactions[1]]

    with (
        patch("src.readers.pd.read_excel", return_value=mocked_data_frame) as mocked_read_excel,
        patch("src.readers.logger.warning") as mocked_warning,
    ):
        result = get_transactions_from_xls(Path("data/transactions.xlsx"))

    assert result == reader_transactions
    mocked_read_excel.assert_called_once_with(
        Path("data/transactions.xlsx"),
        sheet_name="Лист 1",
    )
    mocked_data_frame.to_dict.assert_called_once_with(orient="records")
    mocked_warning.assert_called_once_with(
        "В файле %s пропущено некорректных элементов: %d",
        Path("data/transactions.xlsx"),
        1,
    )


def test_get_transactions_from_xls_returns_empty_list_for_empty_file() -> None:
    """Пустая таблица Excel должна дать пустой список."""
    mocked_data_frame = Mock()
    mocked_data_frame.empty = True

    with (
        patch("src.readers.pd.read_excel", return_value=mocked_data_frame),
        patch("src.readers.logger.warning") as mocked_warning,
    ):
        result = get_transactions_from_xls("empty.xlsx")

    assert result == []
    mocked_data_frame.to_dict.assert_not_called()
    mocked_warning.assert_not_called()


@pytest.mark.parametrize(
    "error",
    [
        FileNotFoundError("Файл не найден"),
        PermissionError("Нет доступа к файлу"),
        ValueError("Некорректный формат Excel"),
        ImportError("Не установлен движок Excel"),
        BadZipFile("Повреждённый Excel-файл"),
    ],
    ids=["missing-file", "permission-error", "value-error", "import-error", "bad-zip-file"],
)
def test_get_transactions_from_xls_handles_reading_errors(error: Exception) -> None:
    """Ошибки чтения Excel должны дать пустой список."""
    with patch("src.readers.pd.read_excel", side_effect=error) as mocked_read_excel:
        result = get_transactions_from_xls("transactions.xlsx")

    assert result == []
    mocked_read_excel.assert_called_once_with(
        "transactions.xlsx",
        sheet_name="Лист 1",
    )
