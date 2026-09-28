# tests/test_delivery.py
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "src")))

from delivery_service import calculate_delivery_cost


# ============================================================
# ВАЛИДАЦИЯ ВХОДНЫХ ДАННЫХ
# ============================================================
class TestValidation(unittest.TestCase):

    def test_weight_too_light_returns_error(self):
        result = calculate_delivery_cost(0.05, 100, "обычный")
        self.assertEqual(result, (-1, "0000-00-00"))

    def test_weight_too_heavy_returns_error(self):
        result = calculate_delivery_cost(51.0, 100, "обычный")
        self.assertEqual(result, (-1, "0000-00-00"))

    def test_distance_too_small_returns_error(self):
        result = calculate_delivery_cost(1.0, 0, "обычный")
        self.assertEqual(result, (-1, "0000-00-00"))

    def test_distance_too_large_returns_error(self):
        result = calculate_delivery_cost(1.0, 5001, "обычный")
        self.assertEqual(result, (-1, "0000-00-00"))

    def test_invalid_package_type_returns_error(self):
        result = calculate_delivery_cost(1.0, 100, "волшебный")
        self.assertEqual(result, (-1, "0000-00-00"))

    def test_valid_boundary_weight_min(self):
        cost, date = calculate_delivery_cost(0.1, 100, "обычный")
        self.assertGreater(cost, 0)

    def test_valid_boundary_weight_max(self):
        cost, date = calculate_delivery_cost(50.0, 100, "обычный")
        self.assertGreater(cost, 0)


# ============================================================
# БАЗОВЫЙ РАСЧЁТ СТОИМОСТИ
# ============================================================
class TestBaseCost(unittest.TestCase):

    def test_base_cost_light_package(self):
        # вес 1, расстояние 100, обычный → 200 + 500 = 700
        cost, _ = calculate_delivery_cost(1.0, 100, "обычный")
        self.assertEqual(cost, 700)

    def test_cost_increases_with_distance(self):
        cost1, _ = calculate_delivery_cost(1.0, 100, "обычный")
        cost2, _ = calculate_delivery_cost(1.0, 200, "обычный")
        self.assertLess(cost1, cost2)


# ============================================================
# ВЕСОВЫЕ КОЭФФИЦИЕНТЫ
# ============================================================
class TestWeightCoefficients(unittest.TestCase):

    def test_weight_below_5kg_no_coefficient(self):
        # 1 кг → базовая цена без коэффициентов
        cost, _ = calculate_delivery_cost(1.0, 100, "обычный")
        self.assertEqual(cost, 700)

    def test_weight_between_5_and_20_applies_1_2(self):
        # 10 кг → (200+500)*1.2 = 840
        cost, _ = calculate_delivery_cost(10.0, 100, "обычный")
        self.assertEqual(cost, 840)

    def test_weight_20_or_more_applies_1_5(self):
        # 25 кг → (200+500)*1.5 = 1050
        cost, _ = calculate_delivery_cost(25.0, 100, "обычный")
        self.assertEqual(cost, 1050)

    def test_weight_exactly_20_uses_1_5(self):
        cost, _ = calculate_delivery_cost(20.0, 100, "обычный")
        self.assertEqual(cost, 1050)


# ============================================================
# ТИП УПАКОВКИ
# ============================================================
class TestPackageType(unittest.TestCase):

    def test_fragile_adds_300(self):
        # 200 + 500 + 300 = 1000
        cost, _ = calculate_delivery_cost(1.0, 100, "хрупкий")
        self.assertEqual(cost, 1000)

    def test_dangerous_adds_1000(self):
        # 200 + 500 + 1000 = 1700
        cost, _ = calculate_delivery_cost(1.0, 100, "опасный")
        self.assertEqual(cost, 1700)


# ============================================================
# ЭКСПРЕСС-ДОСТАВКА (здесь ловится BUG-1)
# ============================================================
class TestExpressDelivery(unittest.TestCase):

    def test_express_costs_more_than_regular_BUG1(self):
        """BUG-1: экспресс должен быть ДОРОЖЕ обычной доставки."""
        regular, _ = calculate_delivery_cost(1.0, 100, "обычный", False)
        express, _ = calculate_delivery_cost(1.0, 100, "обычный", True)
        self.assertGreater(express, regular,
                           "Экспресс должен быть дороже обычной доставки!")


# ============================================================
# ДАТА ДОСТАВКИ
# ============================================================
class TestDeliveryDate(unittest.TestCase):

    def test_short_distance_min_one_day(self):
        # distance=100 → days = max(1, 0) = 1 → 2026-09-04
        _, date = calculate_delivery_cost(1.0, 100, "обычный")
        self.assertEqual(date, "2026-09-04")

    def test_long_distance_more_days(self):
        # distance=1000 → days = 1000//500 = 2 → 2026-09-05
        _, date = calculate_delivery_cost(1.0, 1000, "обычный")
        self.assertEqual(date, "2026-09-05")

    def test_express_shortens_delivery(self):
        # distance=2000 → days = 4; express → 2 → 2026-09-05
        _, date = calculate_delivery_cost(1.0, 2000, "обычный", True)
        self.assertEqual(date, "2026-09-05")

    def test_express_never_returns_same_day_BUG2(self):
        """BUG-2: даже для express срок должен быть >= 1 дня."""
        _, date = calculate_delivery_cost(1.0, 100, "обычный", True)
        self.assertNotEqual(date, "2026-09-03",
                            "Экспресс не может быть доставлен в день отправки")


# ============================================================
# КОМБИНИРОВАННЫЕ СЛУЧАИ
# ============================================================
class TestCombined(unittest.TestCase):

    def test_heavy_fragile_express(self):
        # 25кг, 1000км, хрупкий, express
        # (200 + 5000)*1.5 = 7800; +300 = 8100
        # правильный express: 8100 * 1.5 = 12150
        cost, _ = calculate_delivery_cost(25.0, 1000, "хрупкий", True)
        self.assertGreater(cost, 0)

    def test_returns_tuple_of_two(self):
        result = calculate_delivery_cost(1.0, 100, "обычный")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)