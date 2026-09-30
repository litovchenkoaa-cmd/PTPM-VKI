import unittest
from source.another.Delivery import calculate_delivery_cost

class TestDeliveryCost(unittest.TestCase):

    def setUp(self):
        # Начальная настройка
        pass

    # 1. Успешный расчет для стандартной посылки (проверка базовой формулы и весового коэффициента)
    def test_calculate_delivery_cost_success_for_standard_package(self):
        # Вес 10.0 (коэфф. 1.2), дистанция 1000 (5000 руб), база 200. Итого: (200 + 5000) * 1.2 = 6240
        # Дни: max(1, 1000 // 500) = 2. Дата: 2026-09-03 + 2 = 2026-09-05
        cost, date = calculate_delivery_cost(10.0, 1000, "обычный", False)
        self.assertEqual(cost, 6240)
        self.assertEqual(date, "2026-09-05")

    # 2. Успешный расчет для тяжелой посылки (проверка границы >= 20.0 кг)
    def test_calculate_delivery_cost_success_for_heavy_package(self):
        # Вес 20.0 (коэфф. 1.5), дистанция 1000. Итого: (200 + 5000) * 1.5 = 7800
        cost, date = calculate_delivery_cost(20.0, 1000, "обычный", False)
        self.assertEqual(cost, 7800)
        self.assertEqual(date, "2026-09-05")

    # 3. Успешный расчет для хрупкой посылки (проверка фиксированной надбавки)
    def test_calculate_delivery_cost_success_for_fragile_package(self):
        # Вес 2.0 (без коэфф.), дистанция 100 (500 руб), база 200. Надбавка за хрупкость: +300. Итого: 1000
        cost, date = calculate_delivery_cost(2.0, 100, "хрупкий", False)
        self.assertEqual(cost, 1000)
        self.assertEqual(date, "2026-09-04") # 1 день доставки

    # 4. Успешный расчет для опасной посылки (проверка фиксированной надбавки)
    def test_calculate_delivery_cost_success_for_dangerous_package(self):
        # Вес 2.0, дистанция 100. Надбавка за опасность: +1000. Итого: 200 + 500 + 1000 = 1700
        cost, date = calculate_delivery_cost(2.0, 100, "опасный", False)
        self.assertEqual(cost, 1700)
        self.assertEqual(date, "2026-09-04")

    #- 5. Проверка исправления стоимости экспресс-доставки
    def test_calculate_delivery_cost_success_for_express_delivery(self):
        #Проверяет, что экспресс-доставка стоит ДОРОЖЕ обычной (множитель 1.5), а не дешевле.
        # Вес 3.0, дистанция 400. База+расстояние = 2200. Экспресс (коэфф. 1.5) = 3300.
        # Дни: max(1, 400 // 500) = 1. Экспресс: max(1, 1 // 2) = 1 (не может быть 0 дней).
        cost, date = calculate_delivery_cost(3.0, 400, "обычный", True)
        self.assertEqual(cost, 3300)
        self.assertEqual(date, "2026-09-04")

    # 6. Ошибка: вес посылки ниже минимального порога
    def test_calculate_delivery_cost_fails_when_weight_is_too_low(self):
        cost, date = calculate_delivery_cost(0.05, 100, "обычный", False)
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    # 7. Ошибка: вес посылки превышает максимальный порог
    def test_calculate_delivery_cost_fails_when_weight_is_too_high(self):
        cost, date = calculate_delivery_cost(55.0, 100, "обычный", False)
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    # 8. Ошибка: дистанция ниже минимального порога
    def test_calculate_delivery_cost_fails_when_distance_is_too_low(self):
        cost, date = calculate_delivery_cost(5.0, 0, "обычный", False)
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    # 9. Ошибка: дистанция превышает максимальный порог
    def test_calculate_delivery_cost_fails_when_distance_is_too_high(self):
        cost, date = calculate_delivery_cost(5.0, 6000, "обычный", False)
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    # 10. Ошибка: передан недопустимый тип посылки
    def test_calculate_delivery_cost_fails_when_package_type_is_invalid(self):
        cost, date = calculate_delivery_cost(5.0, 100, "секретный", False)
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    #- 11. Проверка исправления границы веса ровно 5.0 кг
    def test_weight_boundary_exactly_5_kg_applies_surcharge(self):
        """
        Проверяет, что вес ровно 5.0 кг получает наценку 1.2.
        Математика: База 200 + (100 км * 5) = 700.
        С множителем 1.2: 700 * 1.2 = 840.
        (В старой версии с условием weight > 5.0 результат был бы 700, так как 5.0 не попадало в диапазон).
        """
        cost, date = calculate_delivery_cost(5.0, 100, "обычный", False)
        self.assertEqual(cost, 840, "Вес ровно 5.0 кг должен получать коэффициент 1.2")



    def tearDown(self):
        # Метод вызывается после каждого теста для очистки
        pass

if __name__ == '__main__':
    unittest.main()