"""Вспомогательные функции для загрузки данных."""

import json
from pathlib import Path
from typing import Any, cast

from src.processing import Transaction


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
    try:
        with open(file_path, encoding="utf-8") as json_file:
            data: Any = json.load(json_file)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []

    return [cast(Transaction, item) for item in data if isinstance(item, dict)]
