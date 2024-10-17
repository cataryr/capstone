from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Sucursal(models.Model):
    NOMBRES_SUCURSALES = [
        ('cafeteria', 'Cafetería'),
        ('heladeria', 'Heladería'),
    ]

    nombre = models.CharField(max_length=20, choices=NOMBRES_SUCURSALES, unique=True)
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return self.get_nombre_display()


class Profile(models.Model):
    USER_TYPES = [
        ('empleado', 'Empleado'),
        ('administrador', 'Administrador'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=20)
    num = models.CharField(max_length=20)
    rol = models.CharField(max_length=20, choices=USER_TYPES, default='empleado')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.sucursal.nombre if self.sucursal else 'Sin Sucursal'}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
        
class Proveedor(models.Model):
    nombre_proveedor = models.CharField(max_length=128)
    telefono = models.CharField(max_length=20)  
    correo_proveedor = models.EmailField(max_length=250)
    
    def save(self, *args, **kwargs):
        # Normalizar el nombre antes de guardar: por ejemplo, convertir a minúsculas
        self.nombre_proveedor = self.nombre_proveedor.strip().lower()
        super(Proveedor, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre_proveedor 

class Categoria(models.Model):
    nombre_categoria = models.CharField(max_length=128)
    descripcion = models.CharField(max_length=500, blank=True)  # La descripción puede ser opcional
    
    def __str__(self):
        if self.descripcion:
            return f"{self.nombre_categoria} - {self.descripcion}"
        return self.nombre_categoria
    
class Producto(models.Model):
    nombre_producto = models.CharField(max_length=128)
    cantidad = models.IntegerField()
    id_categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    fecha_entrada = models.DateField(auto_now_add=True)
    id_proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_producto
    
class MovimientoEmpleado(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ('agregar', 'Agregar'),
        ('restar', 'Restar'),
    ]

    empleado = models.ForeignKey('Profile', on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO_CHOICES)
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.empleado.user.username} {self.tipo_movimiento} {self.cantidad} de {self.producto.nombre_producto} el {self.fecha}"
    
    class Meta:
        permissions = [
            ("view_movimiento_empleado_history", "Puede ver el historial de movimientos de empleados")
        ]