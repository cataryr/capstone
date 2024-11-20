from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Proveedor, Categoria, Producto
import re

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )

class ProveedorForm(forms.ModelForm):
    id_proveedor = forms.CharField(max_length=10, label='ID Proveedor', required=True)  # Agregar el campo ID Proveedor

    class Meta:
        model = Proveedor
        fields = ['id_proveedor', 'nombre_proveedor', 'telefono', 'correo_proveedor']  # Incluir el nuevo campo

    def clean_id_proveedor(self):
        id_proveedor = self.cleaned_data.get('id_proveedor').strip()
        instance = self.instance

        # Excluir el ID actual del proveedor en la verificación de duplicados
        if Proveedor.objects.filter(id_proveedor=id_proveedor).exclude(id_proveedor=instance.id_proveedor).exists():
            raise forms.ValidationError("El ID del proveedor ya está en uso.")

        return id_proveedor

    def clean_nombre_proveedor(self):
        nombre = self.cleaned_data.get('nombre_proveedor').strip().lower()
        instance = self.instance

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise forms.ValidationError("El nombre solo puede contener letras y espacios.")

        if Proveedor.objects.filter(nombre_proveedor__iexact=nombre).exclude(id_proveedor=instance.id_proveedor).exists():
            raise forms.ValidationError("Este proveedor ya existe.")
        
        return nombre

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        chile_phone_regex = r'^(\+56|56)?[2-9]\d{8}$'
        if not re.match(chile_phone_regex, telefono):
            raise forms.ValidationError("El número de teléfono no es válido para Chile.")
        return telefono

    def clean_correo_proveedor(self):
        correo = self.cleaned_data.get('correo_proveedor')

        # Verificar si el correo es None antes de aplicar strip() y lower()
        if correo:
            correo = correo.strip().lower()
        else:
            return correo  # Retorna None si no hay correo

        instance = self.instance

        if Proveedor.objects.filter(correo_proveedor__iexact=correo).exclude(id_proveedor=instance.id_proveedor).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        
        return correo

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
    
    
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre_categoria', 'descripcion']

    def clean(self):
        cleaned_data = super().clean()
        nombre_categoria = cleaned_data.get('nombre_categoria').strip().lower()
        descripcion = cleaned_data.get('descripcion').strip().lower()

        # Verificar longitud mínima y máxima
        if len(nombre_categoria) < 3:
            raise forms.ValidationError("El nombre de la categoría debe tener al menos 3 caracteres.")
        if len(nombre_categoria) > 50:
            raise forms.ValidationError("El nombre de la categoría no puede exceder los 50 caracteres.")
        
        # Validar que el nombre de la categoría solo contenga letras y espacios
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre_categoria):
            raise forms.ValidationError("El nombre de la categoría solo puede contener letras y espacios.")
        
        # Validar que la descripción solo contenga letras y espacios
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', descripcion):
            raise forms.ValidationError("La descripción solo puede contener letras y espacios.")

        # Verificar si ya existe una categoría con esa combinación de nombre y descripción
        if Categoria.objects.filter(nombre_categoria__iexact=nombre_categoria, descripcion__iexact=descripcion).exists():
            raise forms.ValidationError("La categoría con esta descripción ya existe.")
        
        # Retornamos los valores originales para mantener el formato que ingresó el usuario
        cleaned_data['nombre_categoria'] = cleaned_data.get('nombre_categoria').strip()
        cleaned_data['descripcion'] = cleaned_data.get('descripcion').strip()
        
        return cleaned_data
    

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre_producto', 'cantidad', 'id_categoria', 'id_proveedor', 'id_sucursal']  # Incluye id_sucursal
        widgets = {
            'nombre_producto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad'}),
            'id_categoria': forms.Select(attrs={'class': 'form-control'}),
            'id_proveedor': forms.Select(attrs={'class': 'form-control'}),
            'id_sucursal': forms.Select(attrs={'class': 'form-control'}),  # Asegúrate de que id_sucursal sea seleccionable
        }

    # Validación para asegurar que la cantidad sea positiva
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser un número positivo.")
        return cantidad

    # Validación para el nombre del producto
    def clean_nombre_producto(self):
        nombre_producto = self.cleaned_data.get('nombre_producto').strip()

        # Validar que el nombre del producto tenga al menos 3 caracteres
        if len(nombre_producto) < 3:
            raise forms.ValidationError("El nombre del producto debe tener al menos 3 caracteres.")

        # Validar que solo contenga letras y espacios (y caracteres con tildes)
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre_producto):
            raise forms.ValidationError("El nombre del producto solo puede contener letras y espacios.")

        return nombre_producto
    
    