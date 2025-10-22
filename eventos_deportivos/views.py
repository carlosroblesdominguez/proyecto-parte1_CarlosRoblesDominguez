from django.shortcuts import render
from .models import *

# Create your views here.

# Vista: Lista todos los jugadores con su equipo y estadísticas

def ListaJugadores(request):
    # QuerySet optimizado
    jugadores = (
        Jugador.objects
        .select_related('estadisticas')  # OneToOne: EstadisticasJugador
        .prefetch_related('equipo_set')  # ManyToMany vía EquipoJugador
        .all()
        .order_by('nombre')
    )

    # Equivalente SQL usando raw()
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
        "jugadores": jugadores, # Para usar QuerySet optimizado
        "jugadores_sql": jugadores_sql  # Para mostrar que se puede usar raw()
    }
    return render(request, "eventos_deportivos/lista_jugadores.html", contexto)