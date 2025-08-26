from django.shortcuts import redirect
from django.contrib import messages
from .models import UserBan


class CheckBanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                user_ban = UserBan.objects.get(user=request.user)
                if user_ban.is_banned():
                    remaining_time = user_ban.remaining_time()
                    # Якщо користувач забанений, виводимо повідомлення про залишковий час
                    messages.error(request, f'Ваш акаунт заблокований. Залишилось: {remaining_time.days} днів, {remaining_time.seconds // 3600} годин.')
                    # Вивести повідомлення і розлогінити користувача
                    return redirect('logout')
            except UserBan.DoesNotExist:
                pass  # Якщо користувач не забанований, пропускаємо
        return self.get_response(request)
