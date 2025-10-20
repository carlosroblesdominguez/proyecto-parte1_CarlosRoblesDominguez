from django.urls import path
from . import views

urlpatterns = [
    path('jugadores/', views.lista_jugadores, name='lista_jugadores'),
]