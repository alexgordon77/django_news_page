from datetime import timedelta
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django import forms
from django.contrib.auth.models import User
from .models import Comment, Article, UserBan, UserSiteSettings


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'no-copy-paste'}),
        label="Пароль"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'no-copy-paste'}),
        label="Підтвердження пароля"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_strong_password(password)
        return password

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password != password_confirm:
            raise forms.ValidationError("Паролі не збігаються")
        return password_confirm


def validate_strong_password(password):
    if len(password) < 8:
        raise ValidationError('Пароль має містити щонайменше 8 символів.')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Пароль має містити хоча б одну велику літеру.')
    if not re.search(r'[!@#$%^&*]', password):
        raise ValidationError('Пароль має містити хоча б один спецсимвол: !@#$%^&*')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Введіть ваш коментар...'}),
        }

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({
            'class': 'form-control comment-input',
            'placeholder': 'Напишіть свій коментар тут...'
        })


class UserSiteSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSiteSettings
        fields = ['font_color', 'background_color', 'font_size']
        widgets = {
            'font_color': forms.TextInput(attrs={'type': 'color'}),
            'background_color': forms.TextInput(attrs={'type': 'color'}),
            'font_size': forms.NumberInput(attrs={
                'type': 'range', 'min': 12, 'max': 36, 'step': 1, 'class': 'slider'
            })
        }


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'article_text', 'author', 'tags', 'date_of_publication', 'image']
        widgets = {
            'date_of_publication': forms.DateInput(attrs={'type': 'date'}),  # Вибір дати
        }


BAN_PERIOD_CHOICES = [
    (1, '1 день'),
    (7, '1 тиждень'),
    (30, '1 місяць'),
    (365, '1 рік'),
    (99999, 'Довічно'),
]


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Ім'я"
        self.fields['email'].label = "Email"
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget = forms.EmailInput(attrs={'class': 'form-control'})


class BanUserForm(forms.Form):
    period = forms.ChoiceField(choices=BAN_PERIOD_CHOICES, label="Термін блокування")

    def apply_ban(self, user):
        period_days = int(self.cleaned_data['period'])
        if period_days == 99999:
            ban_end = timezone.now() + timedelta(days=365*100)
        else:
            ban_end = timezone.now() + timedelta(days=period_days)
        UserBan.objects.update_or_create(user=user, defaults={'ban_end': ban_end})


class CustomLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        try:
            user_ban = UserBan.objects.get(user=user)
            if user_ban.is_banned():
                remaining_time = user_ban.remaining_time()
                # Виведення повідомлення про бан без локалізації
                raise forms.ValidationError(
                    f'Ваш акаунт заблокований. Залишилось: {remaining_time.days} днів, {remaining_time.seconds // 3600} годин.',
                    code='banned',
                )
        except UserBan.DoesNotExist:
            pass  # Якщо бану немає, дозволяємо вхід


class AddUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Підтвердження пароля")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password != password_confirm:
            raise forms.ValidationError("Паролі не збігаються")
        return password_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
