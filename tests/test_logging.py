"""Тесты файлового логирования модулей masks и utils."""

import logging
import re
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src import masks, utils

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize(
    ("module_logger", "handler", "formatter", "file_name"),
    [
        (masks.logger, masks.file_handler, masks.file_formatter, "masks.log"),
        (utils.logger, utils.file_handler, utils.file_formatter, "utils.log"),
    ],
)
def test_file_logger_configuration(
    module_logger: logging.Logger,
    handler: logging.FileHandler,
    formatter: logging.Formatter,
    file_name: str,
) -> None:
    """Логер должен писать DEBUG-сообщения в файл внутри каталога logs."""
    assert module_logger.level == logging.DEBUG
    assert module_logger.propagate is False
    assert handler.level == logging.DEBUG
    assert handler.mode == "w"
    assert handler.formatter is formatter
    assert Path(handler.baseFilename) == PROJECT_ROOT / "logs" / file_name


@pytest.mark.parametrize(
    ("module_logger", "formatter"),
    [
        (masks.logger, masks.file_formatter),
        (utils.logger, utils.file_formatter),
    ],
)
def test_file_formatter_contains_required_fields(
    module_logger: logging.Logger,
    formatter: logging.Formatter,
) -> None:
    """Строка лога должна содержать время, модуль, уровень и сообщение."""
    record = module_logger.makeRecord(
        module_logger.name,
        logging.ERROR,
        __file__,
        1,
        "Тестовое событие",
        (),
        None,
    )

    log_line = formatter.format(record)

    assert re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}", log_line)
    assert module_logger.name in log_line
    assert "ERROR" in log_line
    assert "Тестовое событие" in log_line


def test_masks_logs_successful_operation() -> None:
    """Успешная маскировка карты должна логироваться на уровне INFO."""
    with patch.object(masks.logger, "info") as mocked_info:
        result = masks.get_mask_card_number("7000792289606361")

    assert result == "7000 79** **** 6361"
    mocked_info.assert_called_once()


def test_masks_logs_invalid_operation_as_error() -> None:
    """Некорректный номер карты должен логироваться на уровне ERROR."""
    with patch.object(masks.logger, "error") as mocked_error:
        result = masks.get_mask_card_number("123")

    assert result is None
    mocked_error.assert_called_once()


def test_utils_logs_successful_loading() -> None:
    """Успешная загрузка транзакций должна логироваться на уровне INFO."""
    with (
        patch("builtins.open", mock_open(read_data='[{"id": 1}]')),
        patch.object(utils.logger, "info") as mocked_info,
    ):
        result = utils.get_transactions_from_json("operations.json")

    assert result == [{"id": 1}]
    mocked_info.assert_called_once()


def test_utils_logs_loading_error() -> None:
    """Ошибка открытия JSON-файла должна логироваться на уровне ERROR."""
    with (
        patch("builtins.open", side_effect=FileNotFoundError),
        patch.object(utils.logger, "error") as mocked_error,
    ):
        result = utils.get_transactions_from_json("missing.json")

    assert result == []
    mocked_error.assert_called_once()
