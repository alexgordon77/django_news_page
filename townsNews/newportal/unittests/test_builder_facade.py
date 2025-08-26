import unittest
from unittest.mock import MagicMock, patch
from newportal.builder import (
    OneArticleBlockBuilder,
    ThreeArticlesBlockBuilder,
    TwoArticlesBlockBuilder,
    SixArticlesBlockBuilder,
)
from newportal.builder_facade import (
    BuildersFacadeOneThree,
    BuildersFacadeTwo,
    BuildersFacadeSix
)


class TestBuildersFacadeOneThree(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Створюємо загальні моки для всіх тестів"""
        cls.mock_one_article_block = MagicMock(spec=OneArticleBlockBuilder)
        cls.mock_three_articles_block = MagicMock(spec=ThreeArticlesBlockBuilder)

    def setUp(self):
        """Перед кожним тестом створюємо новий екземпляр фасаду"""
        self.facade = BuildersFacadeOneThree(
            request=None,
            one_article_block=self.mock_one_article_block,
            three_articles_block=self.mock_three_articles_block
        )
        self.articles = ["Article 1", "Article 2", "Article 3"]

    def test_build_one_article_block(self):
        """Перевіряємо, чи викликається build_block() для one_article_block"""
        self.facade.build_one_article_block(self.articles)
        self.mock_one_article_block.build_block.assert_called_once_with(self.articles)
        self.mock_one_article_block.get_block.assert_called_once()

    def test_build_three_articles_block(self):
        """Перевіряємо, чи викликається build_block() для three_articles_block"""
        self.facade.build_three_articles_block(self.articles)
        self.mock_three_articles_block.build_block.assert_called_once_with(self.articles)
        self.mock_three_articles_block.get_block.assert_called_once()

    def tearDown(self):
        """Очищуємо виклики моків після кожного тесту"""
        self.mock_one_article_block.reset_mock()
        self.mock_three_articles_block.reset_mock()

    @classmethod
    def tearDownClass(cls):
        """Очищуємо моки після виконання всіх тестів"""
        del cls.mock_one_article_block
        del cls.mock_three_articles_block


class TestBuildersFacadeTwo(unittest.TestCase):

    def setUp(self):
        self.mock_two_articles_block = MagicMock(spec=TwoArticlesBlockBuilder)
        self.facade = BuildersFacadeTwo(request=None, two_articles_block=self.mock_two_articles_block)
        self.articles = ["Article 1", "Article 2", "Article 3"]

    def test_build_two_articles_block(self):
        """Перевіряємо, чи викликається build_block() для two_articles_block"""
        self.facade.build_two_articles_block(self.articles)
        self.mock_two_articles_block.build_block.assert_called_once_with(self.articles)
        self.mock_two_articles_block.get_block.assert_called_once()

    def tearDown(self):
        """Очищуємо виклики моків"""
        self.mock_two_articles_block.reset_mock()


class TestBuildersFacadeSix(unittest.TestCase):

    def setUp(self):
        self.mock_six_articles_block = MagicMock(spec=SixArticlesBlockBuilder)
        self.facade = BuildersFacadeSix(request=None, six_articles_block=self.mock_six_articles_block)
        self.articles = ["Article 1", "Article 2", "Article 3", "Article 4", "Article 5", "Article 6"]

    def test_build_six_articles_block(self):
        """Перевіряємо, чи викликається build_block() для six_articles_block"""
        self.facade.build_six_articles_block(self.articles)
        self.mock_six_articles_block.build_block.assert_called_once_with(self.articles)
        self.mock_six_articles_block.get_block.assert_called_once()

    def tearDown(self):
        """Очищуємо виклики моків"""
        self.mock_six_articles_block.reset_mock()


def builders_facade_test_suite():
    """Об'єднання всіх тестів у TestSuite"""
    suite = unittest.TestSuite()
    suite.addTests([
        unittest.defaultTestLoader.loadTestsFromTestCase(TestBuildersFacadeOneThree),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestBuildersFacadeTwo),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestBuildersFacadeSix),
    ])
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(builders_facade_test_suite())