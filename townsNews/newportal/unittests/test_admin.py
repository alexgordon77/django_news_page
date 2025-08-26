import unittest
from unittest.mock import patch, MagicMock
from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from django.contrib import messages
from django.urls import reverse
import json
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from newportal.admin import log_admin_action, ArticleAdmin, SelectedFacadeAdmin, CustomAdminSite, SavedArticleAdmin, \
    AuthorAdmin, CommentAdmin, TagAdmin, CustomGroupAdmin, CustomUserAdmin, format_change_message
from newportal.models import Article, SelectedFacade, SavedArticle, Author, Comment, Tag


class LogAdminActionTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Створюємо тестового користувача один раз для всього класу"""
        cls.user = User(id=1, username="admin")

    def setUp(self):
        """Перед кожним тестом створюємо об'єкт статті та запит"""
        self.article = Article(id=1, title="Тестова стаття", article_text="Тестовий контент")
        self.request = MagicMock()
        self.request.user = self.user

    @patch('newportal.admin.LogEntry.objects.log_action')
    def test_log_admin_action_addition(self, mock_log_action):
        """Перевіряємо, що логування додавання працює"""
        log_admin_action(self.request, self.article, ADDITION, "Додано статтю")
        mock_log_action.assert_called_once_with(
            user_id=self.user.pk,
            content_type_id=ContentType.objects.get_for_model(self.article).pk,
            object_id=self.article.pk,
            object_repr=str(self.article),
            action_flag=ADDITION,
            change_message="Додано статтю"
        )


class ArticleAdminTest(unittest.TestCase):
    def setUp(self):
        self.model_admin = ArticleAdmin(model=Article, admin_site=MagicMock())
        self.article = Article(id=1, title="Тестова стаття", article_text="Тестовий контент")
        self.request = MagicMock()
        self.request.user = MagicMock()

    @patch('newportal.admin.log_admin_action')
    @patch('newportal.models.Article.objects.update')
    def test_mark_as_published(self, mock_update, mock_log_admin_action):
        """Перевіряємо, чи оновлюється дата публікації статей"""
        queryset = MagicMock()
        queryset.update.return_value = 2

        self.model_admin.mark_as_published(self.request, queryset)

        mock_update.assert_called_once()
        mock_log_admin_action.assert_called()
        self.request._messages.add.assert_called()

    @patch('newportal.admin.log_admin_action')
    def test_delete_queryset(self, mock_log_admin_action):
        queryset = [self.article]
        self.model_admin.delete_queryset(self.request, queryset)
        mock_log_admin_action.assert_called_once()

    def test_changelist_view(self):
        response = self.model_admin.changelist_view(self.request)
        self.assertEqual(response.status_code, 200)


class SavedArticleAdminTest(unittest.TestCase):
    def setUp(self):
        self.model_admin = SavedArticleAdmin(model=SavedArticle, admin_site=MagicMock())
        self.saved_article = SavedArticle(id=1, user=MagicMock(), article=MagicMock())
        self.request = MagicMock()

    @patch('newportal.admin.log_admin_action')
    def test_save_model(self, mock_log_admin_action):
        self.model_admin.save_model(self.request, self.saved_article, form=None, change=False)
        mock_log_admin_action.assert_called_once()

    @patch('newportal.admin.log_admin_action')
    def test_delete_model(self, mock_log_admin_action):
        self.model_admin.delete_model(self.request, self.saved_article)
        mock_log_admin_action.assert_called_once()

    @patch('newportal.admin.log_admin_action')
    def test_delete_queryset(self, mock_log_admin_action):
        queryset = [self.saved_article]
        self.model_admin.delete_queryset(self.request, queryset)
        mock_log_admin_action.assert_called_once()

    def test_changelist_view(self):
        response = self.model_admin.changelist_view(self.request)
        self.assertEqual(response.status_code, 200)


class AuthorAdminTest(unittest.TestCase):
    def setUp(self):
        self.model_admin = AuthorAdmin(model=Author, admin_site=MagicMock())
        self.author = Author(id=1, name="Автор")
        self.request = MagicMock()

    @patch('newportal.admin.log_admin_action')
    def test_save_model(self, mock_log_admin_action):
        self.model_admin.save_model(self.request, self.author, form=None, change=True)
        mock_log_admin_action.assert_called_once()

    @patch('newportal.admin.log_admin_action')
    def test_delete_model(self, mock_log_admin_action):
        self.model_admin.delete_model(self.request, self.author)
        mock_log_admin_action.assert_called_once()

    @patch('newportal.admin.log_admin_action')
    def test_delete_queryset(self, mock_log_admin_action):
        queryset = [self.author]
        self.model_admin.delete_queryset(self.request, queryset)
        mock_log_admin_action.assert_called_once()

    def test_changelist_view(self):
        response = self.model_admin.changelist_view(self.request)
        self.assertEqual(response.status_code, 200)


class CommentAdminTest(unittest.TestCase):
    def setUp(self):
        self.model_admin = CommentAdmin(model=Comment, admin_site=MagicMock())
        self.comment = Comment(id=1, user=MagicMock(), article=MagicMock(), text="Тестовий коментар")
        self.request = MagicMock()

    @patch('newportal.admin.log_admin_action')
    def test_save_model(self, mock_log_admin_action):
        self.model_admin.save_model(self.request, self.comment, form=None, change=False)
        mock_log_admin_action.assert_called_once()

    @patch('newportal.admin.log_admin_action')
    def test_delete_model(self, mock_log_admin_action):
        self.model_admin.delete_model(self.request, self.comment)
        mock_log_admin_action.assert_called_once()

    @patch('newportal.admin.log_admin_action')
    def test_delete_queryset(self, mock_log_admin_action):
        queryset = [self.comment]
        self.model_admin.delete_queryset(self.request, queryset)
        mock_log_admin_action.assert_called_once()

    def test_changelist_view(self):
        response = self.model_admin.changelist_view(self.request)
        self.assertEqual(response.status_code, 200)


class TagAdminTest(unittest.TestCase):
    def setUp(self):
        self.model_admin = TagAdmin(model=Tag, admin_site=MagicMock())
        self.tag = Tag(id=1, name="Тестовий тег")
        self.request = MagicMock()

    @patch('newportal.admin.log_admin_action')
    def test_save_model(self, mock_log_admin_action):
        self.model_admin.save_model(self.request, self.tag, form=None, change=True)
        mock_log_admin_action.assert_called_once()

    @patch('newportal.admin.log_admin_action')
    def test_delete_model(self, mock_log_admin_action):
        self.model_admin.delete_model(self.request, self.tag)
        mock_log_admin_action.assert_called_once()

    @patch('newportal.admin.log_admin_action')
    def test_delete_queryset(self, mock_log_admin_action):
        queryset = [self.tag]
        self.model_admin.delete_queryset(self.request, queryset)
        mock_log_admin_action.assert_called_once()

    def test_changelist_view(self):
        response = self.model_admin.changelist_view(self.request)
        self.assertEqual(response.status_code, 200)


class CustomGroupAdminTest(unittest.TestCase):
    def setUp(self):
        self.model_admin = CustomGroupAdmin(model=Group, admin_site=MagicMock())
        self.group = Group(id=1, name="Test Group")
        self.request = MagicMock()

    @patch('newportal.admin.log_admin_action')
    def test_save_model(self, mock_log_admin_action):
        self.model_admin.save_model(self.request, self.group, form=None, change=True)
        mock_log_admin_action.assert_called_once()

    @patch('newportal.admin.log_admin_action')
    def test_delete_model(self, mock_log_admin_action):
        self.model_admin.delete_model(self.request, self.group)
        mock_log_admin_action.assert_called_once()


class CustomUserAdminTest(unittest.TestCase):
    def setUp(self):
        self.model_admin = CustomUserAdmin(model=User, admin_site=MagicMock())
        self.user = User(id=1, username="TestUser")
        self.request = MagicMock()

    @patch('newportal.admin.log_admin_action')
    def test_save_model(self, mock_log_admin_action):
        self.model_admin.save_model(self.request, self.user, form=None, change=True)
        mock_log_admin_action.assert_called_once()

    @patch('newportal.admin.log_admin_action')
    def test_delete_model(self, mock_log_admin_action):
        self.model_admin.delete_model(self.request, self.user)
        mock_log_admin_action.assert_called_once()


class SelectedFacadeAdminTest(unittest.TestCase):

    def setUp(self):
        """Перед кожним тестом створюємо адміністраторський клас"""
        self.admin_instance = SelectedFacadeAdmin(model=SelectedFacade, admin_site=MagicMock())
        self.request = MagicMock()

    @patch('newportal.admin.SelectedFacade.objects.first')
    def test_changelist_view_redirects(self, mock_first):
        """Перевіряємо, що changelist_view перенаправляє на зміну першого об'єкта"""
        mock_first.return_value = MagicMock(id=1)
        response = self.admin_instance.changelist_view(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('admin:newportal_selectedfacade_change', args=[1])))

    @patch('newportal.admin.SelectedFacade.objects.first')
    @patch('newportal.admin.admin.ModelAdmin.message_user')
    def test_changelist_view_no_objects(self, mock_message_user, mock_first):
        """Перевіряємо повідомлення, якщо об'єктів немає"""
        mock_first.return_value = None

        self.request.GET.get.side_effect = lambda key, default=None: default

        response = self.admin_instance.changelist_view(self.request)

        mock_message_user.assert_called_once_with(self.request, "Немає об'єктів для перегляду.", level=messages.WARNING)
        self.assertEqual(response.status_code, 200)


class CustomAdminSiteTest(unittest.TestCase):

    def setUp(self):
        """Перед кожним тестом створюємо кастомний адміністративний сайт"""
        self.admin_site = CustomAdminSite()
        self.request = MagicMock()

    @patch('newportal.admin.LogEntry.objects.all')
    def test_clear_logs(self, mock_log_entries):
        """Перевіряємо, чи викликається очищення логів"""
        mock_log_entries.return_value.delete = MagicMock()
        response = self.admin_site.clear_logs(self.request)
        mock_log_entries.return_value.delete.assert_called_once()
        self.assertEqual(response.status_code, 302)  # Перенаправлення на головну сторінку адмінки


class FormatChangeMessageTest(unittest.TestCase):
    def test_empty_message(self):
        self.assertEqual(format_change_message(""), "Без повідомлення")

    def test_valid_json_message(self):
        message = json.dumps([{"changed": {"fields": ["title", "content"]}}])
        self.assertEqual(format_change_message(message), "Змінено поля: title, content.")

    def test_invalid_json_message(self):
        self.assertEqual(format_change_message("Тестове повідомлення"), "Тестове повідомлення")


def admin_test_suite():
    """Об'єднання всіх тестів у TestSuite"""
    suite = unittest.TestSuite()
    suite.addTests([
        unittest.defaultTestLoader.loadTestsFromTestCase(LogAdminActionTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(ArticleAdminTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(SelectedFacadeAdminTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(CustomAdminSiteTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(LogAdminActionTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(SavedArticleAdminTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(AuthorAdminTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(CommentAdminTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(TagAdminTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(CustomGroupAdminTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(CustomUserAdminTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(FormatChangeMessageTest),
    ])
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(admin_test_suite())
