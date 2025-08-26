import unittest
import json
import os
import time
from unittest.mock import MagicMock, patch
from django.contrib import messages
from newportal.observer import (
    NewsBlockSubject, ObserverTxtError, ObserverJsonError,
    ObserverArticleCount, ObserverBlockCreationTime, ObserverNewTag,
    ObserverProhibitedWords, ObserverUserActivity, ObserverPopularArticleTracker,
    ObserverAuthorActivity, ObserverSeoTitleChecker, ObserverArticleSaveTracker
)
from newportal.models import Tag


class FakeArticle:
    """Фейковий об'єкт статті для тестів."""
    def __init__(self, title, id=1, tags=None, num_saves=0):
        self.title = title
        self.id = id
        self.tags = tags or []
        self.num_saves = num_saves
        self.author = FakeAuthor("Test Author")

    def all(self):
        return self.tags


class FakeAuthor:
    """Фейковий об'єкт автора."""
    def __init__(self, name):
        self.name = name


class BaseObserverTest(unittest.TestCase):
    """Базовий клас для тестів спостерігачів."""

    @classmethod
    def setUpClass(cls):
        """Створення загальних змінних."""
        cls.fake_article = FakeArticle("Test Article", id=1, tags=[Tag(name="News")])
        cls.block_data = {
            "one_article_block": cls.fake_article,
            "two_articles_block": [cls.fake_article, FakeArticle("Another Article", id=2)],
        }
        cls.request_mock = MagicMock()
        cls.subject = NewsBlockSubject(cls.block_data, request=cls.request_mock)

    def tearDown(self):
        """Видалення тестових файлів після кожного тесту."""
        for file in ["errors.txt", "errors.json", "creation_times.txt", "new_tags.log",
                     "prohibited_words.log", "user_activity.log", "popular_articles.log",
                     "author_activity.log", "seo_title_issues.log", "article_saves.log"]:
            if os.path.exists(file):
                os.remove(file)


class TestObserverTxtError(BaseObserverTest):
    """Тести для ObserverTxtError"""

    def test_log_missing_blocks(self):
        observer = ObserverTxtError()
        self.subject.attach(observer)
        self.subject._block.pop("one_article_block", None)
        self.subject.notify()

        with open("errors.txt", "r") as file:
            content = file.read()
        self.assertIn("Відсутній блок", content)


class TestObserverJsonError(BaseObserverTest):
    """Тести для ObserverJsonError"""

    def test_log_missing_blocks(self):
        observer = ObserverJsonError()
        self.subject.attach(observer)
        self.subject._block.pop("one_article_block", None)
        self.subject.notify()

        with open("errors.json", "r") as file:
            content = json.loads(file.readline())
        self.assertIn("Помилки", content["error"])


class TestObserverArticleCount(BaseObserverTest):
    """Тести для ObserverArticleCount"""

    def test_notify_user(self):
        observer = ObserverArticleCount()
        observer.notify_user = MagicMock()
        self.subject.attach(observer)
        self.subject.notify()
        observer.notify_user.assert_called()


class TestObserverBlockCreationTime(BaseObserverTest):
    """Тести для ObserverBlockCreationTime"""

    def test_log_creation_time(self):
        observer = ObserverBlockCreationTime()
        self.subject.attach(observer)
        time.sleep(0.1)
        self.subject.notify()

        with open("creation_times.txt", "r") as file:
            content = file.read()
        self.assertIn(":", content)


class TestObserverNewTag(BaseObserverTest):
    """Тести для ObserverNewTag"""

    def test_detect_new_tags(self):
        """Перевіряємо, чи виявляються нові теги у статтях"""
        observer = ObserverNewTag()
        self.subject.attach(observer)

        # Створюємо новий тег і додаємо його до фейкової статті
        new_tag = Tag(name="НовийТег")
        new_article = FakeArticle("Новий заголовок", id=3, tags=[new_tag])

        # Додаємо нову статтю як об'єкт, а не список
        self.subject._block["one_article_block"] = new_article

        self.subject.notify()

        with open("new_tags.log", "r") as file:
            content = file.read()

        self.assertIn("НовийТег", content)


class TestObserverProhibitedWords(BaseObserverTest):
    """Тести для ObserverProhibitedWords"""

    def test_detect_prohibited_words(self):
        observer = ObserverProhibitedWords(["заборонене"])
        self.subject.attach(observer)
        self.subject.notify()

        if os.path.exists("prohibited_words.log"):
            with open("prohibited_words.log", "r") as file:
                content = file.read()
            self.assertIn("Знайдено заборонені слова", content)


class TestObserverUserActivity(BaseObserverTest):
    """Тести для ObserverUserActivity"""

    def test_log_user_activity(self):
        observer = ObserverUserActivity()
        self.subject.attach(observer)
        self.subject.notify()

        with open("user_activity.log", "r") as file:
            content = file.read()
        self.assertIn("переглянув блок новин", content)


class TestObserverPopularArticleTracker(BaseObserverTest):
    """Тести для ObserverPopularArticleTracker"""

    def test_track_popular_articles(self):
        observer = ObserverPopularArticleTracker()
        self.subject.attach(observer)
        self.subject.notify()

        with open("popular_articles.log", "r") as file:
            content = file.read()
        self.assertIn("Популярні статті", content)


class TestObserverSeoTitleChecker(BaseObserverTest):
    """Тести для ObserverSeoTitleChecker"""

    def test_detect_invalid_titles(self):
        observer = ObserverSeoTitleChecker(min_length=5, max_length=10)
        self.subject.attach(observer)
        self.subject.notify()

        with open("seo_title_issues.log", "r") as file:
            content = file.read()
        self.assertIn("не відповідає SEO-правилам", content)


class TestObserverArticleSaveTracker(BaseObserverTest):
    """Тести для ObserverArticleSaveTracker"""

    def test_log_article_saves(self):
        observer = ObserverArticleSaveTracker()
        self.subject.attach(observer)
        self.subject.notify()

        if os.path.exists("article_saves.log"):
            with open("article_saves.log", "r") as file:
                content = file.read()
            self.assertIn("зберегли", content)


def observer_test_suite():
    """Об'єднання всіх тестів у TestSuite"""
    suite = unittest.TestSuite()
    suite.addTests([
        unittest.defaultTestLoader.loadTestsFromTestCase(TestObserverTxtError),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestObserverJsonError),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestObserverArticleCount),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestObserverBlockCreationTime),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestObserverNewTag),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestObserverProhibitedWords),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestObserverUserActivity),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestObserverPopularArticleTracker),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestObserverSeoTitleChecker),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestObserverArticleSaveTracker),
    ])
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(observer_test_suite())