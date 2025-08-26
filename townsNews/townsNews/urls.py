"""
URL configuration for townsNews project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from newportal import views
from newportal.forms import CustomLoginForm

admin.site.index_template = "admin/index.html"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('errors/', views.error_list_view, name='error_list'),
    path('activity/authors/', views.author_activity, name='author_activity'),
    path('activity/blocks/', views.most_viewed_blocks, name='most_viewed_blocks'),
    path('tracker/popular-views/', views.popular_articles_views, name='popular_articles_views'),
    path('tracker/popular-saves/', views.popular_articles_saves, name='popular_articles_saves'),
    path('word/prohibited-words/', views.prohibited_words_report, name='prohibited_words_report'),
    path('word/seo-titles/', views.seo_titles_report, name='seo_titles_report'),
    path('word/tags/', views.tags_report, name='tags_report'),
    path('count/updates', views.news_updates, name='news-updates'),
    path('count/time', views.news_time, name='news-time'),
    path('', views.index, name='index'),  # Головна сторінка
    path('articles/', views.article_list, name='article-list'),  # Список статей
    path('articles/<int:pk>/', views.article_detail, name='article-detail'),  # Деталі статті
    path('articles/<int:pk>/save/', views.save_for_later, name='save-for-later'),  # Збереження статті
    path('articles/<int:pk>/comment/', views.add_comment, name='add-comment'),  # Додавання коментаря
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html',
                                                authentication_form=CustomLoginForm
                                                ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('saved/', views.saved_articles, name='saved-articles'),
    path('saved/<int:pk>/remove/', views.remove_from_saved, name='remove-from-saved'),
    path('settings/', views.edit_user_site_settings, name='edit-user-site-settings'),
    path('statistics/', views.article_statistics, name='article-statistics'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete-comment'),
    path('articles/create/', views.create_article, name='create-article'),
    path('articles/<int:pk>/edit/', views.edit_article, name='edit-article'),
    path('articles/<int:pk>/delete/', views.delete_article, name='delete-article'),
    path('add/', views.create_article, name='article-add'),
    path('profile/', views.edit_profile, name='edit-profile'),
    path('users/', views.manage_users, name='user-management'),
    path('users/add/', views.add_user, name='add-user'),
    path('users/<int:user_id>/ban/', views.ban_user, name='ban-user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete-user'),
    path('api/articles/', views.articles_api, name='articles_api'),
    path('how-listen/', views.how_listn, name='how-listen'),
    path('comment-rules/', views.comment_rules, name='comment-rules'),
    path('about-us/', views.about_us, name='about-us'),
    path('our-codex/', views.our_codex, name='our-codex'),
    path('legal-aspects/', views.legal_aspects, name='legal-aspects'),
    path('feedback/', views.feedback, name='feedback'),
    path('api/weather/', views.get_weather, name='get-weather'),
    path('api/currency_rates/', views.get_currency_rates, name='get-currency-rates'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


