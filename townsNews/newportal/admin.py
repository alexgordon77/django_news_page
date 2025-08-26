from django.urls import path
from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib import messages
import json
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes.models import ContentType

from newportal import views
from newportal.models import Article, Tag, Author, Comment, SavedArticle, SelectedFacade, ProhibitedWord


# Helper function for logging actions
def log_admin_action(request, obj, action_flag, message):
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=action_flag,
        change_message=message
    )


# ---- Article ----
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date_of_publication', 'display_tag', 'views_count')
    list_filter = ('author', 'date_of_publication', 'tags')
    search_fields = ('title', 'article_text', 'author__name')
    ordering = ('-date_of_publication',)

    actions = ['mark_as_published']

    def mark_as_published(self, request, queryset):
        rows_updated = queryset.update(date_of_publication=timezone.now())
        for article in queryset:
            log_admin_action(request, article, CHANGE, "Стаття опублікована")
        self.message_user(request, f"{rows_updated} статті опубліковано.")

    def save_model(self, request, obj, form, change):
        message = "Змінено статтю" if change else "Додано нову статтю"
        log_admin_action(request, obj, CHANGE if change else ADDITION, message)
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        log_admin_action(request, obj, DELETION, "Видалено статтю")
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            log_admin_action(request, obj, DELETION, "Масове видалення статті")
        super().delete_queryset(request, queryset)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = _("Статті")
        return super().changelist_view(request, extra_context=extra_context)


# ---- Author ----
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)

    def save_model(self, request, obj, form, change):
        message = "Змінено автора" if change else "Додано нового автора"
        log_admin_action(request, obj, CHANGE if change else ADDITION, message)
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        log_admin_action(request, obj, DELETION, "Видалено автора")
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            log_admin_action(request, obj, DELETION, "Масове видалення автора")
        super().delete_queryset(request, queryset)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = _("Автори")
        return super().changelist_view(request, extra_context=extra_context)


# ---- Comment ----
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at')
    list_filter = ('created_at', 'user')

    def save_model(self, request, obj, form, change):
        message = "Змінено коментар" if change else "Додано новий коментар"
        log_admin_action(request, obj, CHANGE if change else ADDITION, message)
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        log_admin_action(request, obj, DELETION, "Видалено коментар")
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            log_admin_action(request, obj, DELETION, "Масове видалення коментаря")
        super().delete_queryset(request, queryset)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = _("Коментарі")
        return super().changelist_view(request, extra_context=extra_context)


# ---- SavedArticle ----
@admin.register(SavedArticle)
class SavedArticleAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'saved_at')
    list_filter = ('saved_at', 'user')

    def save_model(self, request, obj, form, change):
        message = "Змінено збережену статтю" if change else "Додано нову збережену статтю"
        log_admin_action(request, obj, CHANGE if change else ADDITION, message)
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        log_admin_action(request, obj, DELETION, "Видалено збережену статтю")
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            log_admin_action(request, obj, DELETION, "Масове видалення збережених статей")
        super().delete_queryset(request, queryset)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = _("Збережені статті")
        return super().changelist_view(request, extra_context=extra_context)


# ---- Tag ----
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

    def save_model(self, request, obj, form, change):
        message = "Змінено тег" if change else "Додано новий тег"
        log_admin_action(request, obj, CHANGE if change else ADDITION, message)
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        log_admin_action(request, obj, DELETION, "Видалено тег")
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            log_admin_action(request, obj, DELETION, "Масове видалення тегів")
        super().delete_queryset(request, queryset)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = _("Теги")
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(ProhibitedWord)
class ProhibitedWordAdmin(admin.ModelAdmin):
    list_display = ('word',)
    search_fields = ('word',)


# ---- SelectedFacade ----
@admin.register(SelectedFacade)
class SelectedFacadeAdmin(admin.ModelAdmin):
    change_form_template = "admin/newportal/selectedfacade/change_form.html"

    def has_add_permission(self, request):
        return not SelectedFacade.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Перевірка наявності об'єктів
        first_obj = SelectedFacade.objects.first()
        if first_obj:
            return redirect(reverse('admin:newportal_selectedfacade_change', args=[first_obj.pk]))
        else:
            # Якщо немає об'єктів, повертаємо повідомлення
            self.message_user(request, "Немає об'єктів для перегляду.", level=messages.WARNING)
            return super().changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = "Звіти"
        extra_context['reports'] = {
            'Помилки': reverse('error_list'),
            'Активність авторів': reverse('author_activity'),
            'Найбільш переглядані блоки новин': reverse('most_viewed_blocks'),
            'Популярні статті за переглядами': reverse('popular_articles_views'),
            'Популярні статті за збереженнями': reverse('popular_articles_saves'),
            'Заборонені слова в статтях': reverse('prohibited_words_report'),
            'Теги в статтях': reverse('tags_report'),
            'Перевірка заголовків на SEO': reverse('seo_titles_report'),
            'Оновлення новин': reverse('news-updates'),
            'Час створення блоків': reverse('news-time'),
        }

        # Обробка параметра "report"
        selected_report = request.GET.get('report')
        if selected_report:
            extra_context['selected_report'] = selected_report

        return super().change_view(request, object_id, form_url, extra_context)


admin.site.unregister(Group)
admin.site.unregister(User)


# ---- Group ----
@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    def save_model(self, request, obj, form, change):
        message = "Змінено групу" if change else "Додано нову групу"
        log_admin_action(request, obj, CHANGE if change else ADDITION, message)
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        log_admin_action(request, obj, DELETION, "Видалено групу")
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            log_admin_action(request, obj, DELETION, "Масове видалення груп")
        super().delete_queryset(request, queryset)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = "Групи"
        return super().changelist_view(request, extra_context=extra_context)


# ---- User ----
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    def save_model(self, request, obj, form, change):
        message = "Змінено користувача" if change else "Додано нового користувача"
        log_admin_action(request, obj, CHANGE if change else ADDITION, message)
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        log_admin_action(request, obj, DELETION, "Видалено користувача")
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            log_admin_action(request, obj, DELETION, "Масове видалення користувачів")
        super().delete_queryset(request, queryset)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = "Користувачі"
        return super().changelist_view(request, extra_context=extra_context)


def format_change_message(change_message):
    # Якщо повідомлення пусте, повертаємо "Без повідомлення"
    if not change_message:
        return "Без повідомлення"

    try:
        parsed_message = json.loads(change_message)  # Спроба розпарсити JSON
        formatted_message = []

        for entry in parsed_message:
            if "added" in entry:
                formatted_message.append("Додано новий об'єкт.")
            if "changed" in entry:
                fields = ", ".join(entry["changed"].get("fields", []))
                formatted_message.append(f"Змінено поля: {fields}.")
            if "deleted" in entry:
                formatted_message.append("Видалено об'єкт.")

        # Якщо список порожній (немає додаткової інформації), повертаємо "Без повідомлення"
        return " ".join(formatted_message) if formatted_message else "Без повідомлення"
    except json.JSONDecodeError:
        # Якщо не JSON, повертаємо оригінальний текст
        return change_message


# ---- Custom Admin Site ----
class CustomAdminSite(admin.AdminSite):
    site_header = "Управління сайтом"
    site_title = "Адмін панель"
    index_title = "Головна"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('clear-log/', self.admin_view(self.clear_logs), name='clear_log'),
            path('errors/', self.admin_view(views.error_list_view), name='error_list'),
            path('activity/authors/', self.admin_view(views.author_activity), name='author_activity'),
            path('tracker/popular-views/', self.admin_view(views.popular_articles_views),
                 name='popular_articles_views'),
            path('tracker/popular-saves/', self.admin_view(views.popular_articles_saves),
                 name='popular_articles_saves'),
            path('word/prohibited-words/', self.admin_view(views.prohibited_words_report),
                 name='prohibited_words_report'),
            path('word/seo-titles/', self.admin_view(views.seo_titles_report), name='seo_titles_report'),
            path('word/tags/', self.admin_view(views.tags_report), name='tags_report'),
            path('count/updates/', self.admin_view(views.news_updates), name='news-updates'),
            path('count/time/', self.admin_view(views.news_time), name='news-time'),
        ]
        return custom_urls + urls

    def clear_logs(self, request):
        LogEntry.objects.all().delete()  # Видаляємо всі записи з LogEntry
        messages.success(request, "Журнал дій очищено.")  # Відображаємо повідомлення успіху
        return HttpResponseRedirect(reverse('admin:index'))

    def each_context(self, request):
        context = super().each_context(request)
        recent_logs = LogEntry.objects.filter(user=request.user).order_by('-action_time')[:10]

        for log in recent_logs:
            log.formatted_change_message = format_change_message(log.change_message)

        context['recent_actions'] = recent_logs
        return context


# Створення кастомного адміністративного сайту
admin.site = CustomAdminSite()
admin.site.register(Author)
admin.site.register(Tag, TagAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(SavedArticle, SavedArticleAdmin)
admin.site.register(SelectedFacade, SelectedFacadeAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
