# Generated by Django 5.1 on 2024-08-31 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='empleados',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('run', models.CharField(max_length=12, unique=True)),
                ('contraseña', models.CharField(max_length=128)),
            ],
        ),
    ]