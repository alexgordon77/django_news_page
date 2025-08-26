import unittest
from unittest.mock import MagicMock
from newportal.observer_facade import (
    ObserverFacadeError, ObserverFacadeActivity, ObserverFacadeTracker,
    ObserverFacadeWord, ObserverFacadeCount
)
from newportal.observer import (
    ObserverTxtError, ObserverJsonError, ObserverUserActivity, ObserverAuthorActivity,
    ObserverPopularArticleTracker, ObserverArticleSaveTracker, ObserverNewTag,
    ObserverProhibitedWords, ObserverSeoTitleChecker, ObserverArticleCount, ObserverBlockCreationTime
)
from newportal.builder import NewsBlockBuilder


class BaseObserverFacadeTest(unittest.TestCase):
    """Базовий клас для тестування фасадів Observer"""

    @classmethod
    def setUpClass(cls):
        """Створюємо мокований `NewsBlockBuilder` перед усіма тестами"""
        cls.mock_builder = MagicMock(spec=NewsBlockBuilder)

    def tearDown(self):
        """Очищуємо всі моки після кожного тесту"""
        self.mock_builder.attach_observer.reset_mock()
        self.mock_builder.notify_observers.reset_mock()


class TestObserverFacadeError(BaseObserverFacadeTest):
    """Тести для ObserverFacadeError"""

    def setUp(self):
        """Створюємо екземпляр фасаду перед кожним тестом"""
        self.facade = ObserverFacadeError(builder=self.mock_builder)

    def test_attach_observers(self):
        """Перевіряємо, чи додаються потрібні спостерігачі"""
        self.facade.attach_observers()
        self.assertEqual(len(self.facade.observers), 2)
        self.assertIsInstance(self.facade.observers[0], ObserverTxtError)
        self.assertIsInstance(self.facade.observers[1], ObserverJsonError)

    def test_notify_observers(self):
        """Перевіряємо, чи викликається notify_observers"""
        self.facade.notify_observers()
        self.mock_builder.notify_observers.assert_called_once()


class TestObserverFacadeActivity(BaseObserverFacadeTest):
    """Тести для ObserverFacadeActivity"""

    def setUp(self):
        self.facade = ObserverFacadeActivity(builder=self.mock_builder)

    def test_attach_observers(self):
        self.facade.attach_observers()
        self.assertEqual(len(self.facade.observers), 2)
        self.assertIsInstance(self.facade.observers[0], ObserverUserActivity)
        self.assertIsInstance(self.facade.observers[1], ObserverAuthorActivity)

    def test_notify_observers(self):
        self.facade.notify_observers()
        self.mock_builder.notify_observers.assert_called_once()


class TestObserverFacadeTracker(BaseObserverFacadeTest):
    """Тести для ObserverFacadeTracker"""

    def setUp(self):
        self.facade = ObserverFacadeTracker(builder=self.mock_builder)

    def test_attach_observers(self):
        self.facade.attach_observers()
        self.assertEqual(len(self.facade.observers), 2)
        self.assertIsInstance(self.facade.observers[0], ObserverPopularArticleTracker)
        self.assertIsInstance(self.facade.observers[1], ObserverArticleSaveTracker)

    def test_notify_observers(self):
        self.facade.notify_observers()
        self.mock_builder.notify_observers.assert_called_once()


class TestObserverFacadeWord(BaseObserverFacadeTest):
    """Тести для ObserverFacadeWord"""

    def setUp(self):
        self.facade = ObserverFacadeWord(builder=self.mock_builder)

    def test_attach_observers(self):
        self.facade.attach_observers()
        self.assertEqual(len(self.facade.observers), 3)
        self.assertIsInstance(self.facade.observers[0], ObserverNewTag)
        self.assertIsInstance(self.facade.observers[1], ObserverProhibitedWords)
        self.assertIsInstance(self.facade.observers[2], ObserverSeoTitleChecker)

    def test_notify_observers(self):
        self.facade.notify_observers()
        self.mock_builder.notify_observers.assert_called_once()


class TestObserverFacadeCount(BaseObserverFacadeTest):
    """Тести для ObserverFacadeCount"""

    def setUp(self):
        self.facade = ObserverFacadeCount(builder=self.mock_builder)

    def test_attach_observers(self):
        self.facade.attach_observers()
        self.assertEqual(len(self.facade.observers), 2)
        self.assertIsInstance(self.facade.observers[0], ObserverArticleCount)
        self.assertIsInstance(self.facade.observers[1], ObserverBlockCreationTime)

    def test_notify_observers(self):
        self.facade.notify_observers()
        self.mock_builder.notify_observers.assert_called_once()


def observer_facade_test_suite():
    """Об'єднання всіх тестів у TestSuite"""
    suite = unittest.TestSuite()
    suite.addTests([
        unittest.defaultTestLoader.loadTestsFromTestCase(TestObserverFacadeError),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestObserverFacadeActivity),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestObserverFacadeTracker),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestObserverFacadeWord),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestObserverFacadeCount),
    ])
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(observer_facade_test_suite())