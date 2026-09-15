"""Функции для маскировки банковских данных."""

import logging
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("masks")
logger.setLevel(logging.DEBUG)
logger.propagate = False

file_handler = logging.FileHandler(
    LOG_DIR / "masks.log",
    mode="w",
    encoding="utf-8",
)
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_mask_card_number(card_number: str) -> str | None:
    """Вернуть маску номера банковской карты.

    Первые шесть и последние четыре цифры остаются видимыми.

    Args:
        card_number: Номер банковской карты из 16 цифр.

    Returns:
        Номер карты в формате ``XXXX XX** **** XXXX`` или ``None``,
        если длина номера карты не равна 16 символам или содержит не цифры.
    """
    logger.debug("Начало маскирования номера банковской карты")
    normalized_card_number = "".join(card_number.split())

    if len(normalized_card_number) != 16 or not normalized_card_number.isdigit():
        logger.error(
            "Некорректный номер карты: длина после нормализации — %d",
            len(normalized_card_number),
        )
        return None

    masked_card_number = (
        f"{normalized_card_number[:4]} " f"{normalized_card_number[4:6]}** **** " f"{normalized_card_number[-4:]}"
    )
    logger.info("Номер карты успешно замаскирован: %s", masked_card_number)

    return masked_card_number


def get_mask_account(account_number: str) -> str | None:
    """Вернуть маску номера банковского счёта.

    Args:
        account_number: Номер банковского счёта длиной не менее четырёх цифр.

    Returns:
        Последние четыре цифры счёта с двумя звёздочками перед ними или
        ``None``, если длина номера меньше четырёх символов.
    """
    logger.debug("Начало маскирования номера банковского счёта")
    normalized_account_number = "".join(account_number.split())

    if len(normalized_account_number) < 4:
        logger.error(
            "Некорректный номер счёта: длина после нормализации — %d",
            len(normalized_account_number),
        )
        return None

    masked_account_number = f"**{normalized_account_number[-4:]}"
    logger.info("Номер счёта успешно замаскирован: %s", masked_account_number)

    return masked_account_number
