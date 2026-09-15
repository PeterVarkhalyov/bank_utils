"""Вспомогательные функции для загрузки данных из файлов CSV и Excel."""

import csv
import logging
from pathlib import Path
from typing import Any, cast
from zipfile import BadZipFile

import pandas as pd

from src.processing import Transaction

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("readers")
logger.setLevel(logging.DEBUG)
logger.propagate = False

file_handler = logging.FileHandler(
    LOG_DIR / "readers.log",
    mode="w",
    encoding="utf-8",
)
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_transactions_from_csv(file_path: str | Path) -> list[Transaction]:
    """Загрузить список финансовых транзакций из CSV-файла.

    Пустые строки и строки, содержащие только пробелы или разделители,
    пропускаются.

    Args:
        file_path: Путь к CSV-файлу с транзакциями.

    Returns:
        Список словарей с транзакциями. Если файл отсутствует,
        недоступен, пуст или содержит некорректные данные,
        возвращается пустой список.
    """
    logger.debug("Начало загрузки транзакций из файла: %s", file_path)

    transactions: list[Transaction] = []

    try:
        with open(
            file_path,
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file, delimiter=";")

            if reader.fieldnames is None:
                logger.error(
                    "Некорректная структура файла %s: отсутствует строка наименования столбцов.",
                    file_path,
                )
                return []

            for row in reader:
                row_is_empty = not any(isinstance(value, str) and value.strip() for value in row.values())

                if row_is_empty:
                    continue

                transactions.append(cast(Transaction, dict(row)))

    except (OSError, UnicodeDecodeError, csv.Error) as error:
        logger.error(
            "Не удалось загрузить транзакции из файла %s: %s",
            file_path,
            error,
        )
        return []

    skipped_items = len(list(reader)) - len(transactions)
    if skipped_items:
        logger.error(
            "В файле %s пропущено некорректных элементов: %d",
            file_path,
            skipped_items,
        )

    logger.info(
        "Успешно загружено транзакций из файла %s: %d",
        file_path,
        len(transactions),
    )

    return transactions


def get_transactions_from_xls(file_path: str | Path) -> list[Transaction]:
    """Загрузить список финансовых транзакций из Excel файла.

    Пустые строки и строки, содержащие только пробелы или разделители,
    пропускаются.

    Args:
        file_path: Путь к Excel файлу с транзакциями.

    Returns:
        Список словарей с транзакциями. Если файл отсутствует,
        недоступен, пуст или содержит некорректные данные,
        возвращается пустой список.
    """
    logger.debug("Начало загрузки транзакций из файла: %s", file_path)

    try:
        data_frame = pd.read_excel(file_path, sheet_name="Лист 1")

        if data_frame.empty:
            logger.info("Файл %s пуст.", file_path)
            return []

        records = cast(
            list[dict[str, Any]],
            data_frame.to_dict(orient="records"),
        )

        transactions: list[Transaction] = []

        for record in records:
            row_is_empty = not any(
                not pd.isna(value) and (not isinstance(value, str) or bool(value.strip())) for value in record.values()
            )

            if row_is_empty:
                continue

            transactions.append(cast(Transaction, record))

        logger.info(
            "Успешно загружено транзакций из файла %s: %d",
            file_path,
            len(transactions),
        )

        return transactions

    except (
        OSError,
        ValueError,
        ImportError,
        BadZipFile,
    ) as error:
        logger.error(
            "Не удалось загрузить транзакции из файла %s: %s",
            file_path,
            error,
        )
        return []
