import unittest
from django.urls import reverse, resolve
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from newportal import views


class TestUrls(unittest.TestCase):
    """Тестування всіх маршрутів у `urls.py`"""

    @classmethod
    def setUpClass(cls):
        """Перевіряємо, чи `settings` коректно налаштовані перед тестуванням"""
        super().setUpClass()
        try:
            _ = settings.INSTALLED_APPS  # Перевіряємо, чи Django налаштований
        except ImproperlyConfigured:
            raise unittest.SkipTest("Django не налаштований правильно")

    def test_admin_url(self):
        """Перевіряємо `/admin/`"""
        url = reverse("admin:index")
        self.assertEqual(resolve(url).app_name, "admin")

    def test_index_url(self):
        """Перевіряємо `/` -> `index`"""
        url = reverse("index")
        self.assertEqual(resolve(url).func, views.index)

    def test_articles_urls(self):
        """Перевіряємо `articles/`"""
        self.assertEqual(resolve(reverse("article-list")).func, views.article_list)
        self.assertEqual(resolve(reverse("article-detail", args=[1])).func, views.article_detail)
        self.assertEqual(resolve(reverse("create-article")).func, views.create_article)
        self.assertEqual(resolve(reverse("edit-article", args=[1])).func, views.edit_article)
        self.assertEqual(resolve(reverse("delete-article", args=[1])).func, views.delete_article)

    def test_save_comment_urls(self):
        """Перевіряємо `articles/<int:pk>/save/` і `articles/<int:pk>/comment/`"""
        self.assertEqual(resolve(reverse("save-for-later", args=[1])).func, views.save_for_later)
        self.assertEqual(resolve(reverse("add-comment", args=[1])).func, views.add_comment)

    def test_auth_urls(self):
        """Перевіряємо маршрути авторизації та реєстрації"""
        self.assertEqual(resolve(reverse("login")).func.view_class, LoginView)
        self.assertEqual(resolve(reverse("logout")).func.view_class, LogoutView)
        self.assertEqual(resolve(reverse("register")).func, views.register)

    def test_saved_articles_urls(self):
        """Перевіряємо `saved/`"""
        self.assertEqual(resolve(reverse("saved-articles")).func, views.saved_articles)
        self.assertEqual(resolve(reverse("remove-from-saved", args=[1])).func, views.remove_from_saved)

    def test_admin_views_urls(self):
        """Перевіряємо `/settings/` і `/statistics/`"""
        self.assertEqual(resolve(reverse("edit-site-settings")).func, views.edit_site_settings)
        self.assertEqual(resolve(reverse("article-statistics")).func, views.article_statistics)

    def test_comment_delete_url(self):
        """Перевіряємо `comment/<int:comment_id>/delete/`"""
        self.assertEqual(resolve(reverse("delete-comment", args=[1])).func, views.delete_comment)

    def test_user_management_urls(self):
        """Перевіряємо `users/`"""
        self.assertEqual(resolve(reverse("user-management")).func, views.manage_users)
        self.assertEqual(resolve(reverse("ban-user", args=[1])).func, views.ban_user)
        self.assertEqual(resolve(reverse("delete-user", args=[1])).func, views.delete_user)

    def test_errors_urls(self):
        """Перевіряємо `errors/`"""
        self.assertEqual(resolve(reverse("error_list")).func, views.error_list_view)

    def test_activity_urls(self):
        """Перевіряємо `/activity/authors/` і `/activity/blocks/`"""
        self.assertEqual(resolve(reverse("author_activity")).func, views.author_activity)
        self.assertEqual(resolve(reverse("most_viewed_blocks")).func, views.most_viewed_blocks)

    def test_tracker_urls(self):
        """Перевіряємо `/tracker/popular-views/` і `/tracker/popular-saves/`"""
        self.assertEqual(resolve(reverse("popular_articles_views")).func, views.popular_articles_views)
        self.assertEqual(resolve(reverse("popular_articles_saves")).func, views.popular_articles_saves)

    def test_word_management_urls(self):
        """Перевіряємо `/word/` маршрути"""
        self.assertEqual(resolve(reverse("prohibited_words_report")).func, views.prohibited_words_report)
        self.assertEqual(resolve(reverse("seo_titles_report")).func, views.seo_titles_report)
        self.assertEqual(resolve(reverse("tags_report")).func, views.tags_report)

    def test_news_count_urls(self):
        """Перевіряємо `/count/` маршрути"""
        self.assertEqual(resolve(reverse("news-updates")).func, views.news_updates)
        self.assertEqual(resolve(reverse("news-time")).func, views.news_time)

    def test_api_articles_url(self):
        """Перевіряємо `/api/articles/`"""
        self.assertEqual(resolve(reverse("articles_api")).func, views.articles_api)

    def test_footer_urls(self):
        """Перевіряємо `/about-us/`, `/our-codex/` тощо"""
        self.assertEqual(resolve(reverse("how-listen")).func, views.how_listn)
        self.assertEqual(resolve(reverse("comment-rules")).func, views.comment_rules)
        self.assertEqual(resolve(reverse("about-us")).func, views.about_us)
        self.assertEqual(resolve(reverse("our-codex")).func, views.our_codex)
        self.assertEqual(resolve(reverse("legal-aspects")).func, views.legal_aspects)
        self.assertEqual(resolve(reverse("feedback")).func, views.feedback)


def urls_test_suite():
    """Об'єднання всіх тестів у `TestSuite`"""
    suite = unittest.TestSuite()
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestUrls))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(urls_test_suite())