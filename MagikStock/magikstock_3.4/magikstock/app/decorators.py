from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from functools import wraps


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        print(f"Datos de la sesión: {request.session.items()}")
        if 'user_id' in request.session:
            return view_func(request, *args, **kwargs)
        else:
            print(f"Usuario no autenticado, redirigiendo al login desde {request.path}.")
            return redirect('login')
    return wrapper



def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get('rol') == 'administrador':
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrapper

def employee_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get('rol') == 'empleado':
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrapper