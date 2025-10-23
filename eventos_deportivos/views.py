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

def lista_partidos(request):
    """
    Vista que muestra todos los partidos registrados en la base de datos.
    Incluye equipos local y visitante, resultado y torneo al que pertenece.
    
    Se utiliza select_related para optimizar las relaciones ManyToOne con Equipo y Torneo.
    """
    # QuerySet optimizado
    partidos = (
        Partido.objects
        .select_related('equipo_local', 'equipo_visitante', 'torneo')
        .all()
        .order_by('fecha')
    )

    # Equivalente SQL usando raw()
    sql = """
    SELECT p.id, p.fecha, p.resultado,
           el.id as equipo_local_id, el.nombre as equipo_local_nombre,
           ev.id as equipo_visitante_id, ev.nombre as equipo_visitante_nombre,
           t.id as torneo_id, t.nombre as torneo_nombre
    FROM eventos_deportivos_partido p
    INNER JOIN eventos_deportivos_equipo el ON p.equipo_local_id = el.id
    INNER JOIN eventos_deportivos_equipo ev ON p.equipo_visitante_id = ev.id
    INNER JOIN eventos_deportivos_torneo t ON p.torneo_id = t.id
    ORDER BY p.fecha;
    """
    partidos_sql = Partido.objects.raw(sql)

    contexto = {
        "partidos": partidos,         # Para usar QuerySet optimizado
        "partidos_sql": partidos_sql  # Para mostrar que se puede usar raw()
    }

    return render(request, "eventos_deportivos/lista_partidos.html", contexto)

def detalle_partido(request, partido_id):
    """
    Vista que muestra todos los datos de un partido específico,
    incluyendo equipos, resultado, fecha, torneo y árbitros.
    """

    # Obtener el partido y sus relaciones OneToOne/ForeignKey
    partido = get_object_or_404(
        Partido.objects.select_related("equipo_local", "equipo_visitante", "torneo"),
        pk=partido_id
    )

    # Obtener los árbitros que están asignados a este partido
    arbitros = partido.arbitro_set.all()  # Muchos a Muchos: Arbitro.partidos

    # SQL equivalente usando raw()
    sql = """
    SELECT p.id, p.fecha, p.resultado,
           el.nombre as equipo_local_nombre,
           ev.nombre as equipo_visitante_nombre,
           t.nombre as torneo_nombre
    FROM eventos_deportivos_partido p
    INNER JOIN eventos_deportivos_equipo el ON p.equipo_local_id = el.id
    INNER JOIN eventos_deportivos_equipo ev ON p.equipo_visitante_id = ev.id
    INNER JOIN eventos_deportivos_torneo t ON p.torneo_id = t.id
    WHERE p.id = %s;
    """
    partido_sql = Partido.objects.raw(sql, [partido_id])

    contexto = {
        "partido": partido,
        "arbitros": arbitros,
        "partido_sql": partido_sql
    }
    return render(request, "eventos_deportivos/detalle_partido.html", contexto)

def lista_equipos(request):
    """
    Vista que obtiene todos los equipos registrados en la base de datos,
    incluyendo información básica y opcionalmente número de jugadores asociados.
    
    Relaciones utilizadas:
    - ManyToMany: jugadores a través de EquipoJugador
    """
    
    # QuerySet optimizado
    equipos = (
        Equipo.objects
        .prefetch_related('jugadores')  # ManyToMany: jugadores asociados
        .all()
        .order_by('nombre')
    )
    
    # Equivalente SQL usando raw()
    sql = """
    SELECT e.id, e.nombre, e.ciudad, e.fundacion, e.activo,
           ej.jugador_id, j.nombre as jugador_nombre, j.apellido as jugador_apellido
    FROM eventos_deportivos_equipo e
    LEFT JOIN eventos_deportivos_equipojugador ej ON ej.equipo_id = e.id
    LEFT JOIN eventos_deportivos_jugador j ON j.id = ej.jugador_id
    ORDER BY e.nombre;
    """
    equipos_sql = Equipo.objects.raw(sql)
    
    contexto = {
        "equipos": equipos,           # Para usar QuerySet optimizado
        "equipos_sql": equipos_sql    # Para mostrar que se puede usar raw()
    }
    return render(request, "eventos_deportivos/lista_equipos.html", contexto)