from django.shortcuts import render
from .models import *

# Create your views here.

def lista_jugadores(request):
    """
    Vista que lista todos los jugadores con sus estadísticas y equipos.
    """

    # QuerySet optimizado
    jugadores = (
        Jugador.objects
        .select_related('estadisticas')  # OneToOne: EstadisticasJugador
        .prefetch_related('equipojugador_set')  # Trae la tabla intermedia correctamente
        .all()
        .order_by('nombre')
    )

    # SQL equivalente usando raw()
    sql = """
    SELECT j.id, j.nombre, j.apellido, j.fecha_nacimiento, j.posicion,
           es.partidos_jugados, es.goles, es.asistencias, es.tarjetas,
           e.id as equipo_id, e.nombre as equipo_nombre, ej.fecha_ingreso, ej.capitan
    FROM eventos_deportivos_jugador j
    INNER JOIN eventos_deportivos_estadisticasjugador es ON j.estadisticas_id = es.id
    LEFT JOIN eventos_deportivos_equipojugador ej ON ej.jugador_id = j.id
    LEFT JOIN eventos_deportivos_equipo e ON ej.equipo_id = e.id
    ORDER BY j.nombre;
    """
    jugadores_sql = Jugador.objects.raw(sql)

    contexto = {
        "jugadores": jugadores,
        "jugadores_sql": jugadores_sql
    }

    return render(request, "eventos_deportivos/lista_jugadores.html", contexto)