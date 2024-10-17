from django import forms
from .models import Proveedor, Categoria, Producto
import re

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre_proveedor', 'telefono', 'correo_proveedor']
    
    def clean_nombre_proveedor(self):
        nombre = self.cleaned_data.get('nombre_proveedor').strip().lower()  # Normalizar a minúsculas y eliminar espacios en blanco
        instance = self.instance  # Obtener la instancia actual en caso de edición
        
        # Validar que el nombre solo contenga letras y espacios
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', self.cleaned_data.get('nombre_proveedor').strip()):
            raise forms.ValidationError("El nombre solo puede contener letras y espacios.")
        
        # Verificar si ya existe un proveedor con ese nombre en minúsculas
        if Proveedor.objects.filter(nombre_proveedor__iexact=nombre).exclude(id=instance.id).exists():
            raise forms.ValidationError("Este proveedor ya existe.")
        
        return self.cleaned_data.get('nombre_proveedor').strip()  # Devolver el nombre original, con formato del usuario
    
    # Validación del número de teléfono
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        chile_phone_regex = r'^(\+56|56)?[2-9]\d{8}$'  # Regex para números de Chile
        if not re.match(chile_phone_regex, telefono):
            raise forms.ValidationError("El número de teléfono no es válido para Chile.")
        return telefono

    def clean_correo_proveedor(self):
        correo = self.cleaned_data.get('correo_proveedor').strip().lower()  # Normalizar a minúsculas
        instance = self.instance  # Obtener la instancia actual en caso de edición
        
        # Verificar si ya existe un proveedor con ese correo en minúsculas
        if Proveedor.objects.filter(correo_proveedor__iexact=correo).exclude(id=instance.id).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        
        return correo

    def clean(self):
        cleaned_data = super().clean()
        
        # Opcional: cualquier validación cruzada que desees hacer entre los campos
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
        fields = ['nombre_producto', 'cantidad', 'id_categoria', 'id_proveedor']
        widgets = {
            'nombre_producto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad'}),
            'id_categoria': forms.Select(attrs={'class': 'form-control'}),
            'id_proveedor': forms.Select(attrs={'class': 'form-control'}),
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
    
    