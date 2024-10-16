# Generated by Django 5.1 on 2024-09-03 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_empleados_rol'),
    ]

    operations = [
        migrations.AddField(
            model_name='empleados',
            name='apellidos_emp',
            field=models.CharField(default='hannus', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='empleados',
            name='correo',
            field=models.EmailField(default='hannus@gmail.com', max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='empleados',
            name='nombre_emp',
            field=models.CharField(default='cristian', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='empleados',
            name='numero',
            field=models.CharField(default='12345678', max_length=15),
            preserve_default=False,
        ),
    ]
