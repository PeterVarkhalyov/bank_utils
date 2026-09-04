"""Тесты декоратора log."""

from pathlib import Path

import pytest

from src.decorators import log


def test_log_success_to_console(capsys: pytest.CaptureFixture[str]) -> None:
    """Успешный вызов возвращает результат и выводит ok в консоль."""

    @log()
    def add(x: int, y: int) -> int:
        return x + y

    result: int = add(1, 2)

    assert result == 3
    assert capsys.readouterr().out == "add ok\n"


def test_log_error_to_console(capsys: pytest.CaptureFixture[str]) -> None:
    """Ошибка и входные параметры выводятся, а исключение не скрывается."""

    @log()
    def divide(x: int, y: int) -> float:
        return x / y

    with pytest.raises(ZeroDivisionError):
        divide(1, 0)

    assert capsys.readouterr().out == (
        "divide error: division by zero. Inputs: (1, 0), {}\n"
    )


def test_log_error_with_keyword_arguments(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """В сообщение об ошибке включаются позиционные и именованные аргументы."""

    @log()
    def fail(value: int, *, reason: str) -> None:
        raise ValueError(reason)

    with pytest.raises(ValueError, match="invalid value"):
        fail(10, reason="invalid value")

    assert capsys.readouterr().out == (
        "fail error: invalid value. " "Inputs: (10,), {'reason': 'invalid value'}\n"
    )


def test_log_success_to_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """При заданном filename сообщения добавляются в файл, а не в консоль."""
    log_file = tmp_path / "mylog.txt"

    @log(filename=str(log_file))
    def multiply(x: int, y: int) -> int:
        return x * y

    assert multiply(2, 3) == 6
    assert multiply(4, 5) == 20
    assert log_file.read_text(encoding="utf-8") == "multiply ok\nmultiply ok\n"
    assert capsys.readouterr().out == ""


def test_log_error_to_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Ошибка записывается в файл вместе с входными параметрами."""
    log_file = tmp_path / "mylog.txt"

    @log(filename=str(log_file))
    def divide(x: int, y: int) -> float:
        return x / y

    with pytest.raises(ZeroDivisionError):
        divide(1, 0)

    assert log_file.read_text(encoding="utf-8") == (
        "divide error: division by zero. Inputs: (1, 0), {}\n"
    )
    assert capsys.readouterr().out == ""


def test_log_preserves_function_metadata() -> None:
    """Декоратор сохраняет имя и строку документации функции."""

    @log()
    def documented_function() -> str:
        """Описание функции."""
        return "result"

    assert documented_function.__name__ == "documented_function"
    assert documented_function.__doc__ == "Описание функции."
