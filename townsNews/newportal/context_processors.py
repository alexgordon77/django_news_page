def user_site_settings(request):
    if request.user.is_authenticated:
        settings = getattr(request.user, "site_settings", None)
    else:
        settings = None
    return {'site_settings': settings}


def is_admin_context(request):
    is_admin = request.user.is_authenticated and request.user.groups.filter(name='admin-group').exists()
    return {'is_admin': is_admin}
