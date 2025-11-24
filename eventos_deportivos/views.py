from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch, Count, Max, Q
from django.contrib import messages
from .models import *
from .forms import *

# Create your views here.
def index(request):
    """
    Página principal del proyecto.
    Muestra enlaces a todas las URLs implementadas.
    Permite búsqueda rápida para URLs que requieren parámetros.
    """
    return render(request, "eventos_deportivos/index.html")

def error_404(request, exception):
    return render(request, 'eventos_deportivos/error_404.html', status=404)

def error_500(request):
    return render(request, 'eventos_deportivos/error_500.html', status=500)

def error_403(request, exception):
    return render(request, 'eventos_deportivos/error_403.html', status=403)

def error_400(request, exception):
    return render(request, 'eventos_deportivos/error_400.html', status=400)

# ----------------------------
# URL1: Lista todos los jugadores
# ----------------------------
def lista_jugadores(request):
    """
    Vista que lista todos los jugadores con sus estadísticas y equipos.
    Incluye filtro OR para mostrar Porteros o Defensas.
    """
    # QuerySet optimizado con OR (sin usar Q)
    jugadores = Jugador.objects.filter().select_related('estadisticas')
    jugadores = (jugadores ).all().order_by('nombre')

    # Obtener equipos de cada jugador usando prefetch_related en tabla intermedia
    jugadores = jugadores.prefetch_related(
        Prefetch('equipojugador_set', queryset=EquipoJugador.objects.select_related('equipo'))
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
    #jugadores_sql = Jugador.objects.raw(sql)

    contexto = {
        "jugadores": jugadores
    }
    return render(request, "eventos_deportivos/jugadores/lista_jugadores.html", contexto)

# ----------------------------
# URL2: Detalle de un jugador
# ----------------------------
def detalle_jugador(request, jugador_id):
    """
    Vista que muestra el detalle de un jugador específico,
    incluyendo sus estadísticas y equipos asociados.
    """
    jugador = get_object_or_404(
        Jugador.objects.select_related('estadisticas'), 
        pk=jugador_id
    )

    equipos_jugador = jugador.equipojugador_set.select_related('equipo').order_by('fecha_ingreso')

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
    #jugador_sql = Jugador.objects.raw(sql)

    contexto = {
        "jugador": jugador,
        "equipos_jugador": equipos_jugador
    }
    return render(request, "eventos_deportivos/jugadores/detalle_jugador.html", contexto)

# ----------------------------
# URL3: Detalle de un equipo
# ----------------------------
def detalle_equipo(request, equipo_id):
    """
    Vista que muestra todos los datos de un equipo específico,
    incluyendo los jugadores asociados.
    """
    equipo = get_object_or_404(
        Equipo.objects.select_related('estadio_principal'), 
        pk=equipo_id
    )

    # Obtener jugadores asociados evitando *_set
    jugadores_equipo = EquipoJugador.objects.filter(equipo=equipo).select_related('jugador').order_by('fecha_ingreso')

    # Equivalente SQL usando raw()
    sql = """
    SELECT ej.id, j.nombre, j.apellido, ej.fecha_ingreso, ej.capitan
    FROM eventos_deportivos_equipojugador ej
    INNER JOIN eventos_deportivos_jugador j ON ej.jugador_id = j.id
    WHERE ej.equipo_id = %s
    ORDER BY ej.fecha_ingreso;
    """
    #jugadores_sql = EquipoJugador.objects.raw(sql, [equipo_id])

    contexto = {
        "equipo": equipo,
        "jugadores_equipo": jugadores_equipo
    }
    return render(request, "eventos_deportivos/detalle_equipo.html", contexto)

# ----------------------------
# URL4: Lista de partidos
# ----------------------------
def lista_partidos(request):
    """
    Vista que muestra todos los partidos con equipos y torneo.
    Incluye aggregate (conteo total de partidos y fecha última).
    """
    partidos = Partido.objects.select_related('equipo_local', 'equipo_visitante', 'torneo').order_by('fecha')

    # Aggregate
    stats = Partido.objects.aggregate(total_partidos=Count('id'), ultimo_partido=Max('fecha'))

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
    #partidos_sql = Partido.objects.raw(sql)

    contexto = {
        "partidos": partidos,
        "stats": stats
    }
    return render(request, "eventos_deportivos/lista_partidos.html", contexto)

# ----------------------------
# URL5: Detalle de un partido
# ----------------------------
def detalle_partido(request, partido_id):
    """
    Vista que muestra los datos de un partido, incluyendo árbitros.
    """
    partido = get_object_or_404(
        Partido.objects.select_related('equipo_local', 'equipo_visitante', 'torneo'),
        pk=partido_id
    )

    # Mejor filtrado ManyToMany: arbitros del partido
    arbitros = Arbitro.objects.filter(partidos=partido)

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
    #partido_sql = Partido.objects.raw(sql, [partido_id])

    contexto = {
        "partido": partido,
        "arbitros": arbitros
    }
    return render(request, "eventos_deportivos/detalle_partido.html", contexto)

# ----------------------------
# URL6: Lista de equipos
# ----------------------------
def lista_equipos(request):
    """
    Muestra todos los equipos, incluyendo equipos sin estadio (None).
    """
    equipos = Equipo.objects.select_related('estadio_principal').prefetch_related('jugadores').filter(estadio_principal__isnull=True).order_by('nombre')
    
    # Equivalente SQL usando raw()
    sql = """
    SELECT e.id, e.nombre, e.ciudad, e.fundacion, e.activo,
           ej.jugador_id, j.nombre as jugador_nombre, j.apellido as jugador_apellido
    FROM eventos_deportivos_equipo e
    LEFT JOIN eventos_deportivos_equipojugador ej ON ej.equipo_id = e.id
    LEFT JOIN eventos_deportivos_jugador j ON j.id = ej.jugador_id
    ORDER BY e.nombre;
    """
    #equipos_sql = Equipo.objects.raw(sql)
    
    contexto = {
        "equipos": equipos
    }
    return render(request, "eventos_deportivos/lista_equipos.html", contexto)

# ----------------------------
# URL7: Detalle de torneos por nombre (r_path)
# ----------------------------
def detalle_torneo(request, nombre_torneo):
    """
    Muestra todos los torneos que coincidan con el nombre.
    """
    torneos = Torneo.objects.filter(nombre=nombre_torneo).all().order_by('fecha_inicio').prefetch_related(
        Prefetch('partido_set', queryset=Partido.objects.select_related('equipo_local', 'equipo_visitante'))
    )

    # Equivalente SQL usando raw()
    sql = f"""
    SELECT t.id, t.nombre, t.pais, t.fecha_inicio, t.fecha_fin,
           p.id AS partido_id, p.resultado, p.fecha,
           el.nombre AS equipo_local, ev.nombre AS equipo_visitante
    FROM eventos_deportivos_torneo t
    LEFT JOIN eventos_deportivos_partido p ON p.torneo_id = t.id
    LEFT JOIN eventos_deportivos_equipo el ON p.equipo_local_id = el.id
    LEFT JOIN eventos_deportivos_equipo ev ON p.equipo_visitante_id = ev.id
    WHERE t.nombre = '{nombre_torneo}'
    ORDER BY t.fecha_inicio;
    """
    #torneos_sql = Torneo.objects.raw(sql)

    contexto = {
        "torneos": torneos
    }
    return render(request, "eventos_deportivos/detalle_torneo.html", contexto)

# ----------------------------
# URL8: Lista de torneos
# ----------------------------
def lista_torneos(request):
    """
    Lista todos los torneos con sus partidos y equipos.
    """
    torneos = Torneo.objects.prefetch_related(
        Prefetch('partido_set', queryset=Partido.objects.select_related('equipo_local', 'equipo_visitante'))
    ).all().order_by('fecha_inicio')

    contexto = {
        "torneos": torneos
    }
    return render(request, "eventos_deportivos/lista_torneos.html", contexto)

# ----------------------------
# URL9: Detalle de árbitro en un torneo
# ----------------------------
def detalle_arbitro_torneo(request, arbitro_id, torneo_id):
    """
    Detalle de un árbitro y sus partidos en un torneo.
    """
    arbitro = get_object_or_404(Arbitro, pk=arbitro_id)
    partidos = arbitro.partidos.filter(torneo_id=torneo_id).select_related('equipo_local', 'equipo_visitante', 'torneo').order_by('fecha')

    contexto = {
        "arbitro": arbitro,
        "partidos": partidos
    }
    return render(request, "eventos_deportivos/detalle_arbitro_torneo.html", contexto)

# ----------------------------
# URL10: Lista de Sponsors
# ----------------------------
def lista_sponsors(request, pais, monto_min):
    """
    Lista todos los sponsors filtrando por país y monto, y usando ManyToMany para equipos.
    """
    sponsors = Sponsor.objects.filter(pais=pais).filter(monto__gte=monto_min).all().prefetch_related('equipos').order_by('nombre')

    # Equivalente SQL usando raw()
    sql = f"""
    SELECT s.id, s.nombre, s.monto, s.pais, e.id AS equipo_id, e.nombre AS equipo_nombre
    FROM eventos_deportivos_sponsor s
    LEFT JOIN eventos_deportivos_sponsor_equipos se ON s.id = se.sponsor_id
    LEFT JOIN eventos_deportivos_equipo e ON se.equipo_id = e.id
    WHERE s.pais = '{pais}' AND s.monto >= {monto_min}
    ORDER BY s.nombre;
    """
    #sponsors_sql = Sponsor.objects.raw(sql)

    contexto = {
        "sponsors": sponsors
    }
    return render(request, "eventos_deportivos/lista_sponsors.html", contexto)

# ----------------------------
# FORMULARIOS
# ----------------------------
# CRUD Jugador
# ----------------------------

# CREAR
def jugador_create_valid(formulario):
    # Valida y guarda el formulario de jugador junto con sus estadísticas.
    # Devuelve True si se guardó correctamente, False si hubo error.

    jugador_creado = False
    # Comprueba si el formulario es valido
    if formulario.is_valid():
        try:
            # Crear la estadística
            estadisticas = EstadisticasJugador.objects.create(
                partidos_jugados=formulario.cleaned_data['partidos_jugados'],
                goles=formulario.cleaned_data['goles'],
                asistencias=formulario.cleaned_data['asistencias'],
                tarjetas=formulario.cleaned_data['tarjetas']
            )
            # Guarda el jugador en la base de datos
            # Crear el jugador asignando la estadística
            formulario = formulario.save(commit=False)
            formulario.estadisticas = estadisticas
            formulario.save()
            
            jugador_creado = True
        except Exception as e:
            print("Error al guardar usuario: ", e)
    else:
        print("Formulario no valido: ", formulario.errors)
    return jugador_creado

def jugador_create(request):
    # si la peticion es GET se crea el formulario vacio
    # en el caso de set POST se crea el formulario con datos
    datosFormulario = None
    if request.method == "POST":
        datosFormulario = request.POST
        
    formulario = JugadorModelForm(datosFormulario)
    
    if (request.method == "POST"):
        jugador_creado = jugador_create_valid(formulario)
        if(jugador_creado):
            messages.success(request, 'Se a creado el jugador'+formulario.cleaned_data.get('nombre')+" correctamente")
            return redirect("lista_jugadores")
    return render(request, 'eventos_deportivos/jugadores/jugador_create.html',{"formulario":formulario})

# LEER
def jugador_buscar(request):
    formulario=BusquedaJugadorForm(request.GET)
    
    if formulario.is_valid():
        texto=formulario.cleaned_data.get("nombreBusqueda")
        jugadores=Jugador.objects.select_related("estadisticas")
        jugadores=jugadores.filter(Q(nombre__icontains=texto)|Q(apellido__icontains=texto)).all()
        return render(request, 'eventos_deportivos/jugadores/jugador_buscar.html', {"jugadores":jugadores,"nombre_busqueda":texto})
    
    if("HTTP_REFERER" in request.META):
        return redirect(request.META["HTTP_REFERER"])
    else:
        return redirect("index")

# EDITAR/ACTUALIZAR
def jugador_editar(request,jugador_id):
    jugador = Jugador.objects.get(id=jugador_id)
    
    datosFormulario=None
    
    if request.method=="POST":
        datosFormulario=request.POST
        
    formulario=JugadorModelForm(datosFormulario,instance=jugador)
    
    if (request.method=="POST"):
        if formulario.is_valid():
            formulario.save()
            try:
                formulario.save()
                return redirect('lista_jugadores')
            except Exception as e:
                pass
    return render(request, 'eventos_deportivos/jugadores/jugador_editar.html',{"formulario":formulario,"jugador":jugador})

# ELIMINAR
def jugador_eliminar(request,jugador_id):
    jugador=Jugador.objects.get(id=jugador_id)
    try:
        jugador.delete()
    except:
        pass
    return redirect('lista_jugadores')