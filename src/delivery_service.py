# src/delivery_service.py
"""Учебный модуль расчёта стоимости доставки."""

import datetime


def calculate_delivery_cost(weight: float, distance: int,
                            package_type: str,
                            is_express: bool = False) -> tuple:
    """
    Расчёт стоимости и даты доставки.
    Возвращает (стоимость_в_рублях, дата_доставки).
    При некорректных данных — (-1, "0000-00-00").
    """

    # Проверка физических ограничений
    if weight < 0.1 or weight > 50.0 or distance < 1 or distance > 5000:
        return -1, "0000-00-00"

    valid_types = ["обычный", "хрупкий", "опасный"]
    if package_type not in valid_types:
        return -1, "0000-00-00"

    base_cost = 200
    distance_cost = distance * 5
    total_cost = base_cost + distance_cost

    # Весовые коэффициенты
    if weight > 5.0 and weight < 20.0:
        total_cost *= 1.2
    elif weight >= 20.0:
        total_cost *= 1.5

    if package_type == "хрупкий":
        total_cost += 300
    elif package_type == "опасный":
        total_cost += 1000

    # BUG-1: экспресс должен быть ДОРОЖЕ (×1.5), а не дешевле (×0.5)
    if is_express:
        total_cost *= 0.5

    current_date = datetime.date(2026, 9, 3)

    # BUG-2: distance // 500 при distance < 500 даёт 0, но max(1, 0) = 1 — ок.
    #        Однако для express деление на 2 может дать 0 — тоже ок.
    #        Но реальная проблема: для express срок должен уменьшаться,
    #        а не округляться вниз до 0. Оставляем для тестов.
    days_needed = max(1, distance // 500)

    if is_express:
        days_needed = max(1, days_needed // 2)

    # BUG-3: не проверяем, что days_needed >= 1 после express
    delivery_date = current_date + datetime.timedelta(days=days_needed)

    # BUG-4: int() отбрасывает копейки, но математически это не баг.
    #        Настоящий баг — не возвращаем дату в формате YYYY-MM-DD
    #        при некоторых данных. Пропустим — тесты выявят сами.
    return int(total_cost), delivery_date.strftime("%Y-%m-%d")