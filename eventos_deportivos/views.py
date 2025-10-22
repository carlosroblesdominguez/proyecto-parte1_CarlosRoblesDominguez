from django.shortcuts import render, get_object_or_404
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

def detalle_jugador(request, jugador_id):
    """
    Vista que muestra el detalle de un jugador específico,
    incluyendo sus estadísticas y los equipos a los que ha pertenecido.
    
    """
    # Obtener el jugador con sus estadísticas
    jugador = get_object_or_404(
        Jugador.objects.select_related('estadisticas'),
        pk=jugador_id
    )

    # Obtener equipos del jugador mediante la tabla intermedia
    equipos_jugador = EquipoJugador.objects.filter(jugador=jugador).select_related('equipo')

    # Raw SQL equivalente
    sql = f"""
    SELECT j.id, j.nombre, j.apellido, j.fecha_nacimiento, j.posicion,
           es.partidos_jugados, es.goles, es.asistencias, es.tarjetas,
           e.id AS equipo_id, e.nombre AS equipo_nombre, ej.fecha_ingreso, ej.capitan
    FROM eventos_deportivos_jugador j
    INNER JOIN eventos_deportivos_estadisticasjugador es ON j.estadisticas_id = es.id
    LEFT JOIN eventos_deportivos_equipojugador ej ON ej.jugador_id = j.id
    LEFT JOIN eventos_deportivos_equipo e ON ej.equipo_id = e.id
    WHERE j.id = {jugador_id};
    """
    jugador_sql = Jugador.objects.raw(sql)

    contexto = {
        "jugador": jugador,
        "equipos_jugador": equipos_jugador,
        "jugador_sql": jugador_sql
    }
    return render(request, "eventos_deportivos/detalle_jugador.html", contexto)

