"""Вспомогательные функции для загрузки данных."""

import json
import logging
from pathlib import Path
from typing import Any, cast

from src.processing import Transaction

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
logger.propagate = False

file_handler = logging.FileHandler(
    LOG_DIR / "utils.log",
    mode="w",
    encoding="utf-8",
)
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_transactions_from_json(file_path: str | Path) -> list[Transaction]:
    """Загрузить список финансовых транзакций из JSON-файла.

    Args:
        file_path: Путь к JSON-файлу с транзакциями.

    Returns:
        Список словарей с транзакциями. Если файл не найден, недоступен,
        пуст, содержит некорректный JSON или его корневое значение не является
        списком, возвращается пустой список. Элементы списка, которые не
        являются словарями, пропускаются.
    """
    logger.debug("Начало загрузки транзакций из файла: %s", file_path)

    try:
        with open(file_path, encoding="utf-8") as json_file:
            data: Any = json.load(json_file)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        logger.error(
            "Не удалось загрузить транзакции из файла %s: %s",
            file_path,
            error,
        )
        return []

    if not isinstance(data, list):
        logger.error(
            "Некорректная структура файла %s: корневое значение не является списком",
            file_path,
        )
        return []

    transactions = [cast(Transaction, item) for item in data if isinstance(item, dict)]
    skipped_items = len(data) - len(transactions)

    if skipped_items:
        logger.warning(
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
