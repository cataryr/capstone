import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from prophet import Prophet
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Sum, Case, When, IntegerField, Q
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
import pprint 

from .decorators import admin_required
from .forms import ProveedorForm, CategoriaForm, ProductoForm
from .models import Profile, Sucursal, Proveedor, Categoria, Producto, MovimientoEmpleado
from .forms import CustomAuthenticationForm

#---------------------- LOGIN -----------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm

    def form_invalid(self, form):
        # Redirige al usuario a la misma página con un parámetro de error en la URL
        return redirect(f"{self.request.path}?error=1")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


#---------------------- HOME ------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@login_required
def home(request):
    is_admin = request.user.profile.rol == 'administrador'

    # Obtener productos bajos en stock y organizarlos alfabéticamente por proveedor y por producto
    productos_bajo_stock_qs = Producto.objects.filter(cantidad__lt=5).order_by('nombre_producto')
    productos_bajo_stock_dict = defaultdict(list)
    for producto in productos_bajo_stock_qs:
        productos_bajo_stock_dict[producto.id_proveedor.nombre_proveedor].append(producto)
    
    # Convertir a lista y ordenar proveedores alfabéticamente
    productos_bajo_stock = sorted(
        [(proveedor, sorted(productos, key=lambda p: p.nombre_producto)) for proveedor, productos in productos_bajo_stock_dict.items()],
        key=lambda x: x[0]
    )

    movimientos = empleados = sucursales = None
    fecha_inicio = fecha_fin = empleado_id = sucursal_id = None

    if is_admin:
        movimientos = MovimientoEmpleado.objects.all()

        if request.GET.get('clear_filters'):
            fecha_inicio = fecha_fin = empleado_id = sucursal_id = None
        else:
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            if fecha_inicio and fecha_fin:
                try:
                    fecha_inicio_parsed = timezone.make_aware(datetime.strptime(fecha_inicio, "%Y-%m-%d"))
                    fecha_fin_parsed = timezone.make_aware(datetime.strptime(fecha_fin, "%Y-%m-%d"))
                    movimientos = movimientos.filter(fecha__range=[fecha_inicio_parsed, fecha_fin_parsed])
                except Exception as e:
                    print(f"Error en el filtro de fechas: {e}")

            empleado_id = request.GET.get('empleado')
            if empleado_id:
                movimientos = movimientos.filter(empleado__id=empleado_id)

            sucursal_id = request.GET.get('sucursal')
            if sucursal_id:
                movimientos = movimientos.filter(empleado__sucursal__id_sucursal=sucursal_id)

        movimientos = movimientos.order_by('-fecha')
        empleados = Profile.objects.filter(rol__in=['empleado', 'administrador']).order_by('user__username')
        sucursales = Sucursal.objects.all().order_by('nombre')

    return render(request, 'app/home.html', {
        'is_admin': is_admin,
        'movimientos': movimientos,
        'productos_bajo_stock': productos_bajo_stock,
        'empleados': empleados,
        'sucursales': sucursales,
        'empleado_id': empleado_id,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'sucursal_id': sucursal_id,
    })


#---------------------- GESTION DE STOCK ------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#---------------------- PRODUCTOS -------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@login_required
def T1_Producto(request):
    is_admin = request.user.profile.rol == 'administrador'
    
    # Obtener el proveedor seleccionado del parámetro GET
    proveedor_id = request.GET.get('proveedor')
    
    # Filtrar y ordenar productos según el proveedor seleccionado
    if proveedor_id:  # Asegurarnos de que proveedor_id no esté vacío
        productos = Producto.objects.filter(id_proveedor=proveedor_id).order_by('nombre_producto')
    else:
        productos = Producto.objects.all().order_by('nombre_producto')
        
    # Obtener y ordenar la lista de proveedores para el filtro
    proveedores = Proveedor.objects.all().order_by('nombre_proveedor')

    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)  # No guardar aún, para asignar la sucursal
            # Si no se ha proporcionado una sucursal, asignar la primera sucursal por defecto
            if not producto.id_sucursal:
                producto.id_sucursal = Sucursal.objects.first()  # O bien, puedes agregar lógica para elegir la sucursal adecuada
            producto.save()  # Ahora sí guardamos el producto con la sucursal
            messages.success(request, "Producto registrado correctamente.")
            return redirect('T1_Producto')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = ProductoForm()

    return render(request, 'app/T1_Producto.html', {
        'form': form,
        'productos': productos,
        'proveedores': proveedores,
        'is_admin': is_admin,
    })


@login_required
def T1_Edit_Producto(request, producto_id):
    is_admin = request.user.profile.rol == 'administrador'
    producto = get_object_or_404(Producto, id_producto=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect('T1_Producto')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'app/T1_Edit_Producto.html', {'form': form, 'producto': producto, 'is_admin': is_admin})

@login_required
@admin_required
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    producto.delete()
    messages.success(request, "Producto eliminado correctamente.")
    return redirect('T1_Producto')


#---------------------- CATEGORIAS ------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@login_required
def T1_Categoria(request):
    is_admin = request.user.profile.rol == 'administrador'
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
    return render(request, 'app/T1_Categoria.html', {'form': form, 'categorias': categorias, 'is_admin': is_admin})

@login_required
def T1_Edit_Categoria(request, categoria_id):
    is_admin = request.user.profile.rol == 'administrador'
    categoria = get_object_or_404(Categoria, id_categoria=categoria_id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría actualizada correctamente.")
            return redirect('T1_Categoria')  # Redirige a la lista de categorías
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'app/T1_Edit_Categoria.html', {'form': form, 'categoria': categoria, 'is_admin': is_admin})

@login_required
@admin_required
def eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id_categoria=categoria_id)
    categoria.delete()
    messages.success(request, "Categoría eliminada correctamente.")
    return redirect('T1_Categoria')


#---------------------- PROVEEDORES -----------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@login_required
def T1_Proveedor(request):
    is_admin = request.user.profile.rol == 'administrador'
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
    proveedores = Proveedor.objects.all().order_by('id_proveedor')
    return render(request, 'app/T1_Proveedor.html', {'form': form, 'proveedores': proveedores, 'is_admin': is_admin})

@login_required
def T1_edit_proveedor(request, id_proveedor):
    is_admin = request.user.profile.rol == 'administrador'
    proveedor = get_object_or_404(Proveedor, id_proveedor=id_proveedor)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor actualizado correctamente.")
            return redirect('T1_Proveedor')  # Redirigir a la vista de proveedores
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'app/T1_edit_proveedor.html', {'form': form, 'proveedor': proveedor, 'is_admin': is_admin})

@login_required
@admin_required
def eliminar_proveedor(request, id_proveedor):
    proveedor = get_object_or_404(Proveedor, id_proveedor=id_proveedor)
    proveedor.delete()
    messages.success(request, "Proveedor eliminado correctamente.")
    return redirect('T1_Proveedor')


#---------------------- GESTION DE EMPLEADOS --------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@login_required
@admin_required
def T2_Employees_List(request):
    is_admin = request.user.profile.rol == 'administrador'
    empleados = Profile.objects.all()
    return render(request, 'app/T2_Employees_List.html', {'empleados': empleados, 'is_admin': is_admin})

@login_required
@admin_required
def T2_Employees_Edit(request, id):
    is_admin = request.user.profile.rol == 'administrador'
    empleado = get_object_or_404(Profile, id=id)
    if request.method == 'POST':
        empleado.user.first_name = request.POST.get('first_name')
        empleado.user.last_name = request.POST.get('last_name')
        empleado.user.email = request.POST.get('email')
        empleado.rut = request.POST.get('rut')
        empleado.num = request.POST.get('num')
        empleado.rol = request.POST.get('rol')
        sucursal_id = request.POST.get('sucursal') 
        empleado.sucursal = Sucursal.objects.get(id_sucursal=sucursal_id) if sucursal_id else None
        empleado.user.save()
        empleado.save()
        messages.success(request, "Empleado actualizado correctamente.")
        return redirect('T2_Employees_List')
    sucursales = Sucursal.objects.all()
    sucursal_descripcion = empleado.sucursal.descripcion if empleado.sucursal else None
    return render(request, 'app/T2_Employees_Edit.html', {
        'empleado': empleado,
        'sucursales': sucursales, 
        'sucursal_descripcion': sucursal_descripcion, 
        'is_admin': is_admin
    })

@login_required
@admin_required
def T2_Employees_Delete(request, id):
    empleado = get_object_or_404(Profile, id=id)
    if request.method == 'POST':
        empleado.user.delete()  # Eliminar el usuario y el perfil asociado
        messages.success(request, "Empleado eliminado correctamente.")
        return redirect('T2_Employees_List')
    return redirect('T2_Employees_List')

@login_required
@admin_required
def T2_Employees(request):
    is_admin = request.user.profile.rol == 'administrador'
    if request.method == 'POST':
        username = request.POST.get('new-username').strip()
        password = request.POST.get('new-password').strip()
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        email = request.POST.get('email').strip()
        rut = request.POST.get('rut').strip()
        num = request.POST.get('num').strip()
        rol = request.POST.get('rol').strip()
        sucursal_id = request.POST.get('sucursal').strip()  # El ID de la sucursal

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

        # Obtener la sucursal usando el ID
        sucursal = Sucursal.objects.filter(id_sucursal=sucursal_id).first()  # Cambiado para manejar casos sin sucursal
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
            profile.sucursal = sucursal  
            profile.save()
        messages.success(request, "Usuario registrado exitosamente.")
        return redirect('T2_Employees')
    # Obtener todas las sucursales para mostrarlas en el formulario
    sucursales = Sucursal.objects.all()
    return render(request, 'app/T2_Employees.html', {'sucursales': sucursales, 'is_admin': is_admin})


#---------------------- DASHBOARD -------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



@login_required
def T3_Dashboard(request):
    # VERIFICAR SI EL USUARIO ES ADMINISTRADOR
    is_admin = request.user.profile.rol == 'administrador'
    
    # OBTENER LOS PARÁMETROS DE FILTRO DE LA SOLICITUD
    producto_id = request.GET.get('producto')  # FILTRO POR PRODUCTO (si se selecciona uno específico)
    fecha_inicio = request.GET.get('fecha_inicio')  # FILTRO DE FECHA DE INICIO
    fecha_fin = request.GET.get('fecha_fin')  # FILTRO DE FECHA DE FIN
    periodo = int(request.GET.get('periodo', 0))  # OBTENER EL PERÍODO SELECCIONADO PARA LA PREDICCIÓN (por ejemplo, semanas)

    # SI NO SE PROPORCIONAN FECHAS DE INICIO Y FIN, SE UTILIZAN LAS FECHAS MÁS ANTIGUAS Y MÁS RECIENTES
    if not fecha_inicio and not fecha_fin:
        # OBTENER LA FECHA MÁS ANTIGUA Y MÁS RECIENTE EN LA BASE DE DATOS (si existen registros)
        fecha_inicio = MovimientoEmpleado.objects.earliest('fecha').fecha if MovimientoEmpleado.objects.exists() else timezone.now().date()
        fecha_fin = MovimientoEmpleado.objects.latest('fecha').fecha if MovimientoEmpleado.objects.exists() else timezone.now().date()
    else:
        # PARSEAR LAS FECHAS PROPORCIONADAS COMO DATOS DE TIPO FECHA
        fecha_inicio = parse_date(fecha_inicio) if fecha_inicio else None
        fecha_fin = parse_date(fecha_fin) if fecha_fin else None

        # SI SOLO SE PROPORCIONA UNA FECHA DE INICIO, LA FECHA DE FIN SE ESTABLECE COMO LA FECHA ACTUAL
        if fecha_inicio and not fecha_fin:
            fecha_fin = MovimientoEmpleado.objects.latest('fecha').fecha if MovimientoEmpleado.objects.exists() else timezone.now().date()

    # CREAR FILTROS PARA LOS MOVIMIENTOS HISTÓRICOS CON LOS CRITERIOS DE PRODUCTO Y FECHA
    filtros_historico = Q()
    if producto_id:
        filtros_historico &= Q(producto__id_producto=producto_id)  # FILTRAR POR PRODUCTO (si está seleccionado)
    if fecha_inicio:
        filtros_historico &= Q(fecha__gte=fecha_inicio)  # FILTRAR POR FECHA DE INICIO
    if fecha_fin:
        filtros_historico &= Q(fecha__lte=fecha_fin)  # FILTRAR POR FECHA DE FIN

    # OBTENER LOS MOVIMIENTOS HISTÓRICOS AGRUPADOS POR FECHA Y CALCULAR LOS TOTALES DE 'AGREGAR' Y 'RESTAR'
    movimientos_historicos = MovimientoEmpleado.objects.filter(filtros_historico).annotate(
        fecha_agrupada=TruncDate('fecha')  # AGRUPAR POR FECHA SIN LA PARTE DE LA HORA
    ).values('fecha_agrupada').annotate(
        total_agregar=Sum(Case(
            When(tipo_movimiento='agregar', then='cantidad'),  # SUMAR LA CANTIDAD DE LOS MOVIMIENTOS 'AGREGAR'
            default=0,
            output_field=IntegerField()
        )),

        total_restar=Sum(Case(
            When(tipo_movimiento='restar', then='cantidad'),  # SUMAR LA CANTIDAD DE LOS MOVIMIENTOS 'RESTAR'
            default=0,
            output_field=IntegerField()
        ))
    ).order_by('fecha_agrupada')  # ORDENAR POR LA FECHA

    # INICIALIZAR EL CONTEXTO PARA PASAR A LA VISTA (PARA LA PREDICCIÓN Y LOS DATOS HISTÓRICOS)
    context = {
        'productos': Producto.objects.filter(cantidad__gt=0).order_by('nombre_producto'),  # OBTENER LOS PRODUCTOS DISPONIBLES
        'fechas': json.dumps([]),
        'total_agregar': json.dumps([]),
        'total_restar': json.dumps([]),
        'fechas_prediccion': json.dumps([]),
        'valores_prediccion': json.dumps([]),
        'mensaje': ""  # MENSAJE DE ERROR SI NO HAY DATOS DISPONIBLES
    }

    # SI HAY MOVIMIENTOS HISTÓRICOS DISPONIBLES, SE PROCESAN Y SE ENVÍAN AL CONTEXTO
    if movimientos_historicos.exists():
        # EXTRAER LAS FECHAS Y LOS TOTALES DE 'AGREGAR' Y 'RESTAR'
        fechas = [mov['fecha_agrupada'].strftime('%Y-%m-%d') for mov in movimientos_historicos]
        total_agregar = [mov['total_agregar'] for mov in movimientos_historicos]
        total_restar = [mov['total_restar'] for mov in movimientos_historicos]

        # ASIGNAR LOS DATOS HISTÓRICOS AL CONTEXTO (para pasarlos a la plantilla)
        context['fechas'] = json.dumps(fechas)
        context['total_agregar'] = json.dumps(total_agregar)
        context['total_restar'] = json.dumps(total_restar)

        # LÓGICA PARA LAS PREDICCIONES CON PROPHET SOLO SI SE SELECCIONA UN PRODUCTO ESPECÍFICO
        if producto_id:
            # FILTRAR LOS MOVIMIENTOS HISTÓRICOS POR EL PRODUCTO SELECCIONADO
            movimientos_historicos_producto = MovimientoEmpleado.objects.filter(producto_id=producto_id)

            # SI HAY 90 O MÁS REGISTROS HISTÓRICOS DISPONIBLES, SE HACE LA PREDICCIÓN
            if movimientos_historicos_producto.count() >= 90:
                # FILTRAR SOLO LOS MOVIMIENTOS DE TIPO 'RESTAR' Y OBTENER SUS DATOS
                movimientos_restar = movimientos_historicos_producto.filter(tipo_movimiento='restar').values('fecha', 'cantidad')
                df_movimientos_restar = pd.DataFrame(movimientos_restar)

                if 'fecha' in df_movimientos_restar.columns:
                    # PREPARAR LOS DATOS PARA EL MODELO PROPHET (RENAME DE LAS COLUMNAS Y CONVERTIR FECHA)
                    df_prophet = df_movimientos_restar.rename(columns={'fecha': 'ds', 'cantidad': 'y'})
                    df_prophet['ds'] = pd.to_datetime(df_prophet['ds']).dt.tz_localize(None)  # CONVERTIR FECHAS A LOCAL TIME

                    # INICIALIZAR Y AJUSTAR EL MODELO PROPHET CON LOS DATOS HISTÓRICOS
                    model = Prophet()
                    model.fit(df_prophet)

                    # CREAR UN DATAFRAME PARA LAS FECHAS FUTURAS Y REALIZAR LAS PREDICCIONES
                    future = model.make_future_dataframe(periods=32)  # PREDICCIÓN A 32 DÍAS EN EL FUTURO
                    forecast = model.predict(future)

                    # OBTENER LA FECHA ACTUAL COMO EL INICIO DE LAS PREDICCIONES
                    last_date = np.datetime64(timezone.now())  # FECHA ACTUAL PARA FILTRAR LAS PREDICCIONES

                    # FILTRAR LAS PREDICCIONES A PARTIR DE LA FECHA ACTUAL
                    start_index = (forecast['ds'] >= last_date).idxmax()

                    # DETERMINAR CUÁNTOS DÍAS MOSTRAR SEGÚN EL FILTRO 'PERIODO' (POR EJEMPLO, 7 DÍAS)
                    dias_visualizar = periodo * 7 if periodo > 0 else 32  # 7 DÍAS SI 'PERIODO' ES MAYOR A 0, O 32 SI NO

                    # SELECCIONAR LAS FECHAS Y VALORES DE LAS PREDICCIONES A MOSTRAR
                    fechas_prediccion = forecast['ds'].dt.strftime('%Y-%m-%d').tolist()[start_index:start_index + dias_visualizar]
                    valores_prediccion = forecast['yhat'].tolist()[start_index:start_index + dias_visualizar]

                    # ASIGNAR LAS PREDICCIONES AL CONTEXTO
                    context['fechas_prediccion'] = json.dumps(fechas_prediccion)
                    context['valores_prediccion'] = json.dumps(valores_prediccion)
                else:
                    context['mensaje'] = "No hay suficientes registros para predicciones."
            else:
                context['mensaje'] = "No hay suficientes registros para predicciones."
        else:
            context['mensaje'] = "Seleccione un producto para visualizar la predicción."

    else:
        # SI NO HAY MOVIMIENTOS DISPONIBLES, SE MUESTRA UN MENSAJE DE ERROR
        context['mensaje'] = "No hay movimientos para el producto y período seleccionados."

    # RENDERIZAR LA PLANTILLA Y PASAR EL CONTEXTO CON LOS DATOS
    return render(request, 'app/T3_Dashboard.html', {**context, 'is_admin': is_admin})



#---------------------- CONFIGURACION ---------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@login_required
@never_cache
def T4_Settings(request):
    is_admin = request.user.profile.rol == 'administrador'
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
    # Actualización del contexto para usar ID_SUCURSAL
    context = {
        'correo': request.user.email,
        'rut': perfil.rut,
        'num': perfil.num,
        'rol': perfil.rol,
        'nombre': request.user.first_name,  
        'apellido': request.user.last_name,
        'sucursal': perfil.sucursal.id_sucursal,
        'sucursal_nom': perfil.sucursal.descripcion,
    }
    return render(request, 'app/T4_Settings.html', {**context, 'is_admin': is_admin})


#---------------------- OTROS -----------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    
# Verifica si el usuario es administrador
def es_administrador(user):
    return user.profile.rol == 'administrador'

# Template T1_STOCK
@login_required
def T1_Stock(request):
    return render(request, 'app/T1_Stock.html')

# Manejo de Stock
@csrf_exempt
def update_product_quantity(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        cantidad_cambio = int(request.POST.get('cantidad', 1))  # Cantidad específica del cambio, si la hay
        try:
            with transaction.atomic():
                producto = Producto.objects.get(id_producto=product_id)
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
                # Obtener la fecha actual
                today = timezone.now().date()  # Obtener solo la parte de la fecha
                # Filtrar movimientos por empleado, producto y tipo_movimiento en la misma fecha
                movimiento_existente = MovimientoEmpleado.objects.filter(
                    empleado=empleado,
                    producto=producto,
                    tipo_movimiento=tipo_movimiento,
                    fecha__date=today  # Filtrando solo por la fecha
                ).first()
                if movimiento_existente:
                    # Si ya existe un movimiento, acumulamos la cantidad
                    movimiento_existente.cantidad += cantidad_cambio
                    movimiento_existente.save()
                else:
                    # Si no existe, creamos un nuevo registro
                    MovimientoEmpleado.objects.create(
                        empleado=empleado,
                        producto=producto,
                        cantidad=cantidad_cambio,
                        tipo_movimiento=tipo_movimiento,
                        fecha=timezone.now()  # Guardar la fecha y hora actual
                    )
            return JsonResponse({'success': True, 'new_quantity': producto.cantidad})
        except Producto.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})