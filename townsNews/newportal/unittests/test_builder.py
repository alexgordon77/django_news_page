import unittest
from unittest.mock import MagicMock, patch
from newportal.builder import (
    OneArticleBlockBuilder,
    TwoArticlesBlockBuilder,
    ThreeArticlesBlockBuilder,
    SixArticlesBlockBuilder,
    NewsBlockBuilder
)
from newportal.observer import NewsBlockSubject, Observer


class MockNewsBlockBuilder(NewsBlockBuilder):
    """Фіктивний клас для тестування абстрактного NewsBlockBuilder"""
    def build_block(self, articles):
        pass  # Порожня реалізація, щоб не було помилки


class TestNewsBlockBuilder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n[SETUP] Тестування NewsBlockBuilder")

    def setUp(self):
        """Перед кожним тестом створюємо мок для NewsBlockSubject"""
        self.builder = MockNewsBlockBuilder()
        self.builder.subject = MagicMock(spec=NewsBlockSubject)

    def test_attach_observer(self):
        observer = MagicMock(spec=Observer)
        self.builder.attach_observer(observer)
        self.builder.subject.attach.assert_called_once_with(observer)

    def test_notify_observers(self):
        self.builder.notify_observers()
        self.builder.subject.notify.assert_called_once()

    def test_get_block(self):
        self.assertEqual(self.builder.get_block(), {})


class TestOneArticleBlockBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = OneArticleBlockBuilder()

    def test_build_block_with_articles(self):
        articles = ["Article 1", "Article 2", "Article 3"]
        with patch("random.choice", return_value="Article 1"):
            self.builder.build_block(articles)

        self.assertEqual(self.builder.get_block(), {"one_article_block": "Article 1"})
        self.assertNotIn("Article 1", articles)

    def test_build_block_with_empty_list(self):
        articles = []
        self.builder.build_block(articles)
        self.assertEqual(self.builder.get_block(), {})


class TestTwoArticlesBlockBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = TwoArticlesBlockBuilder()

    def test_build_block_with_enough_articles(self):
        articles = ["Article 1", "Article 2", "Article 3"]
        with patch("random.sample", return_value=["Article 1", "Article 2"]):
            self.builder.build_block(articles)

        self.assertEqual(self.builder.get_block(), {"two_articles_block": ["Article 1", "Article 2"]})
        self.assertNotIn("Article 1", articles)
        self.assertNotIn("Article 2", articles)

    def test_build_block_with_not_enough_articles(self):
        articles = ["Article 1"]
        self.builder.build_block(articles)
        self.assertEqual(self.builder.get_block(), {})


class TestThreeArticlesBlockBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = ThreeArticlesBlockBuilder()

    def test_build_block_with_enough_articles(self):
        articles = ["Article 1", "Article 2", "Article 3", "Article 4"]
        with patch("random.sample", return_value=["Article 1", "Article 2", "Article 3"]):
            self.builder.build_block(articles)

        self.assertEqual(self.builder.get_block(), {"three_articles_block": ["Article 1", "Article 2", "Article 3"]})
        self.assertNotIn("Article 1", articles)
        self.assertNotIn("Article 2", articles)
        self.assertNotIn("Article 3", articles)

    def test_build_block_with_few_articles(self):
        articles = ["Article 1", "Article 2"]
        self.builder.build_block(articles)
        self.assertEqual(self.builder.get_block(), {})


class TestSixArticlesBlockBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = SixArticlesBlockBuilder()

    def test_build_block_with_enough_articles(self):
        articles = ["Article 1", "Article 2", "Article 3", "Article 4", "Article 5", "Article 6", "Article 7"]
        with patch("random.sample", return_value=["Article 1", "Article 2", "Article 3", "Article 4", "Article 5", "Article 6"]):
            self.builder.build_block(articles)

        self.assertEqual(self.builder.get_block()["six_articles_block"], ["Article 1", "Article 2", "Article 3"])
        self.assertEqual(self.builder.get_block()["six_articles_block2"], ["Article 4", "Article 5", "Article 6"])
        self.assertNotIn("Article 1", articles)

    def test_build_block_with_three_articles(self):
        articles = ["Article 1", "Article 2", "Article 3"]
        with patch("random.sample", return_value=["Article 1", "Article 2", "Article 3"]):
            self.builder.build_block(articles)

        self.assertEqual(self.builder.get_block()["six_articles_block"], ["Article 1", "Article 2", "Article 3"])
        self.assertNotIn("six_articles_block2", self.builder.get_block())

    def test_build_block_with_few_articles(self):
        articles = ["Article 1", "Article 2"]
        self.builder.build_block(articles)
        self.assertEqual(self.builder.get_block(), {})

    def test_select_articles(self):
        articles = ["Article 1", "Article 2", "Article 3", "Article 4", "Article 5"]
        selected = self.builder._select_articles(articles, 3)
        self.assertEqual(len(selected), 3)
        self.assertTrue(all(article in articles for article in selected))


if __name__ == "__main__":
    unittest.main()