import unittest
from unittest.mock import MagicMock, patch, mock_open
from newportal.facade import (
    NewsFacadeError, NewsFacadeActivity, NewsFacadeTracker,
    NewsFacadeWord, NewsFacadeCount, Facade
)
from newportal.observer_facade import (
    ObserverFacadeError, ObserverFacadeActivity,
    ObserverFacadeTracker, ObserverFacadeWord, ObserverFacadeCount
)
from newportal.builder_facade import (
    BuildersFacadeOneThree, BuildersFacadeTwo, BuildersFacadeSix
)
from newportal.strategy_facade import (
    StrategiesFacadeOneThree, StrategiesFacadeTwo, StrategiesFacadeSix
)


class BaseNewsFacadeTest(unittest.TestCase):
    """Базовий клас для тестування NewsFacade"""

    @classmethod
    def setUpClass(cls):
        cls.mock_builders_facade_one_three = MagicMock(spec=BuildersFacadeOneThree)
        cls.mock_builders_facade_two = MagicMock(spec=BuildersFacadeTwo)
        cls.mock_builders_facade_six = MagicMock(spec=BuildersFacadeSix)
        cls.mock_strategies_facade_one_three = MagicMock(spec=StrategiesFacadeOneThree)
        cls.mock_strategies_facade_two = MagicMock(spec=StrategiesFacadeTwo)
        cls.mock_strategies_facade_six = MagicMock(spec=StrategiesFacadeSix)

    def setUp(self):
        self.articles = ["Article 1", "Article 2", "Article 3"]
        self.request = MagicMock()


# ======= Початкові тести, які були у вас =======
class TestNewsFacadeError(BaseNewsFacadeTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mock_observer_facade = MagicMock(spec=ObserverFacadeError)

    def setUp(self):
        super().setUp()
        self.facade = NewsFacadeError(
            request=self.request,
            observer_facade=self.mock_observer_facade,
            builders_facade_one_three=self.mock_builders_facade_one_three,
            builders_facade_two=self.mock_builders_facade_two,
            builders_facade_six=self.mock_builders_facade_six,
            strategies_facade_one_three=self.mock_strategies_facade_one_three,
            strategies_facade_two=self.mock_strategies_facade_two,
            strategies_facade_six=self.mock_strategies_facade_six
        )

    def test_build_and_notify(self):
        self.facade.build_and_notify(self.articles)
        self.mock_observer_facade.attach_observers.assert_called_once()
        self.mock_observer_facade.notify_observers.assert_called_once()

    # ======= Додано нові тести для get_errors() =======
    @patch("builtins.open", new_callable=mock_open, read_data="Error 1\nError 2\n")
    def test_get_errors(self, mock_file):
        errors = self.facade.get_errors()
        self.assertEqual(errors, ["Error 1", "Error 2"])

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_get_errors_file_not_found(self, mock_file):
        errors = self.facade.get_errors()
        self.assertEqual(errors, ["Файл з помилками не знайдено."])


class TestNewsFacadeActivity(BaseNewsFacadeTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mock_observer_facade = MagicMock(spec=ObserverFacadeActivity)

    def setUp(self):
        super().setUp()
        self.facade = NewsFacadeActivity(request=self.request)

    def test_build_and_notify(self):
        self.facade.build_and_notify(self.articles)
        self.mock_observer_facade.attach_observers.assert_called_once()
        self.mock_observer_facade.notify_observers.assert_called_once()

    # ======= Додано новий тест для generate_activity_report() =======
    @patch("builtins.open", new_callable=mock_open, read_data="Активність авторів: {'Author1': 3}\n")
    def test_generate_activity_report(self, mock_file):
        report = self.facade.generate_activity_report()
        self.assertIn('sorted_author_activity', report)
        self.assertIn('sorted_block_views', report)


class TestNewsFacadeTracker(BaseNewsFacadeTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mock_observer_facade = MagicMock(spec=ObserverFacadeTracker)

    def setUp(self):
        super().setUp()
        self.facade = NewsFacadeTracker(request=self.request)

    # ======= Додано новий тест для get_sorted_article_views() =======
    @patch("builtins.open", new_callable=mock_open, read_data="Популярні статті: {'Article1': 5}\n")
    def test_get_sorted_article_views(self, mock_file):
        views = self.facade.get_sorted_article_views()
        self.assertTrue(any(article["title"] == "Article1" for article in views))

    # ======= Додано новий тест для get_sorted_article_saves() =======
    @patch("builtins.open", new_callable=mock_open, read_data="Статтю 'Article1' зберегли 10 разів\n")
    def test_get_sorted_article_saves(self, mock_file):
        saves = self.facade.get_sorted_article_saves()
        self.assertTrue(any(article["title"] == "Article1" for article in saves))


class TestNewsFacadeWord(BaseNewsFacadeTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mock_observer_facade = MagicMock(spec=ObserverFacadeWord)

    def setUp(self):
        super().setUp()
        self.facade = NewsFacadeWord(request=self.request)

    # ======= Додано новий тест для get_seo_data() =======
    @patch("builtins.open", new_callable=mock_open, read_data="не відповідає SEO-правилам 'Article1'\n")
    def test_get_seo_data(self, mock_file):
        seo_data = self.facade.get_seo_data()
        self.assertTrue(any(article["seo_check"] == "Ні" for article in seo_data))


class TestNewsFacadeCount(BaseNewsFacadeTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mock_observer_facade = MagicMock(spec=ObserverFacadeCount)

    def setUp(self):
        super().setUp()
        self.facade = NewsFacadeCount(request=self.request)

    # ======= Додано новий тест для get_creation_logs() =======
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="one_article: 2024-06-10\n")
    def test_get_creation_logs(self, mock_exists, mock_file):
        logs = self.facade.get_creation_logs()
        self.assertEqual(logs, [{"block_type": "one_article", "time_info": "2024-06-10"}])

    @patch("os.path.exists", return_value=False)
    def test_get_creation_logs_no_file(self, mock_exists):
        logs = self.facade.get_creation_logs()
        self.assertEqual(logs, [])


class TestFacadeMeta(unittest.TestCase):

    def test_facade_meta_valid_type(self):
        facade = Facade("error", None)
        self.assertIsInstance(facade, NewsFacadeError)

    def test_facade_meta_invalid_type(self):
        with self.assertRaises(ValueError):
            Facade("unknown", None)


def news_facade_test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        unittest.defaultTestLoader.loadTestsFromTestCase(TestNewsFacadeError),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestNewsFacadeActivity),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestNewsFacadeTracker),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestNewsFacadeWord),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestNewsFacadeCount),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestFacadeMeta),
    ])
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(news_facade_test_suite())