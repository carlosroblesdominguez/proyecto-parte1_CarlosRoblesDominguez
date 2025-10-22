from django.urls import path
from . import views

urlpatterns = [
    # URL1: Lista todos los jugadores
    path('jugadores/', views.lista_jugadores, name='lista_jugadores'),
    path('jugadores/<int:jugador_id>/', views.detalle_jugador, name='detalle_jugador')
]