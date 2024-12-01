# app/decorators.py
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.profile.rol == 'administrador':
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied("You do not have permission to access this page.")
    return _wrapped_view