# Generated by Django 5.1 on 2024-10-06 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_proveedor'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_categoria', models.CharField(max_length=128)),
                ('descripcion', models.TextField(blank=True, max_length=500)),
            ],
        ),
    ]
