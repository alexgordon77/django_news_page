import unittest
from unittest.mock import patch, MagicMock, mock_open
from django.db.models import Q
from unittest.mock import patch, MagicMock
from newportal.models import Article, Comment, Tag
from newportal.forms import CommentForm
from django.http import JsonResponse, HttpResponse
import json
from django.contrib.messages.storage.fallback import FallbackStorage
from newportal.forms import UserRegistrationForm, BanUserForm, AddUserForm, ArticleForm
from django.test import RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from newportal.models import ProhibitedWord
from newportal.views import (
    index, articles_api, error_list_view, author_activity, most_viewed_blocks,
    popular_articles_views, popular_articles_saves, prohibited_words_report,
    tags_report, seo_titles_report, news_updates, news_time, article_list,
    article_detail, save_for_later, saved_articles, remove_from_saved,
    add_comment, register, edit_site_settings, article_statistics,
    delete_comment, create_article, edit_article, delete_article,
    manage_users, ban_user, delete_user
)
from newportal.views import (
    how_listn, comment_rules, about_us, our_codex, legal_aspects, feedback
)


class TestViews(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Налаштування тестового середовища"""
        cls.mock_request = MagicMock()
        cls.mock_request.headers = {}

    def test_index_view_success(self):
        """Тест головної сторінки, коли є статті"""
        with patch('newportal.views.Facade') as mock_facade, \
                patch('newportal.models.Article.objects.select_related') as mock_articles:
            mock_articles.return_value.prefetch_related.return_value.annotate.return_value = [MagicMock()]
            mock_facade.return_value.build_and_notify.return_value = {'articles': [MagicMock()]}

            response = index(self.mock_request)
            self.assertEqual(response.status_code, 200)

    def test_articles_api(self):
        """Тест API статей"""
        with patch('newportal.models.Article.objects.values') as mock_articles:
            mock_articles.return_value = [{'id': 1, 'title': 'Test Article'}]

            response = articles_api(self.mock_request)
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response, JsonResponse)

            data = json.loads(response.content)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['title'], 'Test Article')

    @patch('newportal.views.NewsFacadeError')
    def test_error_list_view(self, mock_facade):
        """Тест сторінки помилок"""
        mock_facade.return_value.get_errors.return_value = ['Error 1', 'Error 2']
        mock_facade.return_value.clean_errors.return_value = ['Cleaned Error 1', 'Cleaned Error 2']

        response = error_list_view(self.mock_request)
        self.assertEqual(response.status_code, 200)

    @patch('newportal.views.NewsFacadeActivity')
    def test_author_activity(self, mock_facade):
        """Тест активності авторів"""
        mock_facade.return_value.generate_activity_report.return_value = {
            'sorted_author_activity': [('Author 1', 10)]
        }

        response = author_activity(self.mock_request)
        self.assertEqual(response.status_code, 200)

    @patch('newportal.views.NewsFacadeActivity')
    def test_most_viewed_blocks(self, mock_facade):
        """Тест переглядів блоків"""
        mock_facade.return_value.generate_activity_report.return_value = {
            'sorted_block_views': [('Block 1', 15)]
        }

        response = most_viewed_blocks(self.mock_request)
        self.assertEqual(response.status_code, 200)

    @patch('builtins.open', new_callable=mock_open, read_data="Популярні статті: {1: 10, 2: 5}")
    def test_popular_articles_views(self, mock_file):
        """Тест популярних статей за переглядами"""
        response = popular_articles_views(self.mock_request)
        self.assertEqual(response.status_code, 200)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_popular_articles_views_no_file(self, mock_file):
        """Перевіряємо, якщо файл не знайдено"""
        response = popular_articles_views(self.mock_request)
        self.assertEqual(response.status_code, 200)

    @patch("builtins.open", new_callable=mock_open, read_data="Статтю 'Test Article' зберегли 10 разів")
    def test_popular_articles_saves(self, mock_file):
        """Тест популярних статей за збереженнями"""
        response = popular_articles_saves(self.mock_request)
        self.assertEqual(response.status_code, 200)

    @patch("builtins.open", new_callable=mock_open, read_data="Статтю 'Test Article' зберегли invalid_number разів")
    def test_popular_articles_saves_invalid_number(self, mock_file):
        """Тест обробки помилкових числових даних у логах"""
        response = popular_articles_saves(self.mock_request)
        self.assertEqual(response.status_code, 200)

    @patch("newportal.models.ProhibitedWord.objects.values_list", return_value=['badword'])
    @patch("newportal.models.Article.objects.all")
    def test_prohibited_words_report(self, mock_articles, mock_prohibited_words):
        """Тест заборонених слів"""
        mock_articles.return_value = [
            MagicMock(id=1, title="Test Article", article_text="This has badword")
        ]
        response = prohibited_words_report(self.mock_request)
        self.assertEqual(response.status_code, 200)

    @patch("newportal.views.NewsFacadeWord")
    def test_tags_report(self, mock_facade):
        """Тест звіту по тегах"""
        mock_facade.return_value.build_and_notify.return_value = {'tags': ['tag1', 'tag2']}
        response = tags_report(self.mock_request)
        self.assertEqual(response.status_code, 200)

    @patch("newportal.views.NewsFacadeWord")
    def test_seo_titles_report(self, mock_facade):
        """Тест SEO-звіту"""
        mock_facade.return_value.build_and_notify.return_value = {'seo_titles': ['SEO Title 1']}
        response = seo_titles_report(self.mock_request)
        self.assertEqual(response.status_code, 200)

    @patch("newportal.views.NewsFacadeCount")
    def test_news_updates(self, mock_facade):
        """Тест оновлень новин"""
        mock_facade.return_value.get_updates.return_value = ["Update 1", "Update 2"]
        response = news_updates(self.mock_request)
        self.assertEqual(response.status_code, 200)

    @patch("newportal.views.NewsFacadeCount")
    def test_news_time(self, mock_facade):
        """Тест часу створення новин"""
        mock_facade.return_value.get_creation_logs.return_value = ["Log 1", "Log 2"]
        response = news_time(self.mock_request)
        self.assertEqual(response.status_code, 200)

    @patch("newportal.models.Article.objects.annotate")
    def test_article_list(self, mock_articles):
        """Тест списку статей"""
        mock_articles.return_value = [MagicMock(title="Test Article")]
        response = article_list(self.mock_request)
        self.assertEqual(response.status_code, 200)

    @patch("newportal.models.Article.objects.get")
    def test_article_detail(self, mock_article):
        """Тест перегляду статті"""
        mock_article.return_value = MagicMock(title="Test Article", views_count=5)
        response = article_detail(self.mock_request, pk=1)
        self.assertEqual(response.status_code, 200)

    @patch("newportal.models.SavedArticle.objects.get_or_create")
    @patch("newportal.models.Article.objects.get")
    def test_save_for_later(self, mock_get_article, mock_get_or_create):
        """Тест збереження статті для перегляду пізніше"""
        mock_get_article.return_value = MagicMock(title="Test Article")
        mock_get_or_create.return_value = (MagicMock(), True)

        response = save_for_later(self.mock_request, pk=1)
        self.assertEqual(response.status_code, 302)  # Перенаправлення після збереження

    @patch("newportal.models.SavedArticle.objects.filter")
    def test_saved_articles(self, mock_saved_articles):
        """Тест перегляду списку збережених статей"""
        mock_saved_articles.return_value.select_related.return_value = [MagicMock(title="Saved Article")]
        response = saved_articles(self.mock_request)
        self.assertEqual(response.status_code, 200)

    @patch("newportal.models.SavedArticle.objects.filter")
    @patch("newportal.models.Article.objects.get")
    def test_remove_from_saved(self, mock_get_article, mock_saved_articles):
        """Тест видалення статті зі збережених"""
        mock_get_article.return_value = MagicMock(title="Test Article")
        mock_saved_articles.return_value.exists.return_value = True
        mock_saved_articles.return_value.delete.return_value = None

        response = remove_from_saved(self.mock_request, pk=1)
        self.assertEqual(response.status_code, 302)  # Перенаправлення після видалення

    @patch("newportal.models.CommentForm")
    @patch("newportal.models.Article.objects.get")
    def test_add_comment(self, mock_get_article, mock_comment_form):
        """Тест додавання коментаря"""
        mock_get_article.return_value = MagicMock(title="Test Article")
        mock_form_instance = MagicMock()
        mock_comment_form.return_value = mock_form_instance
        mock_form_instance.is_valid.return_value = True
        mock_form_instance.save.return_value = MagicMock()

        self.mock_request.method = "POST"
        self.mock_request.POST = {"text": "New comment"}

        response = add_comment(self.mock_request, pk=1)
        self.assertEqual(response.status_code, 302)  # Перенаправлення після додавання

    @patch("newportal.forms.UserRegistrationForm")
    @patch("newportal.models.User.objects.create_user")
    def test_register(self, mock_create_user, mock_registration_form):
        """Тест реєстрації нового користувача"""
        mock_form_instance = MagicMock()
        mock_registration_form.return_value = mock_form_instance
        mock_form_instance.is_valid.return_value = True
        mock_form_instance.save.return_value = MagicMock()

        self.mock_request.method = "POST"
        self.mock_request.POST = {
            "username": "newuser",
            "password1": "password123",
            "password2": "password123",
            "email": "newuser@example.com"
        }

        response = register(self.mock_request)
        self.assertEqual(response.status_code, 302)  # Перенаправлення після реєстрації

    @patch("newportal.models.SiteSettings.objects.first")
    @patch("newportal.forms.SiteSettingsForm")
    def test_edit_site_settings(self, mock_settings_form, mock_get_settings):
        """Тест редагування налаштувань сайту"""
        mock_get_settings.return_value = MagicMock(font_color="#FFFFFF")

        mock_form_instance = MagicMock()
        mock_settings_form.return_value = mock_form_instance
        mock_form_instance.is_valid.return_value = True
        mock_form_instance.save.return_value = None

        self.mock_request.method = "POST"
        self.mock_request.POST = {"font_color": "#000000"}

        response = edit_site_settings(self.mock_request)
        self.assertEqual(response.status_code, 302)  # Перенаправлення після збереження

    @patch("newportal.models.Article.objects.annotate")
    def test_article_statistics(self, mock_articles):
        """Тест статистики статей"""
        mock_articles.return_value.order_by.return_value = [MagicMock(title="Popular Article")]

        response = article_statistics(self.mock_request)
        self.assertEqual(response.status_code, 200)

    @patch("newportal.models.Comment.objects.get")
    def test_delete_comment(self, mock_get_comment):
        """Тест видалення коментаря"""
        mock_comment = MagicMock(article=MagicMock(pk=1))
        mock_get_comment.return_value = mock_comment

        self.mock_request.method = "POST"

        response = delete_comment(self.mock_request, comment_id=1)
        self.assertEqual(response.status_code, 302)  # Перенаправлення після видалення
        mock_comment.delete.assert_called_once()

    @patch("newportal.forms.ArticleForm")
    def test_create_article(self, mock_article_form):
        """Тест створення статті"""
        mock_form_instance = MagicMock()
        mock_article_form.return_value = mock_form_instance
        mock_form_instance.is_valid.return_value = True
        mock_form_instance.save.return_value = MagicMock()

        self.mock_request.method = "POST"
        self.mock_request.POST = {
            "title": "New Article",
            "article_text": "This is a test article",
            "author": 1
        }

        response = create_article(self.mock_request)
        self.assertEqual(response.status_code, 302)  # Перенаправлення після створення

    @patch("newportal.models.Article.objects.get")
    @patch("newportal.forms.ArticleForm")
    def test_edit_article(self, mock_article_form, mock_get_article):
        """Тест редагування статті"""
        mock_article = MagicMock(pk=1, title="Old Title")
        mock_get_article.return_value = mock_article

        mock_form_instance = MagicMock()
        mock_article_form.return_value = mock_form_instance
        mock_form_instance.is_valid.return_value = True

        self.mock_request.method = "POST"
        self.mock_request.POST = {"title": "Updated Title"}

        response = edit_article(self.mock_request, pk=1)
        self.assertEqual(response.status_code, 302)  # Перенаправлення після редагування
        mock_form_instance.save.assert_called_once()

    @patch("newportal.models.Article.objects.get")
    def test_delete_article(self, mock_get_article):
        """Тест видалення статті"""
        mock_article = MagicMock(pk=1)
        mock_get_article.return_value = mock_article

        self.mock_request.method = "POST"

        response = delete_article(self.mock_request, pk=1)
        self.assertEqual(response.status_code, 302)  # Перенаправлення після видалення
        mock_article.delete.assert_called_once()

    @patch("newportal.models.User.objects.select_related")
    @patch("newportal.forms.BanUserForm")
    @patch("newportal.forms.AddUserForm")
    def test_manage_users(self, mock_add_user_form, mock_ban_user_form, mock_users):
        """Тест сторінки керування користувачами"""
        mock_users.return_value.all.return_value = [MagicMock(username="testuser")]

        mock_ban_form_instance = MagicMock()
        mock_ban_user_form.return_value = mock_ban_form_instance

        mock_add_form_instance = MagicMock()
        mock_add_user_form.return_value = mock_add_form_instance

        response = manage_users(self.mock_request)
        self.assertEqual(response.status_code, 200)

    @patch("newportal.models.User.objects.get")
    @patch("newportal.forms.BanUserForm")
    def test_ban_user(self, mock_ban_user_form, mock_get_user):
        """Тест блокування користувача"""
        mock_user = MagicMock(username="banneduser")
        mock_get_user.return_value = mock_user

        mock_form_instance = MagicMock()
        mock_ban_user_form.return_value = mock_form_instance
        mock_form_instance.is_valid.return_value = True

        self.mock_request.method = "POST"
        self.mock_request.POST = {"reason": "Spamming"}

        response = ban_user(self.mock_request, user_id=1)
        self.assertEqual(response.status_code, 302)  # Перенаправлення після блокування
        mock_form_instance.apply_ban.assert_called_once_with(mock_user)

    @patch("newportal.models.User.objects.get")
    def test_delete_user(self, mock_get_user):
        """Тест видалення користувача"""
        mock_user = MagicMock(username="testuser")
        mock_get_user.return_value = mock_user

        self.mock_request.method = "POST"

        response = delete_user(self.mock_request, user_id=1)
        self.assertEqual(response.status_code, 302)  # Перенаправлення після видалення
        mock_user.delete.assert_called_once()


class ProhibitedWordsTestCase(unittest.TestCase):
    """Тестування додавання та видалення заборонених слів"""

    @classmethod
    def setUpClass(cls):
        cls.mock_request = MagicMock()
        cls.mock_request.headers = {}

    @patch("newportal.models.ProhibitedWord.objects.get_or_create")
    def test_add_prohibited_word_success(self, mock_get_or_create):
        """Тест успішного додавання нового забороненого слова"""
        mock_get_or_create.return_value = (MagicMock(), True)  # `created=True`, слово нове

        self.mock_request.POST = {"new_word": "спам"}
        self.mock_request.method = "POST"

        response = prohibited_words_report(self.mock_request)
        self.assertJSONEqual(response.content, {"status": "success"})

    @patch("newportal.models.ProhibitedWord.objects.get_or_create")
    def test_add_prohibited_word_already_exists(self, mock_get_or_create):
        """Тест спроби додати вже існуюче заборонене слово"""
        mock_get_or_create.return_value = (MagicMock(), False)  # `created=False`, слово вже є

        self.mock_request.POST = {"new_word": "спам"}
        self.mock_request.method = "POST"

        response = prohibited_words_report(self.mock_request)
        self.assertJSONEqual(response.content, {
            "status": "exists",
            "message": 'Слово "спам" вже існує в списку!'
        })

    @patch("newportal.models.ProhibitedWord.objects.get")
    def test_delete_prohibited_word_success(self, mock_get):
        """Тест успішного видалення забороненого слова"""
        mock_word = MagicMock()
        mock_get.return_value = mock_word

        self.mock_request.method = "DELETE"
        self.mock_request.body = json.dumps({"word": "спам"})

        response = prohibited_words_report(self.mock_request)
        self.assertJSONEqual(response.content, {"status": "success"})
        mock_word.delete.assert_called_once()

    @patch("newportal.models.ProhibitedWord.objects.get")
    def test_delete_prohibited_word_not_found(self, mock_get):
        """Тест видалення неіснуючого забороненого слова"""
        mock_get.side_effect = ProhibitedWord.DoesNotExist  # Симуляція помилки

        self.mock_request.method = "DELETE"
        self.mock_request.body = json.dumps({"word": "спам"})

        response = prohibited_words_report(self.mock_request)
        self.assertJSONEqual(response.content, {
            "status": "error",
            "message": 'Слово "спам" не знайдено!'
        })


class ArticleListTestCase(unittest.TestCase):
    """Тести для `article_list`"""

    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()

    def setUp(self):
        """Налаштування тестового користувача"""
        self.user = MagicMock()
        self.user.is_authenticated = True

    @patch("newportal.models.Article.objects.all")
    @patch("newportal.models.Author.objects.all")
    @patch("newportal.models.Tag.objects.all")
    def test_article_list_view(self, mock_tags, mock_authors, mock_articles):
        """Тест базового відображення списку статей"""
        mock_articles.return_value.annotate.return_value.order_by.return_value = [MagicMock(title="Test Article")]
        mock_authors.return_value = [MagicMock(name="Author 1")]
        mock_tags.return_value = [MagicMock(name="Tag 1")]

        request = self.factory.get(reverse("article-list"))
        request.user = self.user
        response = article_list(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Article", response.content.decode())

    @patch("newportal.models.Article.objects.all")
    def test_article_list_sort_by_views(self, mock_articles):
        """Тест сортування за переглядами"""
        mock_articles.return_value.annotate.return_value.order_by.return_value = [MagicMock(title="Popular Article")]

        request = self.factory.get(reverse("article-list"), {"sort": "views"})
        request.user = self.user
        response = article_list(request)

        self.assertEqual(response.status_code, 200)
        mock_articles.return_value.annotate.return_value.order_by.assert_called_with("-views_count")

    @patch("newportal.models.Article.objects.all")
    def test_article_list_sort_by_comments(self, mock_articles):
        """Тест сортування за кількістю коментарів"""
        mock_articles.return_value.annotate.return_value.order_by.return_value = [MagicMock(title="Commented Article")]

        request = self.factory.get(reverse("article-list"), {"sort": "comments"})
        request.user = self.user
        response = article_list(request)

        self.assertEqual(response.status_code, 200)
        mock_articles.return_value.annotate.return_value.order_by.assert_called_with("-num_comments")

    @patch("newportal.models.Article.objects.all")
    def test_article_list_filter_by_author(self, mock_articles):
        """Тест фільтрації статей за автором"""
        mock_articles.return_value.annotate.return_value.filter.return_value = [MagicMock(title="Author Article")]

        request = self.factory.get(reverse("article-list"), {"author": "1"})
        request.user = self.user
        response = article_list(request)

        self.assertEqual(response.status_code, 200)
        mock_articles.return_value.annotate.return_value.filter.assert_called_with(author_id="1")

    @patch("newportal.models.Article.objects.all")
    def test_article_list_filter_by_tag(self, mock_articles):
        """Тест фільтрації статей за тегом"""
        mock_articles.return_value.annotate.return_value.filter.return_value = [MagicMock(title="Tagged Article")]

        request = self.factory.get(reverse("article-list"), {"tag": "2"})
        request.user = self.user
        response = article_list(request)

        self.assertEqual(response.status_code, 200)
        mock_articles.return_value.annotate.return_value.filter.assert_called_with(tags__id="2")

    @patch("newportal.models.Article.objects.all")
    def test_article_list_filter_by_date(self, mock_articles):
        """Тест фільтрації статей за датою"""
        mock_articles.return_value.annotate.return_value.filter.return_value = [MagicMock(title="Dated Article")]

        request = self.factory.get(reverse("article-list"), {"date": "2024-03-01"})
        request.user = self.user
        response = article_list(request)

        self.assertEqual(response.status_code, 200)
        mock_articles.return_value.annotate.return_value.filter.assert_called_with(date_of_publication="2024-03-01")

    @patch("newportal.models.Article.objects.all")
    def test_article_list_search_query(self, mock_articles):
        """Тест пошуку статей за ключовим словом"""
        mock_articles.return_value.annotate.return_value.filter.return_value = [MagicMock(title="Search Article")]

        request = self.factory.get(reverse("article-list"), {"query": "news"})
        request.user = self.user
        response = article_list(request)

        self.assertEqual(response.status_code, 200)
        mock_articles.return_value.annotate.return_value.filter.assert_called_with(
            Q(title__icontains="news") | Q(article_text__icontains="news")
        )


class ArticleDetailTestCase(unittest.TestCase):
    """Тестування `article_detail`."""

    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()

    @patch("newportal.models.Article.objects.get")
    @patch("newportal.models.Comment.objects.all")
    def test_article_detail_view_increment_views(self, mock_comments, mock_get_article):
        """Тест збільшення лічильника переглядів при відкритті сторінки статті."""
        mock_article = MagicMock(spec=Article)
        mock_article.views_count = 5
        mock_article.comments.all.return_value = []
        mock_get_article.return_value = mock_article

        request = self.factory.get(reverse("article-detail", args=[1]))
        response = article_detail(request, pk=1)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_article.views_count, 6)  # Лічильник повинен збільшитися на 1
        mock_article.save.assert_called_once()  # Переконуємося, що `save()` викликано

    @patch("newportal.models.Article.objects.get")
    @patch("newportal.models.CommentForm")
    def test_article_detail_view_add_comment(self, mock_comment_form, mock_get_article):
        """Тест додавання коментаря через `POST`."""
        mock_article = MagicMock(spec=Article)
        mock_get_article.return_value = mock_article

        mock_form_instance = MagicMock(spec=CommentForm)
        mock_comment_form.return_value = mock_form_instance
        mock_form_instance.is_valid.return_value = True
        mock_form_instance.save.return_value = MagicMock(spec=Comment)

        request = self.factory.post(reverse("article-detail", args=[1]), {"text": "Тестовий коментар"})
        request.user = MagicMock()
        response = article_detail(request, pk=1)

        self.assertEqual(response.status_code, 302)  # Перенаправлення після успішного додавання
        mock_form_instance.save.assert_called_once()

    @patch("newportal.models.Article.objects.get")
    @patch("newportal.forms.CommentForm")
    def test_article_detail_view_get_request(self, mock_comment_form, mock_get_article):
        """Тест відображення сторінки `article_detail` при `GET`-запиті."""
        mock_article = MagicMock(spec=Article)
        mock_get_article.return_value = mock_article

        mock_form_instance = MagicMock(spec=CommentForm)
        mock_comment_form.return_value = mock_form_instance

        request = self.factory.get(reverse("article-detail", args=[1]))
        response = article_detail(request, pk=1)

        self.assertEqual(response.status_code, 200)  # Сторінка успішно рендериться
        mock_comment_form.assert_called_once()  # Перевіряємо, що форму створено

    @patch("newportal.models.Article.objects.get")
    @patch("newportal.forms.CommentForm")
    def test_article_detail_view_post_invalid_form(self, mock_comment_form, mock_get_article):
        """Тест `POST`-запиту з невалідною формою."""
        mock_article = MagicMock(spec=Article)
        mock_get_article.return_value = mock_article

        mock_form_instance = MagicMock(spec=CommentForm)
        mock_form_instance.is_valid.return_value = False  # Форма невалідна
        mock_comment_form.return_value = mock_form_instance

        request = self.factory.post(reverse("article-detail", args=[1]), {"text": ""})  # Пустий коментар
        request.user = MagicMock()

        response = article_detail(request, pk=1)

        self.assertEqual(response.status_code, 200)  # Сторінка рендериться з формою
        mock_comment_form.assert_called_once_with(request.POST)


class RegisterViewTestCase(unittest.TestCase):
    """Тестування `register`."""

    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()

    @patch("newportal.forms.UserRegistrationForm")
    @patch("newportal.models.User.objects.create_user")
    @patch("newportal.views.login")
    def test_register_success(self, mock_login, mock_create_user, mock_registration_form):
        """Тест успішної реєстрації користувача."""
        mock_form_instance = MagicMock(spec=UserRegistrationForm)
        mock_registration_form.return_value = mock_form_instance
        mock_form_instance.is_valid.return_value = True  # Форма валідна
        mock_user = MagicMock(spec=User)
        mock_form_instance.save.return_value = mock_user

        request = self.factory.post(reverse("register"), {
            "username": "testuser",
            "password1": "password123",
            "password2": "password123",
            "email": "test@example.com"
        })
        request.user = MagicMock()

        response = register(request)

        self.assertEqual(response.status_code, 302)  # Перенаправлення після успіху
        self.assertEqual(response.url, reverse("index"))  # Редірект на головну
        mock_form_instance.save.assert_called_once()  # Переконуємось, що `save()` викликано
        mock_user.set_password.assert_called_once_with("password123")  # Перевіряємо хешування пароля
        mock_user.save.assert_called_once()  # Переконуємось, що користувач збережений
        mock_login.assert_called_once_with(request, mock_user)  # Перевіряємо автоматичний логін

    @patch("newportal.forms.UserRegistrationForm")
    def test_register_invalid_form(self, mock_registration_form):
        """Тест невдалої реєстрації (форма невалідна)."""
        mock_form_instance = MagicMock(spec=UserRegistrationForm)
        mock_registration_form.return_value = mock_form_instance
        mock_form_instance.is_valid.return_value = False  # Форма не проходить валідацію

        request = self.factory.post(reverse("register"), {
            "username": "testuser",
            "password1": "password123",
            "password2": "wrongpassword"
        })
        request.user = MagicMock()

        response = register(request)

        self.assertEqual(response.status_code, 200)  # Помилки в формі, сторінка повинна рендеритись знову
        mock_form_instance.save.assert_not_called()


class FooterLinksTestCase(unittest.TestCase):
    """Тестування сторінок футера"""

    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()

    def test_how_listn_view(self):
        """Тест сторінки 'Як слухати'"""
        request = self.factory.get(reverse("how-listn"))
        response = how_listn(request)
        self.assertEqual(response.status_code, 200)

    def test_comment_rules_view(self):
        """Тест сторінки 'Правила коментування'"""
        request = self.factory.get(reverse("comment-rules"))
        response = comment_rules(request)
        self.assertEqual(response.status_code, 200)

    def test_about_us_view(self):
        """Тест сторінки 'Про нас'"""
        request = self.factory.get(reverse("about-us"))
        response = about_us(request)
        self.assertEqual(response.status_code, 200)

    def test_our_codex_view(self):
        """Тест сторінки 'Наш кодекс'"""
        request = self.factory.get(reverse("our-codex"))
        response = our_codex(request)
        self.assertEqual(response.status_code, 200)

    def test_legal_aspects_view(self):
        """Тест сторінки 'Юридичні аспекти'"""
        request = self.factory.get(reverse("legal-aspects"))
        response = legal_aspects(request)
        self.assertEqual(response.status_code, 200)

    def test_feedback_view(self):
        """Тест сторінки 'Зворотний зв’язок'"""
        request = self.factory.get(reverse("feedback"))
        response = feedback(request)
        self.assertEqual(response.status_code, 200)


class ManageUsersTestCase(unittest.TestCase):
    """Тести керування користувачами (блокування, видалення, додавання)"""

    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()

    def setUp(self):
        """Налаштування об'єкта `request` з `messages`"""
        self.request = self.factory.post(reverse("user-management"))
        self.request.user = MagicMock()
        self.request.session = {}
        self.request._messages = FallbackStorage(self.request)

    @patch("newportal.models.User.objects.get")
    @patch("newportal.forms.BanUserForm")
    def test_ban_user(self, mock_ban_user_form, mock_get_user):
        """Тест блокування користувача"""
        mock_user = MagicMock(username="banneduser")
        mock_get_user.return_value = mock_user

        mock_form = MagicMock()
        mock_form.is_valid.return_value = True
        mock_ban_user_form.return_value = mock_form

        self.request.POST = {"ban_user": "", "user_id": "1"}

        response = manage_users(self.request)

        self.assertEqual(response.status_code, 302)  # Перенаправлення після блокування
        self.assertEqual(response.url, reverse("user-management"))
        mock_form.apply_ban.assert_called_once_with(mock_user)

    @patch("newportal.models.User.objects.get")
    def test_delete_user(self, mock_get_user):
        """Тест видалення користувача"""
        mock_user = MagicMock(username="testuser")
        mock_get_user.return_value = mock_user

        self.request.POST = {"delete_user": "", "user_id": "1"}

        response = manage_users(self.request)

        self.assertEqual(response.status_code, 302)  # Перенаправлення після видалення
        self.assertEqual(response.url, reverse("user-management"))
        mock_user.delete.assert_called_once()

    @patch("newportal.forms.AddUserForm")
    def test_add_user(self, mock_add_user_form):
        """Тест додавання нового користувача"""
        mock_form = MagicMock()
        mock_form.is_valid.return_value = True
        mock_add_user_form.return_value = mock_form

        self.request.POST = {"add_user": ""}

        response = manage_users(self.request)

        self.assertEqual(response.status_code, 302)  # Перенаправлення після додавання
        self.assertEqual(response.url, reverse("user-management"))
        mock_form.save.assert_called_once()


class ArticleManagementTestCase(unittest.TestCase):
    """Тести для створення, редагування та видалення статті"""

    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()

    def setUp(self):
        """Створюємо тестового користувача"""
        self.user = MagicMock(spec=User)
        self.user.is_authenticated = True

    @patch("newportal.forms.ArticleForm")
    @patch("newportal.models.Article.objects.create")
    def test_create_article_success(self, mock_article_create, mock_article_form):
        """Тест успішного створення статті"""
        mock_form_instance = MagicMock(spec=ArticleForm)
        mock_article_form.return_value = mock_form_instance
        mock_form_instance.is_valid.return_value = True
        mock_article = MagicMock()
        mock_form_instance.save.return_value = mock_article

        request = self.factory.post(reverse("create-article"), {
            "title": "New Article",
            "article_text": "Test content",
            "author": self.user
        })
        request.user = self.user

        response = create_article(request)

        self.assertEqual(response.status_code, 302)  # Перевіряємо редірект
        self.assertEqual(response.url, reverse("article-list"))  # Перевіряємо правильний редірект
        mock_form_instance.save.assert_called_once()  # Переконуємося, що `save()` викликано
        mock_form_instance.save_m2m.assert_called_once()  # Переконуємося, що `save_m2m()` викликано

    @patch("newportal.forms.ArticleForm")
    def test_create_article_invalid_form(self, mock_article_form):
        """Тест невдалої спроби створення статті (невалідна форма)"""
        mock_form_instance = MagicMock(spec=ArticleForm)
        mock_article_form.return_value = mock_form_instance
        mock_form_instance.is_valid.return_value = False

        request = self.factory.post(reverse("create-article"), {})
        request.user = self.user

        response = create_article(request)

        self.assertEqual(response.status_code, 200)  # Перевіряємо, що сторінка рендериться знову
        mock_article_form.assert_called_once()  # Переконуємося, що форму викликано
        mock_form_instance.save.assert_not_called()  # `save()` не має викликатися

    @patch("newportal.models.Article.objects.get")
    @patch("newportal.forms.ArticleForm")
    def test_edit_article_success(self, mock_article_form, mock_get_article):
        """Тест успішного редагування статті"""
        mock_article = MagicMock()
        mock_get_article.return_value = mock_article

        mock_form_instance = MagicMock(spec=ArticleForm)
        mock_article_form.return_value = mock_form_instance
        mock_form_instance.is_valid.return_value = True

        request = self.factory.post(reverse("edit-article", args=[1]), {"title": "Updated Title"})
        request.user = self.user

        response = edit_article(request, pk=1)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("article-detail", args=[1]))
        mock_form_instance.save.assert_called_once()

    @patch("newportal.models.Article.objects.get")
    @patch("newportal.forms.ArticleForm")
    def test_edit_article_invalid_form(self, mock_article_form, mock_get_article):
        """Тест спроби редагування з невалідною формою"""
        mock_article = MagicMock()
        mock_get_article.return_value = mock_article

        mock_form_instance = MagicMock(spec=ArticleForm)
        mock_article_form.return_value = mock_form_instance
        mock_form_instance.is_valid.return_value = False

        request = self.factory.post(reverse("edit-article", args=[1]), {"title": ""})
        request.user = self.user

        response = edit_article(request, pk=1)

        self.assertEqual(response.status_code, 200)  # Форма невалідна — повертаємо сторінку
        mock_form_instance.save.assert_not_called()

    @patch("newportal.models.Article.objects.get")
    def test_delete_article_success(self, mock_get_article):
        """Тест успішного видалення статті"""
        mock_article = MagicMock()
        mock_get_article.return_value = mock_article

        request = self.factory.post(reverse("delete-article", args=[1]))
        request.user = self.user

        response = delete_article(request, pk=1)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("article-list"))
        mock_article.delete.assert_called_once()

    @patch("newportal.models.Article.objects.get")
    def test_delete_article_get_request(self, mock_get_article):
        """Тест GET-запиту на сторінку видалення статті"""
        mock_article = MagicMock()
        mock_get_article.return_value = mock_article

        request = self.factory.get(reverse("delete-article", args=[1]))
        request.user = self.user

        response = delete_article(request, pk=1)

        self.assertEqual(response.status_code, 200)
