from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from app.views import login_view, stock, bi, config, employee, home, logout_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('stock/', stock, name='stock'),
    path('bi/', bi, name='bi'),
    path('config/', config, name='config'),
    path('employee/', employee, name='employee'),
    path('home/', home, name='home'),
    path('logout/', logout_view, name='logout'),

    # Redirigir la raíz (/) al login
    path('', lambda request: redirect('login')),  # Redirige al login
]
