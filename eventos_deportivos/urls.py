from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Página principal
    path('jugadores/', views.lista_jugadores, name='lista_jugadores'), # URL1: Lista todos los jugadores
    path('jugadores/<int:jugador_id>/', views.detalle_jugador, name='detalle_jugador'), #URL2 Detalles de un jugador
    path('equipos/<int:equipo_id>/', views.detalle_equipo, name='detalle_equipo'),  # URL3 detalles de un equipo
    path('partidos/', views.lista_partidos, name='lista_partidos'), # URL4 Lista de partidos
    path('partidos/<int:partido_id>/', views.detalle_partido, name='detalle_partido'), # URL5 Detalles de un partido
    path('equipos/', views.lista_equipos, name='lista_equipos'), #URL6 Lista de equipos
    path('torneos/<str:nombre_torneo>/', views.detalle_torneo, name='detalle_torneo'), #URL7 detalle un torneo (r_path)
    path('torneos/', views.lista_torneos, name='lista_torneos'), # URL8 lista de torneos
    path('arbitros/<int:arbitro_id>/torneo/<int:torneo_id>/', views.detalle_arbitro_torneo, name='detalle_arbitro_torneo'), # URL9: Detalle de un árbitro en un torneo específico
    path('sponsors/<str:pais>/<int:monto_min>/', views.lista_sponsors, name='lista_sponsors'), # URL10: Lista de Sponsors filtrando por país y monto
]