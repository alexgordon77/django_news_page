from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate


class Author(models.Model):
    name = models.CharField(max_length=50,
                            help_text="Введіть ім'я автора",
                            verbose_name="Ім'я автора")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "автори"
        verbose_name_plural = "Автори"


class Tag(models.Model):
    name = models.CharField(max_length=20,
                            help_text="Введіть тег",
                            verbose_name="Теги")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "Теги"


class Article(models.Model):
    title = models.CharField(max_length=100,
                             verbose_name='Назва статті')
    article_text = models.TextField(max_length=1000,
                                    verbose_name='Текст статті',
                                    default="Поле статті")
    author = models.ForeignKey(Author, on_delete=models.CASCADE,
                               verbose_name="Автор")
    date_of_publication = models.DateField(verbose_name='Дата публікації',
                                           null=True,
                                           blank=True)
    tags = models.ManyToManyField(Tag, verbose_name="Теги")
    views_count = models.IntegerField(default=0, verbose_name="Кількість переглядів")
    image = models.ImageField(upload_to='article_images/', null=True, blank=True, verbose_name="Зображення")

    def display_tag(self):
        return ', '.join([tag.name for tag in self.tags.all()])

    display_tag.short_description = 'Теги'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article-detail',
                       args=[str(self.id)])

    class Meta:
        verbose_name = "статтю"
        verbose_name_plural = "Статті"


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Введіть текст коментаря')
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата створення')

    def __str__(self):
        return f'Коментар від {self.user.username} до {self.article.title}'

    class Meta:
        verbose_name = "коментар"
        verbose_name_plural = "Коментарі"


class SavedArticle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='saved_articles')
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата збереження')

    def __str__(self):
        return f'{self.user.username} зберіг "{self.article.title}"'

    class Meta:
        verbose_name = "збережену статтю"
        verbose_name_plural = "Збережені статті"


class UserSiteSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="site_settings"
    )
    font_color = models.CharField(max_length=7, default='#ffffff')
    background_color = models.CharField(max_length=7, default='#002f31')
    font_size = models.IntegerField(default=14, validators=[MinValueValidator(12), MaxValueValidator(36)])

    def __str__(self):
        return f"Site settings for {self.user.username}"


class UserBan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ban_end = models.DateTimeField()

    def is_banned(self):
        return self.ban_end > timezone.now()

    def remaining_time(self):
        return self.ban_end - timezone.now()

    def __str__(self):
        return f'{self.user.username} - заблокований до {self.ban_end}'

    class Meta:
        verbose_name = "Блокування користувача"
        verbose_name_plural = "Блокування користувачів"


class SelectedFacade(models.Model):
    FACADE_CHOICES = {
        ("error", "error"),
        ("activity", "activity"),
        ("tracker", "tracker"),
        ("word", "word"),
        ("count", "count")
    }

    selected_facade = models.CharField(max_length=20,
                                       default='error',
                                       choices=FACADE_CHOICES,
                                       verbose_name='Виберіть варіант дослідження')

    def save(self, *args, **kwargs):
        if SelectedFacade.objects.exists() and not self.pk:
            raise ValidationError("Може бути лише один варіант дослідження")
        super(SelectedFacade, self).save(*args, **kwargs)

    def __str__(self):
        return ''

    class Meta:
        verbose_name = "звіт"
        verbose_name_plural = "Звіти"


class ProhibitedWord(models.Model):
    word = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.word
