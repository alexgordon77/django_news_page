import unittest
from unittest.mock import MagicMock
from newportal.strategy_facade import (
    StrategiesFacadeOneThree, StrategiesFacadeTwo, StrategiesFacadeSix
)
from newportal.strategy import (
    OneArticleSelectionStrategy, ThreeArticlesSelectionStrategy,
    TwoArticlesSelectionStrategy, SixArticlesSelectionStrategy
)


class BaseStrategyFacadeTest(unittest.TestCase):
    """Базовий клас для тестування фасадів стратегій"""

    @classmethod
    def setUpClass(cls):
        """Створюємо моки для стратегій перед всіма тестами"""
        cls.mock_one_article_strategy = MagicMock(spec=OneArticleSelectionStrategy)
        cls.mock_three_articles_strategy = MagicMock(spec=ThreeArticlesSelectionStrategy)
        cls.mock_two_articles_strategy = MagicMock(spec=TwoArticlesSelectionStrategy)
        cls.mock_six_articles_strategy = MagicMock(spec=SixArticlesSelectionStrategy)

    def tearDown(self):
        """Очищуємо моки після кожного тесту"""
        self.mock_one_article_strategy.reset_mock()
        self.mock_three_articles_strategy.reset_mock()
        self.mock_two_articles_strategy.reset_mock()
        self.mock_six_articles_strategy.reset_mock()


class TestStrategiesFacadeOneThree(BaseStrategyFacadeTest):
    """Тести для `StrategiesFacadeOneThree`"""

    def test_select_one_article_strategy(self):
        """Перевіряємо, чи повертається стратегія `OneArticleSelectionStrategy`"""
        facade = StrategiesFacadeOneThree(one_article_strategy=self.mock_one_article_strategy)
        strategy = facade.select_strategy("one_article")
        self.assertEqual(strategy, self.mock_one_article_strategy)

    def test_select_three_articles_strategy(self):
        """Перевіряємо, чи повертається стратегія `ThreeArticlesSelectionStrategy`"""
        facade = StrategiesFacadeOneThree(three_articles_strategy=self.mock_three_articles_strategy)
        strategy = facade.select_strategy("three_articles")
        self.assertEqual(strategy, self.mock_three_articles_strategy)

    def test_invalid_strategy(self):
        """Перевіряємо, чи виникає помилка для невідомої стратегії"""
        facade = StrategiesFacadeOneThree()
        with self.assertRaises(ValueError) as context:
            facade.select_strategy("invalid_strategy")
        self.assertEqual(str(context.exception), "Невідома стратегія: invalid_strategy")


class TestStrategiesFacadeTwo(BaseStrategyFacadeTest):
    """Тести для `StrategiesFacadeTwo`"""

    def test_select_two_articles_strategy(self):
        """Перевіряємо, чи повертається стратегія `TwoArticlesSelectionStrategy`"""
        facade = StrategiesFacadeTwo(two_articles_strategy=self.mock_two_articles_strategy)
        strategy = facade.select_strategy("two_articles")
        self.assertEqual(strategy, self.mock_two_articles_strategy)

    def test_invalid_strategy(self):
        """Перевіряємо, чи виникає помилка для невідомої стратегії"""
        facade = StrategiesFacadeTwo()
        with self.assertRaises(ValueError) as context:
            facade.select_strategy("invalid_strategy")
        self.assertEqual(str(context.exception), "Невідома стратегія: invalid_strategy")


class TestStrategiesFacadeSix(BaseStrategyFacadeTest):
    """Тести для `StrategiesFacadeSix`"""

    def test_select_six_articles_strategy(self):
        """Перевіряємо, чи повертається стратегія `SixArticlesSelectionStrategy`"""
        facade = StrategiesFacadeSix(six_articles_strategy=self.mock_six_articles_strategy)
        strategy = facade.select_strategy("six_articles")
        self.assertEqual(strategy, self.mock_six_articles_strategy)

    def test_invalid_strategy(self):
        """Перевіряємо, чи виникає помилка для невідомої стратегії"""
        facade = StrategiesFacadeSix()
        with self.assertRaises(ValueError) as context:
            facade.select_strategy("invalid_strategy")
        self.assertEqual(str(context.exception), "Невідома стратегія: invalid_strategy")


def strategy_facade_test_suite():
    """Об'єднання всіх тестів у TestSuite"""
    suite = unittest.TestSuite()
    suite.addTests([
        unittest.defaultTestLoader.loadTestsFromTestCase(TestStrategiesFacadeOneThree),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestStrategiesFacadeTwo),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestStrategiesFacadeSix),
    ])
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(strategy_facade_test_suite())