from django.urls import path
from . import views

urlpatterns = [
    # URL 1: Listado de jugadores
    path('jugadores/', views.ListaJugadores, name='lista_jugadores.html'),
]