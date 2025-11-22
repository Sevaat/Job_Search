from typing import Optional


def is_convertible_to_id(value: str) -> Optional[bool]:
    """
    Проверка на возможность конвертации строки в id компании
    :param value:
    :return:
    """
    try:
        company_id = int(value)
        if company_id > 0:
            return True
    except (ValueError, TypeError):
        return False
    return None
