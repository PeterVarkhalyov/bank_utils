"""Обработка справочника config/field_aliases.json"""

import json
import logging
from collections.abc import Mapping
from pathlib import Path
from typing import Any

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("fields")
logger.setLevel(logging.DEBUG)
logger.propagate = False

file_handler = logging.FileHandler(
    LOG_DIR / "fields.log",
    mode="w",
    encoding="utf-8",
)
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def load_fields(file_path: str | Path) -> Any:
    """Загрузить справочник путей к полям.

    Args:
        file_path: Путь к JSON-справочнику путей к полям.
    """
    logger.debug("Начало загрузки структур из файла: %s", file_path)

    try:
        with open(file_path, encoding="utf-8") as file:
            data: Any = json.load(file)
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as error:
        logger.error(
            "Не удалось загрузить справочник %s: %s",
            file_path,
            error,
        )
        return []

    if not isinstance(data, dict):
        logger.error(
            "Корневым элементом %s должен быть объект",
            file_path,
        )
        return []

    logger.info(
        "Успешно загружено транзакций из файла %s: %d",
        file_path,
        len(data),
    )

    return data


def get_by_path(item: Mapping[str, Any], path: str) -> Any:
    """Получить значение по буквальному ключу или вложенному пути.

    Буквальный ключ имеет приоритет: для пути ``currency.code`` сначала
    проверяется ключ с таким полным именем, а затем вложенная структура
    ``{"currency": {"code": ...}}``.

    Raises:
        KeyError: Если указанный путь отсутствует.
    """
    try:
        return item[path]
    except KeyError:
        logger.debug("Буквальный ключ %r не найден", path)

    value: Any = item

    try:
        for key in path.split("."):
            value = value[key]
    except (KeyError, TypeError) as error:
        logger.debug("Вложенный путь %r не найден", path)
        logger.error(
            "Путь %r не найден: %s",
            path,
            error,
        )
        raise KeyError(path) from error

    return value


def get_field_value(
    transaction: Mapping[str, Any],
    field_name: str,
    field_aliases: Mapping[str, list[str]],
) -> Any:
    """Найти значение поля транзакции по первому доступному `aliase`.

    Returns:
        Значение первого найденного поля или пустой список, если поле
        отсутствует в справочнике либо транзакции.
    """
    try:
        paths = field_aliases[field_name]
    except KeyError as error:
        logging.error(
            "Поле %s отсутствует в справочнике: %s",
            field_name,
            error,
        )
        return []

    for path in paths:
        try:
            return get_by_path(transaction, path)
        except KeyError:
            continue

    logging.error("Поле %s отсутствует в транзакции", field_name)
    return []
