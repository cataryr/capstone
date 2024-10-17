from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from .forms import ProveedorForm, CategoriaForm, ProductoForm
from .models import Profile,Sucursal, Proveedor, Categoria, Producto, MovimientoEmpleado
import json


def home(request):
    if request.user.is_authenticated:
        productos_bajo_stock = Producto.objects.filter(cantidad__lt=5)

        if request.user.profile.rol == 'administrador':
            movimientos = MovimientoEmpleado.objects.all()

            # Filtros por fecha
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')

            if fecha_inicio and fecha_fin:
                fecha_inicio = timezone.make_aware(parse_datetime(fecha_inicio))
                fecha_fin = timezone.make_aware(parse_datetime(fecha_fin))
                movimientos = movimientos.filter(fecha__range=[fecha_inicio, fecha_fin])

            # Filtro por empleado
            empleado_id = request.GET.get('empleado')
            if empleado_id:
                movimientos = movimientos.filter(empleado__id=empleado_id)

            # Filtro por sucursal
            sucursal_id = request.GET.get('sucursal')
            if sucursal_id:
                movimientos = movimientos.filter(empleado__sucursal__id=sucursal_id)

            empleados = Profile.objects.filter(rol='empleado')
            sucursales = Sucursal.objects.all()

            return render(request, 'app/home_admin.html', {
                'movimientos': movimientos,
                'productos_bajo_stock': productos_bajo_stock,
                'empleados': empleados,
                'sucursales': sucursales,
                'empleado_id': empleado_id,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'sucursal_id': sucursal_id,
            })

        elif request.user.profile.rol == 'empleado':
            return render(request, 'app/home_empleado.html', {
                'productos_bajo_stock': productos_bajo_stock,
            })

    # Redirige a la página de login solo si el usuario no está autenticado
    return redirect('login')

    
# Verifica si el usuario es administrador
def es_administrador(user):
    return user.profile.rol == 'administrador'


@login_required
def T1_Stock(request):
    return render(request, 'app/T1_Stock.html')

@csrf_exempt
def update_product_quantity(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        cantidad_cambio = int(request.POST.get('cantidad', 1))  # Cantidad específica del cambio, si la hay

        try:
            with transaction.atomic():
                producto = Producto.objects.get(id=product_id)
                empleado = request.user.profile  # Asegúrate de que el usuario tenga un perfil asociado
                
                if action == 'add':
                    producto.cantidad += cantidad_cambio
                    tipo_movimiento = 'agregar'
                elif action == 'subtract' and producto.cantidad >= cantidad_cambio:
                    producto.cantidad -= cantidad_cambio
                    tipo_movimiento = 'restar'
                else:
                    return JsonResponse({'success': False, 'error': 'Cantidad insuficiente'})

                producto.save()

                # Crear registro en el historial de movimientos
                MovimientoEmpleado.objects.create(
                    empleado=empleado,
                    producto=producto,
                    cantidad=cantidad_cambio,
                    tipo_movimiento=tipo_movimiento
                )

            return JsonResponse({'success': True, 'new_quantity': producto.cantidad})
        except Producto.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'})

    return JsonResponse({'success': False, 'error': 'Método no permitido'})



def T1_Producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto registrado correctamente.")
            return redirect('T1_Producto')  # Redirigir a la misma página después de guardar
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = ProductoForm()

    productos = Producto.objects.all()  # Obtener todos los productos para mostrarlos en la lista

    return render(request, 'app/T1_Producto.html', {'form': form, 'productos': productos})

def T1_Edit_Producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect('T1_Producto')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'app/T1_Edit_Producto.html', {'form': form, 'producto': producto})

def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    messages.success(request, "Producto eliminado correctamente.")
    return redirect('T1_Producto')

#----------------------INICIO SECTION CATEGORIA-------------------------------------------------------------
def T1_Edit_Categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría actualizada correctamente.")
            return redirect('T1_Categoria')  # Redirige a la lista de categorías
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, 'app/T1_Edit_Categoria.html', {'form': form, 'categoria': categoria})

def eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    categoria.delete()
    messages.success(request, "Categoría eliminada correctamente.")
    return redirect('T1_Categoria')

def T1_Categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría registrada correctamente.")
            return redirect('T1_Categoria')  # Redirige a la lista de categorías, puedes cambiar la redirección según sea necesario
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = CategoriaForm()

    categorias = Categoria.objects.all()  # Obtener todas las categorías para mostrarlas en la lista

    return render(request, 'app/T1_Categoria.html', {'form': form, 'categorias': categorias})

#----------------------FIN SECTION CATEGORIA-------------------------------------------------------------

#----------------------INICIO SECTION PROVEEDOR-------------------------------------------------------------

def T1_Proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()  # Guardar el proveedor en la base de datos
            messages.success(request, "Proveedor registrado correctamente.")
            return redirect('T1_Proveedor')  # Redirigir a la página de stock o a donde prefieras
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = ProveedorForm()

    proveedores = Proveedor.objects.all().order_by('nombre_proveedor')

    return render(request, 'app/T1_Proveedor.html', {'form': form, 'proveedores': proveedores})

def T1_edit_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor actualizado correctamente.")
            return redirect('T1_Proveedor')  # Redirigir a la vista de proveedores
    else:
        form = ProveedorForm(instance=proveedor)

    return render(request, 'app/T1_edit_proveedor.html', {'form': form, 'proveedor': proveedor})

def eliminar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    proveedor.delete()
    messages.success(request, "Proveedor eliminado correctamente.")
    return redirect('T1_Proveedor')

#----------------------FIN SECTION PROVEEDOR-------------------------------------------------------------

def T2_Employees_List(request):
    empleados = Profile.objects.all()

    return render(request, 'app/T2_Employees_List.html', {'empleados': empleados})

# Vista para editar un empleado
def T2_Employees_Edit(request, id):
    empleado = get_object_or_404(Profile, id=id)

    if request.method == 'POST':
        # Recoger datos del formulario
        empleado.user.first_name = request.POST.get('first_name')
        empleado.user.last_name = request.POST.get('last_name')
        empleado.user.email = request.POST.get('email')
        empleado.rut = request.POST.get('rut')
        empleado.num = request.POST.get('num')
        empleado.rol = request.POST.get('rol')
        
        # Obtener la sucursal seleccionada
        sucursal_id = request.POST.get('sucursal')  # Recoger el ID de la sucursal seleccionada
        empleado.sucursal = Sucursal.objects.get(id=sucursal_id) if sucursal_id else None  # Asignar la sucursal

        # Guardar cambios
        empleado.user.save()
        empleado.save()

        messages.success(request, "Empleado actualizado correctamente.")
        return redirect('T2_Employees_List')

    return render(request, 'app/T2_Employees_Edit.html', {'empleado': empleado})

# Vista para eliminar un empleado
def T2_Employees_Delete(request, id):
    empleado = get_object_or_404(Profile, id=id)

    if request.method == 'POST':
        empleado.user.delete()  # Eliminar el usuario y el perfil asociado
        messages.success(request, "Empleado eliminado correctamente.")
        return redirect('T2_Employees_List')

    return redirect('T2_Employees_List')

@login_required
def T2_Employees(request):
    if request.method == 'POST':
        # Recoger datos del formulario
        username = request.POST.get('new-username').strip()
        password = request.POST.get('new-password').strip()
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        email = request.POST.get('email').strip()
        rut = request.POST.get('rut').strip()
        num = request.POST.get('num').strip()
        rol = request.POST.get('rol').strip()
        sucursal_id = request.POST.get('sucursal').strip() 

        # Validaciones
        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya existe.")
            return redirect('T2_Employees')

        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo electrónico ya está registrado.")
            return redirect('T2_Employees')

        if Profile.objects.filter(rut=rut).exists():
            messages.error(request, "Ya existe un usuario con este RUT.")
            return redirect('T2_Employees')
        
        sucursal = Sucursal.objects.get(id=sucursal_id) if sucursal_id else None

        # Crear un nuevo usuario
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        # Verificar si el perfil ya existe
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={'rut': rut, 'num': num, 'rol': rol, 'sucursal': sucursal}
        )

        if not created:  # Si el perfil ya existía, actualiza los campos
            profile.rut = rut
            profile.num = num
            profile.rol = rol
            profile.sucursal = sucursal  # Asignar sucursal
            profile.save()

        messages.success(request, "Usuario registrado exitosamente.")
        return redirect('T2_Employees')

    sucursales = Sucursal.objects.all()  # Obtener todas las sucursales para mostrarlas en el formulario
    return render(request, 'app/T2_Employees.html', {'sucursales': sucursales})

@login_required
def T3_Dashboard(request):
    return render(request, 'app/T3_Dashboard.html')

@login_required
@never_cache
def T4_Settings(request):
    perfil = Profile.objects.get(user=request.user)
    

    if request.method == 'POST':
        nombre = request.POST.get('nombre').strip()
        apellido = request.POST.get('apellido').strip()
        numero = request.POST.get('numero').strip()  # Número de teléfono
        correo = request.POST.get('correo').strip()
        rut = request.POST.get('rut').strip()  
    
        # Validaciones
        if not nombre or not apellido or not numero or not correo or not rut:
            messages.error(request, "No puedes dejar campos vacíos.")
            return redirect('T4_Settings')

        if not nombre.isalpha() or not apellido.isalpha():
            messages.error(request, "El nombre y el apellido solo pueden contener letras.")
            return redirect('T4_Settings')

        if not numero.isdigit() or len(numero) != 9:
            messages.error(request, "El número debe contener solo dígitos y tener 9 caracteres.")
            return redirect('T4_Settings')

        # Validar formato de correo
        try:
            validate_email(correo)
        except ValidationError:
            messages.error(request, "El correo no es válido.")
            return redirect('T4_Settings')


        # Guardar los cambios
        request.user.first_name = nombre
        request.user.last_name = apellido
        perfil.num = numero
        request.user.email = correo
        request.user.save()
        perfil.save()
        
        messages.success(request, "Datos actualizados correctamente.")
        return redirect('T4_Settings')
    

    context = {
        'correo': request.user.email,
        'rut': perfil.rut,
        'num': perfil.num,
        'rol': perfil.rol,
        'nombre': request.user.first_name,  
        'apellido': request.user.last_name, 
        'sucursal': perfil.sucursal,
    }

    return render(request, 'app/T4_Settings.html', context)



class CustomLoginView(LoginView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')  # Redirige a 'home' si ya está autenticado
        return super().dispatch(request, *args, **kwargs)



#----------------------  DASHBOARD -------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
def T3_Dashboard(request):
    # Obtener los datos de proveedores
    proveedores = Proveedor.objects.all()

    proveedores_nombres = [proveedor.nombre_proveedor for proveedor in proveedores]
    proveedores_telefonos = [proveedor.telefono for proveedor in proveedores]

    context = {
        'proveedores_nombres': json.dumps(proveedores_nombres),
        'proveedores_telefonos': json.dumps(proveedores_telefonos),
    }
    return render(request, 'app/T3_Dashboard.html', context)