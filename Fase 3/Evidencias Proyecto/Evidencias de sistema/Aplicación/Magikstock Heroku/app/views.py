import json
from datetime import datetime, timedelta

from django.urls import reverse
import numpy as np
import pandas as pd
from django.conf import settings
from prophet import Prophet
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from .forms import PasswordResetForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.db.models import Sum, Case, When, IntegerField, Q
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from .decorators import admin_required
from .forms import ProveedorForm, CategoriaForm, ProductoForm
from .models import Profile, Sucursal, Proveedor, Categoria, Producto, MovimientoEmpleado
from .forms import CustomAuthenticationForm, SetPasswordForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes

#---------------------- LOGIN -----------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm

    def form_invalid(self, form):
        return redirect(f"{self.request.path}?error=1")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
from django.core.mail import EmailMultiAlternatives

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            user = User.objects.get(username=username)

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain

            reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            protocol = 'https' if request.is_secure() else 'http'
            full_reset_url = f"{protocol}://{domain}{reset_url}"

            subject = "Restablecer tu contraseña"
            html_message = render_to_string("registration/password_reset_email.html", {
                'username': user.username,
                'reset_url': full_reset_url,
                'site_name': get_current_site(request).name,
                'uid': uid,
                'token': token,
                'protocol': protocol,
                'domain': domain,
            })
            text_message = f"""
Hola {user.username},

Recibimos una solicitud para restablecer tu contraseña en {get_current_site(request).name}.
Haz clic en el siguiente enlace para restablecer tu contraseña:

{full_reset_url}

Si no realizaste esta solicitud, puedes ignorar este mensaje.
            """

            email = EmailMultiAlternatives(
                subject,
                text_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

            return redirect("password_reset_done")
    else:
        form = PasswordResetForm()

    return render(request, 'registration/password_reset_request.html', {'form': form})



def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode('utf-8')
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                user.set_password(new_password)
                user.save()

                messages.success(request, "Contraseña restablecida con éxito. Ahora puedes iniciar sesión.")
                return redirect("login")
        else:
            form = SetPasswordForm()

        return render(request, 'registration/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "El enlace de restablecimiento de contraseña no es válido o ha caducado.")
        return redirect("password_reset_request")
    
def custom_password_reset_done(request):
    return render(request, 'registration/password_reset_done.html')


#---------------------- HOME ------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@login_required
def home(request):
    is_admin = request.user.profile.rol == 'administrador'

    
    productos_bajo_stock_qs = Producto.objects.filter(cantidad__lt=5).order_by('nombre_producto')
    productos_bajo_stock_dict = defaultdict(list)
    for producto in productos_bajo_stock_qs:
        productos_bajo_stock_dict[producto.id_proveedor.nombre_proveedor].append(producto)
    
    
    productos_bajo_stock = sorted(
        [(proveedor, sorted(productos, key=lambda p: p.nombre_producto)) for proveedor, productos in productos_bajo_stock_dict.items()],
        key=lambda x: x[0]
    )

    movimientos = empleados = sucursales = None
    empleado_id = sucursal_id = None

    
    fecha_hoy = timezone.now().date()
    fecha_3_dias = fecha_hoy - timedelta(days=3)
    fecha_inicio = fecha_3_dias
    fecha_fin = fecha_hoy

    if is_admin:
        movimientos = MovimientoEmpleado.objects.all()

        
        if request.GET.get('clear_filters'):  
            fecha_inicio = fecha_3_dias
            fecha_fin = fecha_hoy
        else:
            
            fecha_inicio = request.GET.get('fecha_inicio', fecha_3_dias)
            fecha_fin = request.GET.get('fecha_fin', fecha_hoy)

        try:
            
            if isinstance(fecha_inicio, str):
                fecha_inicio = timezone.make_aware(datetime.strptime(fecha_inicio, "%Y-%m-%d"))
            if isinstance(fecha_fin, str):
                fecha_fin = timezone.make_aware(datetime.strptime(fecha_fin, "%Y-%m-%d"))

            movimientos = movimientos.filter(fecha__range=[fecha_inicio, fecha_fin])
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
    
    
    proveedor_id = request.GET.get('proveedor')
    sucursal_id = request.GET.get('sucursal')
    
   
    productos = Producto.objects.all().order_by('nombre_producto')

    if proveedor_id:
        productos = productos.filter(id_proveedor=proveedor_id)
    if sucursal_id:
        productos = productos.filter(id_sucursal=sucursal_id)
        
    
    proveedores = Proveedor.objects.all().order_by('nombre_proveedor')
    sucursales = Sucursal.objects.all().order_by('descripcion')

    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)  
            
            if not producto.id_sucursal:
                producto.id_sucursal = Sucursal.objects.first()  
            producto.save()  
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
        'sucursales': sucursales,
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
            return redirect('T1_Categoria')  
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = CategoriaForm()
    categorias = Categoria.objects.all()  
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
            return redirect('T1_Categoria') 
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'app/T1_Edit_Categoria.html', {'form': form, 'categoria': categoria, 'is_admin': is_admin})

@login_required
@admin_required
def eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id_categoria=categoria_id)
    
   
    no_clasificado = Categoria.objects.get(id_categoria=5)  
    
    
    Producto.objects.filter(id_categoria=categoria).update(id_categoria=no_clasificado)
    
    categoria.delete()
    messages.success(request, "Categoría eliminada correctamente y los productos relacionados han sido actualizados a 'No clasificado'.")
    return redirect('T1_Categoria')


#---------------------- PROVEEDORES -----------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@login_required
def T1_Proveedor(request):
    is_admin = request.user.profile.rol == 'administrador'
    
    
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor registrado correctamente.")
            return redirect('T1_Proveedor')
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
            return redirect('T1_Proveedor')  
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'app/T1_edit_proveedor.html', {'form': form, 'proveedor': proveedor, 'is_admin': is_admin})

@login_required
@admin_required
def eliminar_proveedor(request, id_proveedor):
    proveedor = get_object_or_404(Proveedor, id_proveedor=id_proveedor)
    
    
    sin_proveedor = Proveedor.objects.get(id_proveedor="P000")
    
   
    Producto.objects.filter(id_proveedor=proveedor).update(id_proveedor=sin_proveedor)
    
    
    proveedor.delete()
    messages.success(request, "Proveedor eliminado correctamente, y los productos relacionados han sido actualizados a 'sin proveedor'.")
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
        empleado.user.delete()  
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

       
        sucursal = Sucursal.objects.filter(id_sucursal=sucursal_id).first()  
       
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={'rut': rut, 'num': num, 'rol': rol, 'sucursal': sucursal}
        )
        if not created:  
            profile.rut = rut
            profile.num = num
            profile.rol = rol
            profile.sucursal = sucursal  
            profile.save()
        messages.success(request, "Usuario registrado exitosamente.")
        return redirect('T2_Employees')
    
    sucursales = Sucursal.objects.all()
    return render(request, 'app/T2_Employees.html', {'sucursales': sucursales, 'is_admin': is_admin})


#---------------------- DASHBOARD -------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



@login_required
def T3_Dashboard(request):
    context = {}
    is_admin = request.user.profile.rol == 'administrador'

    producto_id = request.GET.get('producto')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    periodo = int(request.GET.get('periodo', 0))  

   
    if not fecha_inicio and not fecha_fin:
        if MovimientoEmpleado.objects.exists():
            fecha_fin = timezone.now().date()
            fecha_fin += timedelta(days=1)
            fecha_inicio = fecha_fin - timedelta(days=90)

    if fecha_inicio and not fecha_fin:
        fecha_inicio = parse_date(fecha_inicio)
        fecha_fin = timezone.now().date()

    if fecha_fin and not fecha_inicio:
        fecha_fin = parse_date(fecha_fin)
        fecha_inicio = fecha_fin - timedelta(days=30)

    try:
        if fecha_inicio and fecha_fin:
            fecha_inicio = parse_date(fecha_inicio) if isinstance(fecha_inicio, str) else fecha_inicio
            fecha_fin = parse_date(fecha_fin) if isinstance(fecha_fin, str) else fecha_fin

            
            if fecha_inicio > fecha_fin:
                context['mensaje'] = "La fecha de inicio no puede ser posterior a la fecha de fin."
                return render(request, 'app/T3_Dashboard.html', {**context, 'is_admin': is_admin})
    except ValueError:
        context['mensaje'] = "Una o ambas fechas son inválidas."
        return render(request, 'app/T3_Dashboard.html', {**context, 'is_admin': is_admin})

    
    filtros_historico = Q()
    if producto_id:
        filtros_historico &= Q(producto__id_producto=producto_id)
    if fecha_inicio:
        filtros_historico &= Q(fecha__gte=fecha_inicio)
    if fecha_fin:
        filtros_historico &= Q(fecha__lte=fecha_fin)

   
    movimientos_historicos = MovimientoEmpleado.objects.filter(filtros_historico).annotate(
        fecha_agrupada=TruncDate('fecha')
    ).values('fecha_agrupada').annotate(
        total_agregar=Sum(Case(
            When(tipo_movimiento='agregar', then='cantidad'),
            default=0,
            output_field=IntegerField()
        )),
        total_restar=Sum(Case(
            When(tipo_movimiento='restar', then='cantidad'),
            default=0,
            output_field=IntegerField()
        ))
    ).order_by('fecha_agrupada')
    context = {
        'productos': Producto.objects.filter(cantidad__gt=0).order_by('nombre_producto'),
        'fechas': json.dumps([]),
        'total_agregar': json.dumps([]),
        'total_restar': json.dumps([]),
        'fechas_prediccion_hasta_hoy': json.dumps([]),
        'valores_prediccion_hasta_hoy': json.dumps([]),
        'fechas_prediccion_futura': json.dumps([]),
        'valores_prediccion_futura': json.dumps([]),
        'mensaje': ""
    }
    if movimientos_historicos.exists():
        fechas = [mov['fecha_agrupada'].strftime('%Y-%m-%d') for mov in movimientos_historicos]
        total_agregar = [mov['total_agregar'] for mov in movimientos_historicos]
        total_restar = [mov['total_restar'] for mov in movimientos_historicos]

        context['fechas'] = json.dumps(fechas)
        context['total_agregar'] = json.dumps(total_agregar)
        context['total_restar'] = json.dumps(total_restar)

        if producto_id:
            movimientos_historicos_producto = MovimientoEmpleado.objects.filter(producto_id=producto_id)

            if movimientos_historicos_producto.count() >= 90:
                movimientos_restar = movimientos_historicos_producto.filter(tipo_movimiento='restar').values('fecha', 'cantidad')
                df_movimientos_restar = pd.DataFrame(movimientos_restar)

                if 'fecha' in df_movimientos_restar.columns:
                    
                    df_prophet = df_movimientos_restar.rename(columns={'fecha': 'ds', 'cantidad': 'y'})
                    df_prophet['ds'] = pd.to_datetime(df_prophet['ds']).dt.tz_localize(None)

                    
                    ultima_fecha_historica = df_prophet['ds'].max()
                    fecha_actual = pd.to_datetime(timezone.now().date())

                    
                    rango_actual = pd.date_range(start=ultima_fecha_historica, end=fecha_actual, freq='D')
                    df_rango = pd.DataFrame({'ds': rango_actual, 'y': 0})
                    df_prophet = pd.concat([df_prophet, df_rango]).drop_duplicates(subset='ds').reset_index(drop=True)

                    
                    model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
                    model.fit(df_prophet)

                    
                    dias_futuros = 7 * periodo if periodo > 0 else 32
                    future = model.make_future_dataframe(periods=dias_futuros)
                    forecast = model.predict(future)

                    
                    prediccion_hasta_hoy = forecast[(forecast['ds'] > ultima_fecha_historica) & (forecast['ds'] <= fecha_actual)]
                    prediccion_futura = forecast[forecast['ds'] > fecha_actual]

                    fechas_prediccion_hasta_hoy = prediccion_hasta_hoy['ds'].dt.strftime('%Y-%m-%d').tolist()
                    valores_prediccion_hasta_hoy = prediccion_hasta_hoy['yhat'].tolist()

                    fechas_prediccion_futura = prediccion_futura['ds'].dt.strftime('%Y-%m-%d').tolist()
                    valores_prediccion_futura = prediccion_futura['yhat'].tolist()

                    context['fechas_prediccion_hasta_hoy'] = json.dumps(fechas_prediccion_hasta_hoy)
                    context['valores_prediccion_hasta_hoy'] = json.dumps(valores_prediccion_hasta_hoy)
                    context['fechas_prediccion_futura'] = json.dumps(fechas_prediccion_futura)
                    context['valores_prediccion_futura'] = json.dumps(valores_prediccion_futura)
                else:
                    context['mensaje'] = "No hay suficientes registros para predicciones."
            else:
                context['mensaje'] = "No hay suficientes registros para predicciones."
        else:
            context['mensaje'] = "Seleccione un producto para visualizar la predicción."
    else:
        context['mensaje'] = "No hay movimientos para el producto y período seleccionados."

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
        numero = request.POST.get('numero').strip() 
        correo = request.POST.get('correo').strip()
        rut = request.POST.get('rut').strip()  
    
        
        if not nombre or not apellido or not numero or not correo or not rut:
            messages.error(request, "No puedes dejar campos vacíos.")
            return redirect('T4_Settings')
        if not nombre.isalpha() or not apellido.isalpha():
            messages.error(request, "El nombre y el apellido solo pueden contener letras.")
            return redirect('T4_Settings')
        if not numero.isdigit() or len(numero) != 9:
            messages.error(request, "El número debe contener solo dígitos y tener 9 caracteres.")
            return redirect('T4_Settings')
        
        try:
            validate_email(correo)
        except ValidationError:
            messages.error(request, "El correo no es válido.")
            return redirect('T4_Settings')
        
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
        'sucursal': perfil.sucursal.id_sucursal,
        'sucursal_nom': perfil.sucursal.descripcion,
    }
    return render(request, 'app/T4_Settings.html', {**context, 'is_admin': is_admin})


#---------------------- OTROS -----------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    

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
        cantidad_cambio = int(request.POST.get('cantidad', 1))  
        try:
            with transaction.atomic():
                producto = Producto.objects.get(id_producto=product_id)
                empleado = request.user.profile                  
                if action == 'add':
                    producto.cantidad += cantidad_cambio
                    tipo_movimiento = 'agregar'
                elif action == 'subtract' and producto.cantidad >= cantidad_cambio:
                    producto.cantidad -= cantidad_cambio
                    tipo_movimiento = 'restar'
                else:
                    return JsonResponse({'success': False, 'error': 'Cantidad insuficiente'})
                producto.save()
                
                today = timezone.now().date()  
               
                movimiento_existente = MovimientoEmpleado.objects.filter(
                    empleado=empleado,
                    producto=producto,
                    tipo_movimiento=tipo_movimiento,
                    fecha__date=today  
                ).first()
                if movimiento_existente:
                    
                    movimiento_existente.cantidad += cantidad_cambio
                    movimiento_existente.save()
                else:
                   
                    MovimientoEmpleado.objects.create(
                        empleado=empleado,
                        producto=producto,
                        cantidad=cantidad_cambio,
                        tipo_movimiento=tipo_movimiento,
                        fecha=timezone.now()  
                    )
            return JsonResponse({'success': True, 'new_quantity': producto.cantidad})
        except Producto.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})