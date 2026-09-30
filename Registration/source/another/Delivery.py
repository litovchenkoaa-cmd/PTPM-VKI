import datetime


def calculate_delivery_cost(weight: float, distance: int, package_type: str, is_express: bool = False) -> tuple:
    """
    Расчет стоимости и параметров доставки посылки.
    Возвращает: (стоимость_в_рублях, дата_доставки)
    В случае критических ошибок или неверных параметров возвращает (-1, "0000-00-00").
    """

    # 1. Проверка физических ограничений на вес и дистанцию
    if weight < 0.1 or weight > 50.0 or distance < 1 or distance > 5000:
        return (-1, "0000-00-00")

    valid_types = ["обычный", "хрупкий", "опасный"]
    if package_type not in valid_types:
        return (-1, "0000-00-00")

    # 2. Базовые тарифные сетки
    base_cost = 200
    distance_cost = distance * 5
    total_cost = base_cost + distance_cost

    # 3. Рассчитываем весовые коэффициенты
    # ИСПРАВЛЕНО: было "weight > 5.0", из-за чего вес ровно 5.0 не получал наценку.
    # Теперь граница включена: >= 5.0
    if 5.0 <= weight < 20.0:
        total_cost *= 1.2
    elif weight >= 20.0:
        total_cost *= 1.5

    # 4. Надбавки за тип посылки
    if package_type == "хрупкий":
        total_cost += 300
    elif package_type == "опасный":
        total_cost += 1000

    # 5. Экспресс-доставка
    # ИСПРАВЛЕНО: было "total_cost *= 0.5", что делало экспресс-доставку в 2 раза ДЕШЕВЛЕ обычной.
    # Это грубая бизнес-логическая ошибка. Экспресс должен стоить дороже. Исправлено на множитель 1.5 (наценка 50%).
    if is_express:
        total_cost *= 1.5

    # 6. Логика расчета времени транспортировки
    current_date = datetime.date(2026, 9, 3)  # Фиксированная дата отправки (как в исходном ТЗ)

    days_needed = max(1, distance // 500)

    if is_express:
        # ИСПРАВЛЕНО: было "days_needed = days_needed // 2".
        # При distance=400, days_needed был 1. 1 // 2 = 0. Доставка за 0 дней невозможна.
        # Добавлено max(1, ...), чтобы гарантировать минимум 1 день даже для экспресса.
        days_needed = max(1, days_needed // 2)

    delivery_date = current_date + datetime.timedelta(days=days_needed)

    return int(total_cost), delivery_date.strftime("%Y-%m-%d")