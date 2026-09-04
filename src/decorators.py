"""Декораторы проекта."""

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def _write_log(message: str, filename: str | None) -> None:
    """Вывести сообщение в консоль или добавить его в файл."""
    if filename is None:
        print(message)
        return

    with open(filename, "a", encoding="utf-8") as log_file:
        log_file.write(f"{message}\n")


def log(
    filename: str | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Логировать успешное выполнение функции или возникшую ошибку.

    Args:
        filename: Файл для записи логов. Если значение не задано, сообщения
            выводятся в консоль.

    Returns:
        Декоратор, сохраняющий параметры и возвращаемый тип функции.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        """Обернуть функцию логированием."""

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """Вызвать функцию и записать результат её выполнения."""
            try:
                result = func(*args, **kwargs)
            except Exception as error:
                message = f"{func.__name__} error: {error}. " f"Inputs: {args}, {kwargs}"
                _write_log(message, filename)
                raise

            _write_log(f"{func.__name__} ok", filename)
            return result

        return wrapper

    return decorator
