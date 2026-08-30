from datetime import datetime

from src.masks import get_mask_account, get_mask_card_number

ACCOUNT_TYPES = {"счет", "счёт", "account"}


def mask_account_card(account_card: str) -> str:
    """Замаскировать номер карты или банковского счёта.

    Последнее слово входной строки считается номером, а предшествующая часть —
    типом карты или счёта. Типы ``Счет``, ``Счёт`` и ``Account`` распознаются
    без учёта регистра как банковские счета; остальные типы считаются картами.

    Args:
        account_card: Тип и номер карты или счёта, разделённые пробелом.

    Returns:
        Исходный тип и замаскированный номер.

    Raises:
        ValueError: Если строка не содержит тип и номер или номер некорректен.
    """
    try:
        item_type, item_number = account_card.strip().rsplit(maxsplit=1)
    except ValueError as error:
        raise ValueError("Укажите тип и номер карты или счёта") from error

    if item_type.casefold() in ACCOUNT_TYPES:
        masked_number = get_mask_account(item_number)
    else:
        masked_number = get_mask_card_number(item_number)

    if masked_number is None:
        raise ValueError("Некорректный номер карты или счёта")

    return f"{item_type} {masked_number}"
