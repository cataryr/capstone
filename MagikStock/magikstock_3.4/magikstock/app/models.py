from django.db import models

class empleados(models.Model):
    RUN_CHOICES = [
        ('administrador', 'Administrador'),
        ('empleado', 'Empleado'),
    ]

    run = models.CharField(max_length=12, unique=True)  # RUN en formato de texto
    contraseña = models.CharField(max_length=128)  # Contraseña cifrada
    rol = models.CharField(max_length=13, choices=RUN_CHOICES, default='empleado')  # Campo de rol
    nombre_emp = models.CharField(max_length=50)  # Nombre del empleado
    apellidos_emp = models.CharField(max_length=50)  # Apellidos del empleado
    numero = models.CharField(max_length=15)  # Número de contacto del empleado
    correo = models.EmailField(max_length=254, unique=True)  # Correo electrónico del empleado


    def __str__(self):
        return f"{self.run} ({self.rol})"
    
    
class categoria(models.Model):
    nombre_categoria = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre_categoria
    
class proveedor(models.Model):
    nombre_proveedor = models.CharField(max_length=128)
    telefono = models.CharField(max_length=20)  # Podrías usar PhoneNumberField si necesitas validación avanzada
    correo_proveedor = models.EmailField(max_length=250)

    def __str__(self):
        return self.nombre_proveedor 


class producto(models.Model):
    nombre_producto = models.CharField(max_length=128)
    cantidad = models.IntegerField()
    id_categoria = models.ForeignKey(categoria, on_delete=models.CASCADE)
    fecha_entrada = models.DateField(auto_now_add=True)
    id_proveedor = models.ForeignKey(proveedor, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_producto 