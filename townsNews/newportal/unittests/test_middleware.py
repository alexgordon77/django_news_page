import unittest
from unittest.mock import MagicMock, patch
from django.contrib.auth.models import AnonymousUser, User
from django.shortcuts import redirect
from django.contrib.messages.storage.fallback import FallbackStorage
from newportal.middleware import CheckBanMiddleware
from newportal.models import UserBan


class TestCheckBanMiddleware(unittest.TestCase):
    def setUp(self):
        self.get_response_mock = MagicMock()
        self.middleware = CheckBanMiddleware(self.get_response_mock)

    def test_anonymous_user(self):
        """Перевірка: якщо користувач не залогінений, middleware пропускає запит"""
        request = MagicMock()
        request.user = AnonymousUser()
        response = self.middleware(request)
        self.get_response_mock.assert_called_once_with(request)
        self.assertEqual(response, self.get_response_mock(request))

    @patch('newportal.models.UserBan.objects.get', side_effect=UserBan.DoesNotExist)
    def test_authenticated_not_banned_user(self, mock_get):
        """Перевірка: якщо користувач залогінений і не забанений, middleware пропускає запит"""
        request = MagicMock()
        request.user = MagicMock(spec=User, is_authenticated=True)
        response = self.middleware(request)

        # ✅ Переконуємося, що get() викликався
        mock_get.assert_called_once_with(user=request.user)

        self.get_response_mock.assert_called_once_with(request)
        self.assertEqual(response, self.get_response_mock(request))

    @patch('newportal.models.UserBan.objects.get')
    def test_banned_user_redirects(self, mock_get):
        """Перевірка: якщо користувач забанений, виконується редирект на logout"""
        request = MagicMock()
        request.user = MagicMock(spec=User, is_authenticated=True)

        # ✅ Мокуємо UserBan
        user_ban_mock = MagicMock()
        user_ban_mock.is_banned.return_value = True

        # ✅ Симулюємо `remaining_time()`, щоб повертав days та seconds
        remaining_time_mock = MagicMock()
        remaining_time_mock.days = 3
        remaining_time_mock.seconds = 7200  # 2 години
        user_ban_mock.remaining_time.return_value = remaining_time_mock

        mock_get.return_value = user_ban_mock

        # ✅ Додаємо support для messages
        messages_mock = FallbackStorage(request)
        request._messages = messages_mock

        response = self.middleware(request)

        # ✅ 1. Перевіряємо, що get() викликався
        mock_get.assert_called_once_with(user=request.user)

        # ✅ 2. Перевіряємо, що бан реально перевіряється
        user_ban_mock.is_banned.assert_called_once()

        # ✅ 3. Перевіряємо, що залишковий час був підрахований
        user_ban_mock.remaining_time.assert_called_once()

        # ✅ 4. Перевіряємо, що додалося повідомлення
        message_list = list(messages_mock)
        self.assertEqual(len(message_list), 1)
        self.assertIn('Ваш акаунт заблокований', message_list[0].message)
        self.assertIn('3 днів, 2 годин', message_list[0].message)

        # ✅ 5. Перевіряємо, що це дійсно редирект
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, redirect('logout').url)

    @patch('newportal.models.UserBan.objects.get', side_effect=UserBan.DoesNotExist)
    def test_no_ban_does_not_redirect(self, mock_get):
        """Перевірка: якщо UserBan не існує, запит продовжується без змін"""
        request = MagicMock()
        request.user = MagicMock(spec=User, is_authenticated=True)
        response = self.middleware(request)

        # ✅ Переконуємося, що get() викликався
        mock_get.assert_called_once_with(user=request.user)

        self.get_response_mock.assert_called_once_with(request)
        self.assertEqual(response, self.get_response_mock(request))


if __name__ == '__main__':
    unittest.main()