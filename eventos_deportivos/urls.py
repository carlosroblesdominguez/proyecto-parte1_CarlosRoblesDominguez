from django.urls import path
from . import views

urlpatterns = [
    # URL1: Lista todos los jugadores
    path('jugadores/', views.lista_jugadores, name='lista_jugadores'),
    path('jugadores/<int:jugador_id>/', views.detalle_jugador, name='detalle_jugador'), #URL2 Detalles de un jugador
    path('equipos/<int:equipo_id>/', views.detalle_equipo, name='detalle_equipo'),  # URL3 detalles de un equipo
    path('partidos/', views.lista_partidos, name='lista_partidos'), # URL4 Lista de partidos
    path('partidos/<int:partido_id>/', views.detalle_partido, name='detalle_partido'), # URL5 Detalles de un partido
    path('equipos/', views.lista_equipos, name='lista_equipos'), #URL6 Lista de equipos
]