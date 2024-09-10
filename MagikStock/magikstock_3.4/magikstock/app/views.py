from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.auth import logout
from .models import empleados, proveedor
from .forms import LoginForm
from .decorators import admin_required, login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Vista para la página principal
@login_required
def home(request):
    return render(request, 'app/home.html')

# Vista para la página de stock
@login_required
@never_cache
def stock(request):
    return render(request, 'app/stock.html')

# Vista para la página de BI
@login_required
def bi(request):
    return render(request, 'app/bi.html')

# Vista para la página de configuración
@login_required
@never_cache
def config(request):
    if request.method == 'POST':
        empleado = empleados.objects.get(run=request.session.get('run'))
        
        # Actualizamos los campos si fueron enviados en el formulario
        nuevo_nombre = request.POST.get('nombre')
        nuevos_apellidos = request.POST.get('apellidos')
        nuevo_correo = request.POST.get('correo')
        nuevo_numero = request.POST.get('numero')

        if nuevo_nombre:
            empleado.nombre_emp = nuevo_nombre
        if nuevos_apellidos:
            empleado.apellidos_emp = nuevos_apellidos
        if nuevo_correo:
            empleado.correo = nuevo_correo
        if nuevo_numero:
            empleado.numero = nuevo_numero
        
        empleado.save()
        return redirect('config')

    else:
        empleado = empleados.objects.get(run=request.session.get('run'))

        context = {
            'correo': empleado.correo,
            'nombre': empleado.nombre_emp,
            'apellidos': empleado.apellidos_emp,
            'numero': empleado.numero,
        }

        return render(request, 'app/config.html', context)


# Vista para la página de empleados
@login_required
@never_cache
@admin_required
def employee(request):
    return render(request, 'app/employee.html')

@never_cache
def login_view(request):
    # Si el usuario ya está autenticado, redirigirlo a la página de inicio
    if 'user_id' in request.session:
        return redirect('home')

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            run = form.cleaned_data['run']
            password = form.cleaned_data['contraseña']

            try:
                user = empleados.objects.get(run=run)
                if check_password(password, user.contraseña):
                    # Guardar información en la sesión
                    request.session['user_id'] = user.id
                    request.session['run'] = user.run
                    request.session['rol'] = user.rol

                    print(f"Usuario {user.run} autenticado. ID guardado en sesión: {request.session['user_id']}")
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('home')  # Redirigir a la página principal
                else:
                    form.add_error('contraseña', 'Contraseña incorrecta.')
            except empleados.DoesNotExist:
                form.add_error('run', 'RUN no encontrado.')
    else:
        form = LoginForm()

    return render(request, 'app/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Has cerrado sesión exitosamente.")
    return redirect('login')
