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

def detalle_equipo(request, equipo_id):
    """
    Vista que muestra todos los datos de un equipo específico,
    incluyendo los jugadores asociados a través de la tabla intermedia EquipoJugador.
    
    Se utiliza get_object_or_404 para manejar de forma segura la búsqueda:
    - Si el equipo no existe, devuelve un error 404.
    - Es más seguro que usar get(), que lanzaría una excepción si no se encuentra.
    """

    # Obtener el equipo
    equipo = get_object_or_404(
        Equipo.objects.select_related('estadio_principal'), 
        pk=equipo_id
    )

    # Obtener jugadores del equipo de manera optimizada
    jugadores_equipo = (
        EquipoJugador.objects
        .select_related('jugador')  # Relación ManyToOne hacia Jugador
        .filter(equipo=equipo)
        .order_by('fecha_ingreso')
    )

    # Equivalente SQL usando raw()
    sql = """
    SELECT ej.id, j.nombre, j.apellido, ej.fecha_ingreso, ej.capitan
    FROM eventos_deportivos_equipojugador ej
    INNER JOIN eventos_deportivos_jugador j ON ej.jugador_id = j.id
    WHERE ej.equipo_id = %s
    ORDER BY ej.fecha_ingreso;
    """
    jugadores_sql = EquipoJugador.objects.raw(sql, [equipo_id])

    contexto = {
        "equipo": equipo,
        "jugadores_equipo": jugadores_equipo,
        "jugadores_sql": jugadores_sql  # Para mostrar que se puede usar raw()
    }
    return render(request, "eventos_deportivos/detalle_equipo.html", contexto)