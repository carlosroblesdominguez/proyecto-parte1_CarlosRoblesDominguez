from django.shortcuts import render
from .models import *

# Create your views here.

# Vista: Lista todos los jugadores con su equipo y estadísticas
def lista_jugadores(request):
    """
    Vista que obtiene todos los jugadores de la base de datos junto con sus equipos y estadísticas.
    Muestra relaciones OneToOne (Estadísticas), ManyToOne (Equipo) y los campos propios del jugador.

    Query SQL equivalente:
    SELECT j.id, j.nombre, j.edad, e.nombre AS equipo, es.goles, es.asistencias
    FROM eventos_deportivos_jugador j
    INNER JOIN eventos_deportivos_equipo e ON j.equipo_id = e.id
    INNER JOIN eventos_deportivos_estadisticas es ON es.jugador_id = j.id;
    """
    
    jugadores = (
        Jugador.objects
        .select_related("estadisticas") # Solo la relación OneToOne directa
        .prefetch_related("equiposjugador_set__equipo") # Trae los equipos relacionados de manera eficiente
        .all()
        .order_by("nombre") # orden alfabetico
    )
    
    # Contexto con todos los jugadores
    contexto = {"jugadores": jugadores}
    return render(request, "eventos_deportivos/lista_jugadores.html", contexto)