from django.urls import path
from django.views.generic import RedirectView
from .views import custom_password_reset_done
from .views import home, password_reset_confirm, password_reset_request, T1_Stock, T2_Employees, T3_Dashboard, T4_Settings, CustomLoginView, T2_Employees_List, T2_Employees_Edit, T2_Employees_Delete, T1_Producto, T1_Categoria, T1_Proveedor, T1_edit_proveedor, eliminar_proveedor, T1_Edit_Categoria, eliminar_categoria, T1_Edit_Producto, eliminar_producto, update_product_quantity

urlpatterns = [
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/password_reset/', password_reset_request, name='password_reset_request'),
    path('accounts/password_reset/done/', custom_password_reset_done, name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    
    path('home/', home, name="home"),
    path('T1_Producto/', T1_Producto, name='T1_Producto'),
    path('T1_Edit_Producto/editar/<int:producto_id>/', T1_Edit_Producto, name='editar_producto'),
    path('T1_Edit_Producto/eliminar/<int:producto_id>/', eliminar_producto, name='eliminar_producto'),
    path('update-product-quantity/', update_product_quantity, name='update_product_quantity'), 
    
    # Rutas categorias
    path('T1_Edit_Categoria/editar/<int:categoria_id>/', T1_Edit_Categoria, name='editar_categoria'),
    path('T1_Edit_Categoria/eliminar/<int:categoria_id>/', eliminar_categoria, name='eliminar_categoria'),
    path('T1_Categoria/', T1_Categoria, name='T1_Categoria'),
    
    # Rutas proveedor
    path('T1_Proveedor/', T1_Proveedor, name='T1_Proveedor'),
     path('T1_edit_proveedor/editar/<str:id_proveedor>/', T1_edit_proveedor, name='editar_proveedor'),
    path('T1_edit_proveedor/eliminar/<str:id_proveedor>/', eliminar_proveedor, name='eliminar_proveedor'),
    
    # Rutas empleados
    path('T2_Employees_List/', T2_Employees_List, name="T2_Employees_List"),  
    path('T2_Employees/', T2_Employees, name="T2_Employees"),
    path('T2_Employees/editar/<int:id>/', T2_Employees_Edit, name='T2_Employees_Edit'),
    path('T2_Employees/eliminar/<int:id>/', T2_Employees_Delete, name='T2_Employees_Delete'), 
    path('T3_Dashboard/', T3_Dashboard, name="T3_Dashboard"), 
    path('T4_Settings/', T4_Settings, name="T4_Settings"),
]