import unittest
from unittest.mock import MagicMock, patch
from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from newportal.forms import (
    UserRegistrationForm, CommentForm, SiteSettingsForm, ArticleForm,
    BanUserForm, CustomLoginForm, AddUserForm
)


class TestUserRegistrationForm(unittest.TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepassword123',
            'password_confirm': 'securepassword123'
        }

    def test_valid_form(self):
        form = UserRegistrationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        self.valid_data['password_confirm'] = 'wrongpassword'
        form = UserRegistrationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Паролі не збігаються', form.errors['password_confirm'])

    def test_empty_password(self):
        """Перевірка помилки, якщо пароль відсутній"""
        self.valid_data['password'] = ''
        self.valid_data['password_confirm'] = ''
        form = UserRegistrationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Обов\'язкове поле.', form.errors['password'])
        self.assertIn('Обов\'язкове поле.', form.errors['password_confirm'])


class TestCommentForm(unittest.TestCase):
    def test_comment_form_init(self):
        form = CommentForm()
        self.assertEqual(form.fields['text'].widget.attrs['class'], 'form-control comment-input')


class TestSiteSettingsForm(unittest.TestCase):
    def test_widgets(self):
        form = SiteSettingsForm()
        self.assertEqual(form.fields['font_color'].widget.attrs['type'], 'color')
        self.assertEqual(form.fields['background_color'].widget.attrs['type'], 'color')
        self.assertEqual(form.fields['font_size'].widget.attrs['type'], 'range')


class TestArticleForm(unittest.TestCase):
    def test_widgets(self):
        form = ArticleForm()
        self.assertEqual(form.fields['date_of_publication'].widget.attrs['type'], 'date')


class TestBanUserForm(unittest.TestCase):
    def setUp(self):
        self.mock_user = MagicMock()
        self.form_data = {'period': '7'}
        self.form = BanUserForm(data=self.form_data)

    @patch('news.models.UserBan.objects.update_or_create')
    def test_apply_ban(self, mock_update_or_create):
        self.assertTrue(self.form.is_valid())
        self.form.apply_ban(self.mock_user)
        mock_update_or_create.assert_called_once()


class TestCustomLoginForm(unittest.TestCase):
    @patch('news.models.UserBan.objects.get')
    def test_banned_user(self, mock_get):
        mock_user_ban = MagicMock()
        mock_user_ban.is_banned.return_value = True
        mock_user_ban.remaining_time.return_value = timedelta(days=3, hours=5)
        mock_get.return_value = mock_user_ban

        form = CustomLoginForm()
        with self.assertRaises(forms.ValidationError) as e:
            form.confirm_login_allowed(MagicMock())
        self.assertIn('Ваш акаунт заблокований', str(e.exception))


class TestAddUserForm(unittest.TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepassword123',
            'password_confirm': 'securepassword123'
        }

    def test_valid_form(self):
        """Перевірка валідності форми"""
        form = AddUserForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        self.valid_data['password_confirm'] = 'wrongpassword'
        form = AddUserForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Паролі не збігаються', form.errors['password_confirm'])

    def test_empty_password(self):
        """Перевірка, що форма не проходить без пароля"""
        self.valid_data['password'] = ''
        self.valid_data['password_confirm'] = ''
        form = AddUserForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Обов\'язкове поле.', form.errors['password'])
        self.assertIn('Обов\'язкове поле.', form.errors['password_confirm'])

    @patch.object(User, 'save')
    def test_save(self, mock_save):
        form = AddUserForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        user = form.save(commit=True)
        mock_save.assert_called_once()
        self.assertTrue(user.check_password('securepassword123'))


if __name__ == '__main__':
    unittest.main()