import ast
from collections import Counter
from datetime import datetime
from django.contrib import messages
import requests
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.template.loader import render_to_string
from newportal.facade import Facade, NewsFacadeError, NewsFacadeActivity, NewsFacadeWord, NewsFacadeCount
from newportal.forms import CommentForm, UserRegistrationForm, ArticleForm, BanUserForm, AddUserForm, \
    EditProfileForm, UserSiteSettingsForm
from newportal.models import Author, Article, Tag, SavedArticle, Comment, SelectedFacade, ProhibitedWord, \
    UserSiteSettings


def index(request):
    selected_facade = SelectedFacade.objects.first()
    facade_type = selected_facade.selected_facade if selected_facade else "error"

    all_articles = list(
        Article.objects.select_related('author').prefetch_related('tags')
            .annotate(
            num_comments=Count('comments'),
            num_saves=Count('savedarticle')
        )
    )

    if not all_articles:
        return HttpResponse("Немає статей для відображення")

    try:
        facade = Facade(facade_type, request)
    except ValueError as e:
        return HttpResponse(str(e))

    context = facade.build_and_notify(all_articles)

    return render(request, "index.html", context)


def articles_api(request):
    articles = Article.objects.values('id', 'title', 'author__name', 'date_of_publication', 'views_count')
    return JsonResponse(list(articles), safe=False)


# Error Report
def error_list_view(request):
    news_facade_error = NewsFacadeError(request)
    errors = news_facade_error.get_errors()
    cleaned_errors = news_facade_error.clean_errors(errors)
    developer_message = "Якщо не можете вирішити помилку, зверніться до розробника."

    context = {
        'errors': cleaned_errors,
        'developer_message': developer_message,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('admin/error/error_list.html', context, request=request)
        return JsonResponse({'html': html_content})

    return render(request, 'admin/error/error_list.html', context)


# Author Activity
def author_activity(request):
    news_facade_activity = NewsFacadeActivity(request)
    report_data = news_facade_activity.generate_activity_report()

    context = {
        'sorted_author_activity': report_data['sorted_author_activity'],
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('admin/activity/author_activity.html', context, request=request)
        return JsonResponse({'html': html_content})
    return render(request, 'admin/activity/author_activity.html', context)


# Most Viewed Blocks
def most_viewed_blocks(request):
    news_facade_activity = NewsFacadeActivity(request)
    report_data = news_facade_activity.generate_activity_report()

    context = {
        'sorted_block_views': report_data['sorted_block_views'],
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('admin/activity/activity_block.html', context, request=request)
        return JsonResponse({'html': html_content})

    return render(request, 'admin/activity/activity_block.html', context)


# Popular Articles by Views
def popular_articles_views(request):
    article_views = Counter()
    try:
        with open('popular_articles.log', 'r') as file:
            for line in file:
                if "Популярні статті:" in line:
                    data = line.split("Популярні статті:")[-1].strip()
                    views_data = ast.literal_eval(data)
                    article_views.update(views_data)
    except FileNotFoundError:
        article_views = {}  # 🟢 Робимо пустий словник замість рядка

    sorted_article_views = sorted(article_views.items(), key=lambda x: x[1], reverse=True)
    article_views_with_titles = []

    for article_id, views in sorted_article_views:
        if not isinstance(article_id, int):  # 🟢 Перевіряємо, чи це число
            continue  # Пропускаємо некоректні значення

        try:
            article = Article.objects.get(id=article_id)
            article_views_with_titles.append((article.title, views))
        except Article.DoesNotExist:
            article_views_with_titles.append((f"ID {article_id}", views))

    context = {
        'sorted_article_views': article_views_with_titles,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('admin/tracker/popular_articles_views.html', context, request=request)
        return JsonResponse({'html': html_content})

    return render(request, 'admin/tracker/popular_articles_views.html', context)


# Popular Articles by Saves
def popular_articles_saves(request):
    article_saves = Counter()
    try:
        with open('article_saves.log', 'r') as file:
            for line in file:
                if "Статтю" in line and "зберегли" in line:
                    title = line.split("'")[1]
                    saves = int(line.split()[-2])
                    article_saves[title] += saves
    except FileNotFoundError:
        article_saves = {"Файл 'article_saves.log' не знайдено": 0}

    sorted_article_saves = sorted(article_saves.items(), key=lambda x: x[1], reverse=True)

    context = {
        'sorted_article_saves': sorted_article_saves,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('admin/tracker/popular_articles_saves.html', context, request=request)
        return JsonResponse({'html': html_content})

    return render(request, 'admin/tracker/popular_articles_saves.html', context)


# Prohibited Words
def prohibited_words_report(request):
    import json

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_word = data.get("new_word", "").strip()
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Невірний формат JSON'}, status=400)

        if new_word:
            word_obj, created = ProhibitedWord.objects.get_or_create(word=new_word)
            if not created:
                return JsonResponse({'status': 'exists', 'message': f'Слово "{new_word}" вже існує в списку!'})

            # Оновлений список слів і статей
            updated_words = list(ProhibitedWord.objects.values_list('word', flat=True))
            updated_articles = get_prohibited_words_data(updated_words)

            return JsonResponse(
                {'status': 'success', 'prohibited_words': updated_words, 'prohibited_words_data': updated_articles})

    elif request.method == "DELETE":
        try:
            body = json.loads(request.body)
            word_to_delete = body.get("word", "").strip()
            if not word_to_delete:
                return JsonResponse({"status": "error", "message": "Слово не передано"}, status=400)
            word_obj = ProhibitedWord.objects.filter(word=word_to_delete).first()
            if word_obj:
                word_obj.delete()
                updated_words = list(ProhibitedWord.objects.values_list('word', flat=True))
                updated_articles = get_prohibited_words_data(updated_words)

                return JsonResponse(
                    {"status": "success", "prohibited_words": updated_words, "prohibited_words_data": updated_articles})
            else:
                return JsonResponse({"status": "error", "message": f'Слово "{word_to_delete}" не знайдено!'},
                                    status=404)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Некоректний формат JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # Отримання списку заборонених слів і статей
    prohibited_words = list(ProhibitedWord.objects.values_list('word', flat=True))
    prohibited_words_data = get_prohibited_words_data(prohibited_words)

    context = {
        'prohibited_words': prohibited_words,
        'prohibited_words_data': prohibited_words_data,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('admin/word/prohibited_words_report.html', context=context)
        return JsonResponse({'html': html_content, 'prohibited_words': prohibited_words,
                             'prohibited_words_data': prohibited_words_data})

    return render(request, 'admin/word/prohibited_words_report.html', context)


# Функція для отримання оновлених статей із забороненими словами
def get_prohibited_words_data(prohibited_words):
    articles = Article.objects.all()
    return [
        {
            'id': article.id,
            'title': article.title,
            'words': ", ".join(
                [word for word in prohibited_words if word in article.article_text]
            ),
        }
        for article in articles if any(word in article.article_text for word in prohibited_words)
    ]


# Tags Report
def tags_report(request):
    articles = Article.objects.all()
    news_facade = NewsFacadeWord(request)
    context = news_facade.build_and_notify(articles)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('admin/word/tags_report.html', context, request=request)
        return JsonResponse({'html': html_content})

    return render(request, 'admin/word/tags_report.html', context)


# SEO Titles Report
def seo_titles_report(request):
    articles = Article.objects.all()
    news_facade = NewsFacadeWord(request)
    context = news_facade.build_and_notify(articles)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('admin/word/seo_titles_report.html', context, request=request)
        return JsonResponse({'html': html_content})

    return render(request, 'admin/word/seo_titles_report.html', context)


# News Updates
def news_updates(request):
    facade = NewsFacadeCount(request)
    context = {
        "updates": facade.get_updates(),
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('admin/count/updates_report.html', context, request=request)
        return JsonResponse({'html': html_content})

    return render(request, 'admin/count/updates_report.html', context)


# News Creation Times
def news_time(request):
    facade = NewsFacadeCount(request)
    context = {
        "creation_logs": facade.get_creation_logs(),
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string('admin/count/block_creation_times.html', context, request=request)
        return JsonResponse({'html': html_content})

    return render(request, 'admin/count/block_creation_times.html', context)


@login_required
def article_list(request):
    articles = Article.objects.all()
    articles = articles.annotate(
        num_comments=Count('comments'),
        num_saves=Count('savedarticle')
    )
    authors = Author.objects.all()
    tags = Tag.objects.all()

    # Сортування за параметрами
    sort_by = request.GET.get('sort', 'date')
    if sort_by == 'author':
        articles = articles.order_by('author__name')
    elif sort_by == 'tags':
        articles = articles.order_by('tags__name')
    elif sort_by == 'views':
        articles = articles.order_by('-views_count')  # Сортування за переглядами
    elif sort_by == 'comments':
        articles = articles.order_by('-num_comments')  # Сортування за коментарями
    elif sort_by == 'saves':
        articles = articles.order_by('-num_saves')  # Сортування за збереженнями
    else:  # Сортування за датою
        articles = articles.order_by('-date_of_publication')

    # Фільтр за автором
    author_id = request.GET.get('author')
    if author_id:
        articles = articles.filter(author_id=author_id)

    # Фільтр за тегом
    tag_id = request.GET.get('tag')
    if tag_id:
        articles = articles.filter(tags__id=tag_id)

    # Фільтр за датою
    date_filter = request.GET.get('date')
    if date_filter:
        articles = articles.filter(date_of_publication=date_filter)

    # Пошук за ключовим словом
    query = request.GET.get('query')
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(article_text__icontains=query)
        )

    context = {
        'articles': articles,
        'authors': authors,
        'tags': tags,
    }
    return render(request, "catalog/article_list.html", context)


@login_required
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)

    # Збільшення кількості переглядів
    article.views_count += 1
    article.save()

    comments = article.comments.all()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.user = request.user
            comment.save()
            return redirect('article-detail', pk=pk)
    else:
        form = CommentForm()

    return render(request, 'catalog/article_detail.html', {
        'article': article,
        'comments': comments,
        'form': form,
    })


@login_required
def save_for_later(request, pk):
    article = get_object_or_404(Article, pk=pk)
    saved_article, created = SavedArticle.objects.get_or_create(user=request.user, article=article)
    if created:
        saved_article.save()
    messages.success(request, "Новину збережено!")
    return redirect('article-detail', pk=pk)


@login_required
def saved_articles(request):
    saved_articles = SavedArticle.objects.filter(user=request.user).select_related('article')
    return render(request, 'catalog/saved_articles.html', {'saved_articles': saved_articles})


@login_required
def remove_from_saved(request, pk):
    article = get_object_or_404(Article, pk=pk)
    saved_article = SavedArticle.objects.filter(user=request.user, article=article)
    if saved_article.exists():
        saved_article.delete()
    return redirect('saved-articles')


@login_required
def add_comment(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.user = request.user
            comment.save()
            return redirect('article-detail', pk=pk)
    else:
        form = CommentForm()
    return render(request, 'catalog/article_detail.html', {'form': form, 'article': article})


def is_admin_group(user):
    return user.groups.filter(name='admin-group').exists()


admin_group_required = user_passes_test(is_admin_group)


@login_required
def edit_user_site_settings(request):
    settings, created = UserSiteSettings.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        if 'reset_defaults' in request.POST:
            settings.font_color = UserSiteSettings._meta.get_field('font_color').default
            settings.background_color = UserSiteSettings._meta.get_field('background_color').default
            settings.font_size = UserSiteSettings._meta.get_field('font_size').default
            settings.save()
            return redirect('edit-user-site-settings')
        else:
            form = UserSiteSettingsForm(request.POST, instance=settings)
            if form.is_valid():
                form.save()
                return redirect('edit-user-site-settings')
    else:
        form = UserSiteSettingsForm(instance=settings)
    return render(request, 'catalog/edit_settings.html', {'form': form})


@login_required
@admin_group_required
def article_statistics(request):
    sort = request.GET.get('sort', 'views')

    ordering = {
        'views': '-views_count',
        'comments': '-num_comments',
        'saves': '-num_saves',
    }
    order = ordering.get(sort, '-views_count')

    articles = (
        Article.objects
            .annotate(
            num_comments=Count('comments'),
            num_saves=Count('savedarticle')
        )
            .order_by(order)
    )

    return render(request, 'catalog/article_statistics.html', {
        'articles': articles,
        'current_sort': sort,
    })


@login_required
@user_passes_test(is_admin_group)
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == "POST":
        comment.delete()
        return redirect('article-detail', pk=comment.article.pk)

    return HttpResponseForbidden("Ви не маєте прав для видалення цього коментаря.")


@login_required
@user_passes_test(is_admin_group)
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.date_of_publication = datetime.now()
            article.save()
            form.save_m2m()  # Зберігаємо теги
            return redirect('article-list')
    else:
        form = ArticleForm()

    return render(request, 'catalog/article_form.html', {'form': form, 'is_editing': False})


# Представлення для редагування статті
@login_required
@user_passes_test(is_admin_group)
def edit_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            return redirect('article-detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'catalog/article_form.html', {'form': form, 'is_editing': True})


@login_required
@user_passes_test(is_admin_group)
def delete_article(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if request.method == "POST":
        article.delete()
        return redirect('article-list')

    return render(request, 'catalog/confirm_delete_article.html', {'article': article})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Хешування пароля перед збереженням
            user.save()
            login(request, user)  # Автоматичний вхід після реєстрації
            return redirect('index')  # Перенаправлення на головну сторінку
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
@user_passes_test(is_admin_group)
def manage_users(request):
    users = User.objects.select_related('userban').all()
    add_user_form = AddUserForm()

    if request.method == 'POST':
        if 'ban_user' in request.POST:
            user_id = request.POST.get('user_id')
            period = request.POST.get('period')
            user = get_object_or_404(User, id=user_id)
            if period:
                period_days = int(period)
                from django.utils import timezone
                from datetime import timedelta
                if period_days == 99999:
                    ban_end = timezone.now() + timedelta(days=365 * 100)
                else:
                    ban_end = timezone.now() + timedelta(days=period_days)
                from .models import UserBan
                UserBan.objects.update_or_create(user=user, defaults={'ban_end': ban_end})
                messages.success(request, f'Користувач {user.username} заблокований.')
            else:
                messages.error(request, 'Оберіть термін блокування.')
            return redirect('user-management')

        elif 'unban_user' in request.POST:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            from .models import UserBan
            UserBan.objects.filter(user=user).delete()
            messages.success(request, f'Користувача {user.username} розблоковано.')
            return redirect('user-management')

        elif 'delete_user' in request.POST:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            user.delete()
            messages.success(request, f'Користувач {user.username} видалений.')
            return redirect('user-management')

        elif 'add_user' in request.POST:
            add_user_form = AddUserForm(request.POST)
            if add_user_form.is_valid():
                add_user_form.save()
                messages.success(request, 'Новий користувач успішно створений.')
                return redirect('user-management')

    return render(request, 'catalog/manage_users.html', {
        'users': users,
        'add_user_form': add_user_form
    })


@login_required
@user_passes_test(is_admin_group)
def add_user(request):
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f'Користувач "{user.username}" створений успішно.')
            return redirect('user-management')
    else:
        form = AddUserForm()

    return render(request, 'catalog/add_users.html', {
        'form': form,
    })


@login_required
@user_passes_test(is_admin_group)
def ban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = BanUserForm(request.POST)
        if form.is_valid():
            form.apply_ban(user)
            messages.success(request, f'Користувач {user.username} заблокований.')
            return redirect('user-management')
    else:
        form = BanUserForm()

    return render(request, 'catalog/manage_users.html', {'form': form, 'user': user})


@login_required
@user_passes_test(is_admin_group)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f'Користувач {user.username} видалений.')
        return redirect('user-management')
    return render(request, 'catalog/manage_users.html', {'user': user})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile_form = EditProfileForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
        if 'save_profile' in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Дані профілю оновлені.')
                return redirect('edit-profile')
        elif 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Пароль успішно змінено.')
                return redirect('edit-profile')
    else:
        profile_form = EditProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    return render(request, 'catalog/edit_profile.html', {
        'profile_form': profile_form,
        'password_form': password_form
    })


def get_weather(request):
    api_key = '8bedf0a0f13c9adb19d19f366ad96f9f'

    lat = request.GET.get('lat')
    lon = request.GET.get('lon')

    if lat and lon:
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=ua'
    else:
        url = f'https://api.openweathermap.org/data/2.5/weather?q=Kyiv&appid={api_key}&units=metric&lang=ua'

    try:
        response = requests.get(url)
        data = response.json()

        weather = {
            'temp': round(data['main']['temp']),
            'icon': data['weather'][0]['icon'],
            'description': data['weather'][0]['description'].capitalize()
        }
        return JsonResponse(weather)
    except Exception as e:
        return JsonResponse({'error': 'Не вдалося завантажити погоду'}, status=500)


def get_currency_rates(request):
    try:
        response = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json")
        response.raise_for_status()
        data = response.json()

        usd = next((item for item in data if item['cc'] == 'USD'), None)
        eur = next((item for item in data if item['cc'] == 'EUR'), None)

        return JsonResponse({
            'usd': {
                'buy': round(usd['rate'], 2),
                'sell': round(usd['rate'] + 0.5, 2)  # умовна націнка для демонстрації
            },
            'eur': {
                'buy': round(eur['rate'], 2),
                'sell': round(eur['rate'] + 0.5, 2)
            }
        })
    except Exception as e:
        return JsonResponse({'error': 'Не вдалося отримати курси валют'}, status=500)


# посилання в футері
def how_listn(request):
    return render(request, 'footer/how_listen.html')


def comment_rules(request):
    return render(request, 'footer/comment_rules.html')


def about_us(request):
    return render(request, 'footer/about_us.html')


def our_codex(request):
    return render(request, 'footer/our_codex.html')


def legal_aspects(request):
    return render(request, 'footer/legal_aspects.html')


def feedback(request):
    return render(request, 'footer/feedback.html')
