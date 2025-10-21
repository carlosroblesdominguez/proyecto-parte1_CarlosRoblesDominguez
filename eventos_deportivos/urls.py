from django.urls import path
from . import views

urlpatterns = [
    path('jugadores/', views.lista_jugadores, name='lista_jugadores'),
    path('jugadores/<int:jugador_id>/', views.detalle_jugador, name='detalle_jugador'),
    path('equipos/<int:equipo_id>/', views.detalle_equipo, name='detalle_equipo'),
    path('partidos/', views.lista_partidos, name='lista_partidos')
]