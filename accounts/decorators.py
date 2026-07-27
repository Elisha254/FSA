from functools import wraps
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")

            if request.user.role not in allowed_roles:
                messages.error(request, 'You do not have permission to access that page.')
                return redirect(settings.LOGIN_URL)

            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator


admin_or_supervisor_required = role_required(['admin', 'supervisor'])
admin_required = role_required(['admin'])
