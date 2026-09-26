from django.urls import path
from . import views

urlpatterns = [
    # Al dejar la ruta vacía '', esta será la página de inicio
    path('', views.catalogo, name='catalogo'),
]
