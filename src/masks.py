def get_mask_card_number(card_number: str) -> str | None:
    """Вернуть маску номера банковской карты.

    Первые шесть и последние четыре цифры остаются видимыми.

    Args:
        card_number: Номер банковской карты из 16 цифр.

    Returns:
        Номер карты в формате ``XXXX XX** **** XXXX`` или ``None``,
        если длина номера карты не равна 16 символам или содержит не цифры.
    """
    return (
        f"{card_number[:4]} {card_number[4:6]}** **** {card_number[-4:]}"
        if len(card_number) == 16 and card_number.isdigit()
        else None
    )


def get_mask_account(account_number: str) -> str | None:
    """Вернуть маску номера банковского счёта.

    Args:
        account_number: Номер банковского счёта длиной не менее четырёх цифр.

    Returns:
        Последние четыре цифры счёта с двумя звёздочками перед ними или
        ``None``, если длина номера меньше четырёх символов.
    """
    return f"**{account_number[-4:]}" if len(account_number) >= 4 else None
