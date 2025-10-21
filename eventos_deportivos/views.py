from django.shortcuts import render, get_object_or_404
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
        .prefetch_related("equipojugador_set__equipo") # Trae los equipos relacionados de manera eficiente
        .all()
        .order_by("nombre") # orden alfabetico
    )
    
    # Contexto con todos los jugadores
    contexto = {"jugadores": jugadores}
    return render(request, "eventos_deportivos/lista_jugadores.html", contexto)

# vista: Detalle de un jugador por ID
def detalle_jugador(request, jugador_id):
    """
    Vista que muestra todos los datos de un jugador específico,
    incluyendo estadísticas y equipos asociados.
    
    Parámetro:
    - jugador_id (int): ID del jugador a mostrar.

    Relaciones utilizadas:
    - OneToOne: estadisticas
    - ManyToMany: equipos a través de EquipoJugador

    Query SQL equivalente:
    SELECT j.id, j.nombre, j.apellido, j.fecha_nacimiento, j.posicion,
           es.partidos_jugados, es.goles, es.asistencias, es.tarjetas,
           e.nombre AS equipo, ej.fecha_ingreso, ej.capitan
    FROM eventos_deportivos_jugador j
    INNER JOIN eventos_deportivos_estadisticasjugador es ON j.estadisticas_id = es.id
    LEFT JOIN eventos_deportivos_equipojugador ej ON ej.jugador_id = j.id
    LEFT JOIN eventos_deportivos_equipo e ON ej.equipo_id = e.id
    WHERE j.id = jugador_id;
    """
    
    jugador = get_object_or_404(
        Jugador.objects
        .select_related("estadisticas")  # Relación OneToOne
        .prefetch_related("equipojugador_set__equipo"),  # Relación ManyToMany a través de EquipoJugador
        pk=jugador_id
    )
    
    contexto = {"jugador": jugador}
    return render(request, "eventos_deportivos/detalle_jugador.html", contexto)

def detalle_equipo(request, equipo_id):
    """
    Vista que muestra todos los datos de un equipo específico,
    incluyendo los jugadores asociados a través de la tabla intermedia EquipoJugador.

    Parámetro:
    - equipo_id (int): ID del equipo a mostrar.

    Relaciones utilizadas:
    - ManyToMany: jugadores a través de EquipoJugador

    Query SQL equivalente:
    SELECT e.id, e.nombre, e.ciudad, e.fundacion, e.activo,
           j.id AS jugador_id, j.nombre AS jugador_nombre, j.apellido AS jugador_apellido,
           ej.fecha_ingreso, ej.capitan
    FROM eventos_deportivos_equipo e
    LEFT JOIN eventos_deportivos_equipojugador ej ON ej.equipo_id = e.id
    LEFT JOIN eventos_deportivos_jugador j ON ej.jugador_id = j.id
    WHERE e.id = equipo_id;
    """
    
    equipo = get_object_or_404(
        Equipo.objects.prefetch_related('equipojugador_set__jugador'),
        pk=equipo_id
    )
    
    contexto = {"equipo": equipo}
    return render(request, "eventos_deportivos/detalle_equipo.html", contexto)

def lista_partidos(request):
    """
    Vista que obtiene todos los partidos de la base de datos junto con los equipos local y visitante, y el torneo.

    Relaciones utilizadas:
    - ManyToOne: equipo_local, equipo_visitante, torneo

    Query SQL equivalente:
    SELECT p.id, p.fecha, p.resultado,
           el.nombre AS equipo_local, ev.nombre AS equipo_visitante,
           t.nombre AS torneo
    FROM eventos_deportivos_partido p
    INNER JOIN eventos_deportivos_equipo el ON p.equipo_local_id = el.id
    INNER JOIN eventos_deportivos_equipo ev ON p.equipo_visitante_id = ev.id
    INNER JOIN eventos_deportivos_torneo t ON p.torneo_id = t.id;
    """
    partidos = (
        Partido.objects
        .select_related("equipo_local", "equipo_visitante", "torneo")
        .all()
        .order_by("fecha")
    )
    
    contexto = {"partidos": partidos}
    return render(request, "eventos_deportivos/lista_partidos.html", contexto)