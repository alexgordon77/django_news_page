import unittest
from django.utils import timezone
from django.contrib.auth.models import User
from newportal.models import (
    Author, Tag, Article, Comment, SavedArticle,
    SiteSettings, UserBan, SelectedFacade, ProhibitedWord
)


class BaseModelTest(unittest.TestCase):
    """Базовий клас для ініціалізації об'єктів у тестах моделей"""

    @classmethod
    def setUpClass(cls):
        """Створюємо тестові об'єкти перед запуском усіх тестів"""
        cls.author = Author.objects.create(name="Test Author")
        cls.tag = Tag.objects.create(name="Test Tag")
        cls.user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")
        cls.article = Article.objects.create(
            title="Test Article",
            article_text="Тестовий контент",
            author=cls.author,
            date_of_publication=timezone.now().date()
        )
        cls.article.tags.add(cls.tag)

    @classmethod
    def tearDownClass(cls):
        """Видаляємо всі тестові дані після завершення тестів"""
        cls.article.delete()
        cls.author.delete()
        cls.tag.delete()
        cls.user.delete()


class TestAuthorModel(BaseModelTest):

    def test_create_author(self):
        """Перевіряємо створення автора"""
        author = Author.objects.create(name="New Author")
        self.assertEqual(str(author), "New Author")


class TestTagModel(BaseModelTest):

    def test_create_tag(self):
        """Перевіряємо створення тега"""
        tag = Tag.objects.create(name="Django")
        self.assertEqual(str(tag), "Django")


class TestArticleModel(BaseModelTest):

    def test_create_article(self):
        """Перевіряємо створення статті"""
        self.assertEqual(str(self.article), "Test Article")
        self.assertIn(self.tag, self.article.tags.all())

    def test_get_absolute_url(self):
        """Перевіряємо коректність get_absolute_url()"""
        expected_url = f"/articles/{self.article.id}/"
        self.assertTrue(self.article.get_absolute_url().endswith(expected_url))


class TestCommentModel(BaseModelTest):

    def test_create_comment(self):
        """Перевіряємо створення коментаря"""
        comment = Comment.objects.create(article=self.article, user=self.user, text="Тестовий коментар")
        self.assertEqual(str(comment), f'Коментар від {self.user.username} до {self.article.title}')


class TestSavedArticleModel(BaseModelTest):

    def test_create_saved_article(self):
        """Перевіряємо збереження статті користувачем"""
        saved_article = SavedArticle.objects.create(user=self.user, article=self.article)
        self.assertEqual(str(saved_article), f"{self.user.username} зберіг \"{self.article.title}\"")


class TestSiteSettingsModel(unittest.TestCase):

    def test_create_site_settings(self):
        """Перевіряємо створення налаштувань сайту"""
        settings = SiteSettings.objects.create(font_color="#FF5733", background_color="#123456", font_size=18)
        self.assertEqual(str(settings), "Site Settings")
        self.assertEqual(settings.font_size, 18)


class TestUserBanModel(BaseModelTest):

    def test_user_ban(self):
        """Перевіряємо, чи працює система бану"""
        ban_end_time = timezone.now() + timezone.timedelta(days=3)
        user_ban = UserBan.objects.create(user=self.user, ban_end=ban_end_time)
        self.assertTrue(user_ban.is_banned())


class TestSelectedFacadeModel(unittest.TestCase):

    def setUp(self):
        """Перед кожним тестом видаляємо попередні об'єкти SelectedFacade"""
        SelectedFacade.objects.all().delete()

    def test_create_selected_facade(self):
        """Перевіряємо створення об'єкта фасаду"""
        selected_facade = SelectedFacade.objects.create(selected_facade="activity")
        self.assertEqual(selected_facade.selected_facade, "activity")


class TestProhibitedWordModel(unittest.TestCase):

    def setUp(self):
        """Перед кожним тестом очищаємо всі записи ProhibitedWord"""
        ProhibitedWord.objects.all().delete()

    def test_create_prohibited_word(self):
        """Перевіряємо створення забороненого слова"""
        prohibited_word = ProhibitedWord.objects.create(word="заборонене")
        self.assertEqual(str(prohibited_word), "заборонене")

    def tearDown(self):
        """Видаляємо створене заборонене слово після кожного тесту"""
        ProhibitedWord.objects.filter(word="заборонене").delete()


def models_test_suite():
    """Об'єднання всіх тестів у TestSuite"""
    suite = unittest.TestSuite()
    suite.addTests([
        unittest.defaultTestLoader.loadTestsFromTestCase(TestAuthorModel),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestTagModel),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestArticleModel),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestCommentModel),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestSavedArticleModel),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestSiteSettingsModel),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestUserBanModel),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestSelectedFacadeModel),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestProhibitedWordModel),
    ])
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(models_test_suite())
