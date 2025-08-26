import unittest
from unittest.mock import MagicMock
from newportal.strategy import (
    OneArticleSelectionStrategy, TwoArticlesSelectionStrategy,
    ThreeArticlesSelectionStrategy, SixArticlesSelectionStrategy,
    NewsBlockDirector
)
from newportal.builder import (
    OneArticleBlockBuilder, TwoArticlesBlockBuilder,
    ThreeArticlesBlockBuilder, SixArticlesBlockBuilder
)


class BaseStrategyTest(unittest.TestCase):
    """Базовий клас для тестування стратегій"""

    @classmethod
    def setUpClass(cls):
        """Створюємо моки для `BlockBuilder` перед всіма тестами"""
        cls.mock_one_article_builder = MagicMock(spec=OneArticleBlockBuilder)
        cls.mock_two_articles_builder = MagicMock(spec=TwoArticlesBlockBuilder)
        cls.mock_three_articles_builder = MagicMock(spec=ThreeArticlesBlockBuilder)
        cls.mock_six_articles_builder = MagicMock(spec=SixArticlesBlockBuilder)

        cls.mock_articles = ["Article 1", "Article 2", "Article 3", "Article 4", "Article 5", "Article 6"]

    def tearDown(self):
        """Очищуємо всі моки після кожного тесту"""
        self.mock_one_article_builder.reset_mock()
        self.mock_two_articles_builder.reset_mock()
        self.mock_three_articles_builder.reset_mock()
        self.mock_six_articles_builder.reset_mock()


class TestOneArticleSelectionStrategy(BaseStrategyTest):
    """Тести для `OneArticleSelectionStrategy`"""

    def test_build_block(self):
        """Перевіряємо, чи `OneArticleSelectionStrategy` створює правильний блок"""
        strategy = OneArticleSelectionStrategy()
        strategy.build_block = MagicMock(return_value=self.mock_one_article_builder)

        block = strategy.build_block(self.mock_articles[:1])
        strategy.build_block.assert_called_once_with(self.mock_articles[:1])
        self.assertEqual(block, self.mock_one_article_builder)


class TestTwoArticlesSelectionStrategy(BaseStrategyTest):
    """Тести для `TwoArticlesSelectionStrategy`"""

    def test_build_block(self):
        """Перевіряємо, чи `TwoArticlesSelectionStrategy` створює правильний блок"""
        strategy = TwoArticlesSelectionStrategy()
        strategy.build_block = MagicMock(return_value=self.mock_two_articles_builder)

        block = strategy.build_block(self.mock_articles[:2])
        strategy.build_block.assert_called_once_with(self.mock_articles[:2])
        self.assertEqual(block, self.mock_two_articles_builder)


class TestThreeArticlesSelectionStrategy(BaseStrategyTest):
    """Тести для `ThreeArticlesSelectionStrategy`"""

    def test_build_block(self):
        """Перевіряємо, чи `ThreeArticlesSelectionStrategy` створює правильний блок"""
        strategy = ThreeArticlesSelectionStrategy()
        strategy.build_block = MagicMock(return_value=self.mock_three_articles_builder)

        block = strategy.build_block(self.mock_articles[:3])
        strategy.build_block.assert_called_once_with(self.mock_articles[:3])
        self.assertEqual(block, self.mock_three_articles_builder)


class TestSixArticlesSelectionStrategy(BaseStrategyTest):
    """Тести для `SixArticlesSelectionStrategy`"""

    def test_build_block(self):
        """Перевіряємо, чи `SixArticlesSelectionStrategy` створює правильний блок"""
        strategy = SixArticlesSelectionStrategy()
        strategy.build_block = MagicMock(return_value=self.mock_six_articles_builder)

        block = strategy.build_block(self.mock_articles[:6])
        strategy.build_block.assert_called_once_with(self.mock_articles[:6])
        self.assertEqual(block, self.mock_six_articles_builder)


class TestNewsBlockDirector(BaseStrategyTest):
    """Тести для `NewsBlockDirector`"""

    def test_set_strategy_and_construct_block(self):
        """Перевіряємо, чи `NewsBlockDirector` встановлює стратегію і викликає `build_block`"""
        director = NewsBlockDirector()
        mock_strategy = MagicMock()
        director.set_strategy(mock_strategy)

        director.construct_block(self.mock_articles)
        mock_strategy.build_block.assert_called_once_with(self.mock_articles)

    def test_construct_block_without_strategy(self):
        """Перевіряємо, чи `NewsBlockDirector` піднімає виняток, якщо стратегія не встановлена"""
        director = NewsBlockDirector()
        with self.assertRaises(Exception) as context:
            director.construct_block(self.mock_articles)

        self.assertEqual(str(context.exception), "Стратегію не встановлено. Будь ласка, встановіть стратегію перед створенням блоку.")


def strategy_test_suite():
    """Об'єднання всіх тестів у TestSuite"""
    suite = unittest.TestSuite()
    suite.addTests([
        unittest.defaultTestLoader.loadTestsFromTestCase(TestOneArticleSelectionStrategy),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestTwoArticlesSelectionStrategy),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestThreeArticlesSelectionStrategy),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestSixArticlesSelectionStrategy),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestNewsBlockDirector),
    ])
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(strategy_test_suite())