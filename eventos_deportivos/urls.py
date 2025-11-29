from django.urls import path
from . import views

urlpatterns = [
    # Página principal con enlaces a todas las vistas
    path('', views.index, name='index'),

    # Jugadores
    path('jugadores/', views.lista_jugadores, name='lista_jugadores'),                # URL1: Lista todos los jugadores
    path('jugadores/<int:jugador_id>/', views.detalle_jugador, name='detalle_jugador'), # URL2: Detalle de un jugador específico

    # Equipos
    path('equipos/', views.lista_equipos, name='lista_equipos'),                      # URL6: Lista todos los equipos
    path('equipos/<int:equipo_id>/', views.detalle_equipo, name='detalle_equipo'),    # URL3: Detalle de un equipo específico

    # Partidos
    path('partidos/', views.lista_partidos, name='lista_partidos'),                    # URL4: Lista todos los partidos
    path('partidos/<int:partido_id>/', views.detalle_partido, name='detalle_partido'), # URL5: Detalle de un partido específico

    # Torneos
    path('torneos/', views.lista_torneos, name='lista_torneos'),                      # URL8: Lista de todos los torneos
    path('torneos/<str:nombre_torneo>/', views.detalle_torneo, name='detalle_torneo'), # URL7: Detalle de un torneo por nombre

    # Árbitros
    path('arbitros/<int:arbitro_id>/torneo/<int:torneo_id>/', views.detalle_arbitro_torneo, name='detalle_arbitro_torneo'),                                              # URL9: Detalle de un árbitro en un torneo específico

    # Sponsors
    path('sponsors/<str:pais>/<int:monto_min>/', views.lista_sponsors, name='lista_sponsors'), # URL10: Lista de Sponsors filtrando por país y monto

    # Estadios
    path('estadios/', views.lista_estadios, name='lista_estadios'),

    # Formularios
    # Crear Jugador
    path('jugadores/create', views.jugador_create, name='jugador_create'),
    # Buscar Jugadores
    path('jugadores/buscar/', views.jugador_buscar, name='jugador_buscar'),
    # Actualizar Jugadores
    path('jugadores/editar/<int:jugador_id>/', views.jugador_editar, name='jugador_editar'),
    # Eliminar Jugadores
    path('jugadores/eliminar/<int:jugador_id>', views.jugador_eliminar, name='jugador_eliminar'),
    
    # Crear Equipos
    path('equipos/create', views.equipo_create, name='equipo_create'),
    # Buscar Equipos
    path('equipos/buscar/', views.equipo_buscar, name='equipo_buscar'),
    # Actualizar Equipos
    path('equipos/editar/<int:equipo_id>/', views.equipo_editar, name='equipo_editar'),
    # Eliminar Equipos
    path('equipos/eliminar/<int:equipo_id>', views.equipo_eliminar, name='equipo_eliminar'),

    # Crear Estadios
    path('estadios/create', views.estadio_create, name='estadio_create'),
    # Buscar estadios
    #path('estadio/buscar/', views.estadio_buscar, name='estadio_buscar'),
    # Actualizar Estadios
    path('estadio/editar/<int:estadio_id>/', views.estadio_editar, name='estadio_editar'),
    # Eliminar Estadios
    path('estadio/eliminar/<int:estadio_id>', views.estadio_eliminar, name='estadio_eliminar'),

]
