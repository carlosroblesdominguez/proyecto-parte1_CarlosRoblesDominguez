from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch, Count, Max, Q
from django.contrib import messages
from datetime import datetime, date, time
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.models import Group
from .models import *
from .forms import *

# Create your views here.
def index(request):
    """
    Página principal del proyecto.
    Muestra enlaces a todas las URLs implementadas.
    Permite búsqueda rápida para URLs que requieren parámetros.
    """
    formularioJ = BusquedaJugadorForm(request.GET or None)
    formularioE = BusquedaEquipoForm(request.GET or None)
    formularioES = BusquedaEstadioForm(request.GET or None)
    formularioSP = BusquedaSponsorForm(request.GET or None)
    formularioP = BusquedaPartidoForm(request.GET or None)
    formularioT = BusquedaTorneoForm(request.GET or None)
    formularioRegistro = RegistroForm(request.GET or None)
    
    if(not "fecha_inicio" in request.session):
        request.session["fecha_inicio"]=datetime.now().strftime('%d/%m/%Y %H:%M')
    
    return render(
        request, 
        "eventos_deportivos/index.html",
        {
            "formularioRegistro":formularioRegistro,
            "formularioJ":formularioJ,
            "formularioE":formularioE,
            "formularioES":formularioES,
            "formularioSP":formularioSP,
            "formularioP":formularioP,
            "formularioT":formularioT,
        }
    )

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
    return render(request, "eventos_deportivos/equipos/detalle_equipo.html", contexto)

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
    return render(request, "eventos_deportivos/partidos/lista_partidos.html", contexto)

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
    return render(request, "eventos_deportivos/partidos/detalle_partido.html", contexto)

# ----------------------------
# URL6: Lista de equipos
# ----------------------------
def lista_equipos(request):
    equipos = Equipo.objects.all()
    """
    Muestra todos los equipos, incluyendo equipos sin estadio (None).
    """
    equipos = Equipo.objects.select_related('estadio_principal').prefetch_related('jugadores').order_by('nombre')
    
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
    
    return render(request, "eventos_deportivos/equipos/lista_equipos.html", {'equipos':equipos})

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
    return render(request, "eventos_deportivos/torneos/detalle_torneo.html", contexto)

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
    return render(request, "eventos_deportivos/torneos/lista_torneos.html", contexto)

# ----------------------------
# URL9: Detalle de árbitro en un torneo <input name="nombreBusqueda" class="fomr-control me-2" type="search" placeholder="Nombre" aria-label="Search"></input>
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
def lista_sponsors(request):
    """
    Lista todos los sponsors, y usando ManyToMany para equipos.
    """
    sponsors = Sponsor.objects.prefetch_related('equipos').order_by('nombre')

    # Equivalente SQL usando raw()
    sql = f"""
    SELECT s.id, s.nombre, s.monto, s.pais, e.id AS equipo_id, e.nombre AS equipo_nombre
    FROM eventos_deportivos_sponsor s
    LEFT JOIN eventos_deportivos_sponsor_equipos se ON s.id = se.sponsor_id
    LEFT JOIN eventos_deportivos_equipo e ON se.equipo_id = e.id
    ORDER BY s.nombre;
    """
    #sponsors_sql = Sponsor.objects.raw(sql)

    contexto = {
        "sponsors": sponsors
    }
    return render(request, "eventos_deportivos/sponsors/lista_sponsors.html", contexto)

# ----------------------------
# URL: Lista de estadios
# ----------------------------
def lista_estadios(request):
    """
    Muestra todos los estadios en la página.
    """
    estadios = Estadio.objects.all().order_by('nombre')  # orden por nombre
    return render(request, "eventos_deportivos/estadios/lista_estadios.html", {'estadios': estadios})

# ----------------------------
# FORMULARIOS
# ----------------------------
# CRUD Jugador
# ----------------------------

# CREAR
def jugador_create_valid(formularioJ):
    # Valida y guarda el formulario de jugador junto con sus estadísticas.
    # Devuelve True si se guardó correctamente, False si hubo error.

    jugador_creado = False
    # Comprueba si el formulario es valido
    if formularioJ.is_valid():
        try:
            # Crear la estadística
            estadisticas = EstadisticasJugador.objects.create(
                partidos_jugados=formularioJ.cleaned_data['partidos_jugados'],
                goles=formularioJ.cleaned_data['goles'],
                asistencias=formularioJ.cleaned_data['asistencias'],
                tarjetas=formularioJ.cleaned_data['tarjetas']
            )
            # Guarda el jugador en la base de datos
            # Crear el jugador asignando la estadística
            formularioJ = formularioJ.save(commit=False) # <-- Crea el objeto del modelo con los datos validados, pero no lo guardes todavia en la BD.
            formularioJ.save()
            
            jugador_creado = True
        except Exception as e:
            print("Error al guardar jugador: ", e)
    else:
        print("Formulario no valido: ", formularioJ.errors)
    return jugador_creado

@login_required
@permission_required('eventos_deportivos.add_jugador')
def jugador_create(request):
    # si la peticion es GET se crea el formulario vacio
    # en el caso de set POST se crea el formulario con datos
    datosFormulario = None
    if request.method == "POST":
        datosFormulario = request.POST
        
    formularioJ = JugadorModelForm(datosFormulario)
    
    if (request.method == "POST"):
        jugador_creado = jugador_create_valid(formularioJ)
        if(jugador_creado):
            messages.success(request, 'Se a creado el jugador'+formularioJ.cleaned_data.get('nombre')+" correctamente")
            return redirect("lista_jugadores")
    return render(request, 'eventos_deportivos/jugadores/jugador_create.html',{"formularioJ":formularioJ})

# LEER
def jugador_buscar(request):
    mensaje_busqueda = ""
    jugadores = Jugador.objects.none() # Por defecto vacio
    formularioJ = BusquedaJugadorForm(request.GET or None)
    formularioE = BusquedaEquipoForm(request.GET or None)
    formularioES = BusquedaEstadioForm(request.GET or None)
    formularioSP = BusquedaSponsorForm(request.GET or None)
    formularioP = BusquedaPartidoForm(request.GET or None)
    formularioT = BusquedaTorneoForm(request.GET or None)
    
    if(len(request.GET)>0):
        
        if formularioJ.is_valid():
            nombreBusqueda=formularioJ.cleaned_data.get('nombreBusqueda')
            apellidoBusqueda=formularioJ.cleaned_data.get('apellidoBusqueda')
            posicionBusqueda=formularioJ.cleaned_data.get('posicionBusqueda')
            
            # --- mensaje de filtros  ---
            filtros_aplicados = []
            if nombreBusqueda:
                filtros_aplicados.append(f"Nombre contiene '{nombreBusqueda}'")
            if apellidoBusqueda:
                filtros_aplicados.append(f"Apellido contiene '{apellidoBusqueda}'")
            filtros_aplicados.append(f"Posicion = '{posicionBusqueda}'")
            mensaje_busqueda = " | ".join(filtros_aplicados)
            
            # --- Construccion del filtro ---
            filtros = Q(posicion=posicionBusqueda) # Posicion obligatoria
            if nombreBusqueda:
                filtros &= Q(nombre__icontains=nombreBusqueda)
            if apellidoBusqueda:
                filtros &= Q(apellido__icontains=apellidoBusqueda)
            
            jugadores = Jugador.objects.filter(filtros).select_related("estadisticas")
    
            return render(request, 'eventos_deportivos/jugadores/jugador_buscar.html', {"formularioJ":formularioJ,"texto_busqueda":mensaje_busqueda,"jugadores":jugadores})
    
    return render(
        request, 
        "eventos_deportivos/index.html",
        {
            "formularioJ":formularioJ,
            "formularioE":formularioE,
            "formularioES":formularioES,
            "formularioSP":formularioSP,
            "formularioP":formularioP,
            "formularioP":formularioT,
        }
    )

# EDITAR/ACTUALIZAR
@login_required
@permission_required('eventos_deportivos.change_jugador')
def jugador_editar(request,jugador_id):
    jugador = Jugador.objects.get(id=jugador_id)
    
    datosFormulario=None
    
    if request.method=="POST":
        datosFormulario=request.POST
        
    formularioJ=JugadorModelForm(datosFormulario,instance=jugador)
    
    if (request.method=="POST"):
        if formularioJ.is_valid():
            formularioJ.save()
            try:
                formularioJ.save()
                messages.success(request, 'Se ha editado el jugador'+formularioJ.cleaned_data.get('nombre')+" correctamente")
                return redirect('lista_jugadores')
            except Exception as e:
                print(e)
    return render(request, 'eventos_deportivos/jugadores/jugador_editar.html',{"formularioJ":formularioJ,"jugador":jugador})

# ELIMINAR
@login_required
@permission_required('eventos_deportivos.delete_jugador')
def jugador_eliminar(request,jugador_id):
    jugador=Jugador.objects.get(id=jugador_id)
    try:
        jugador.delete()
    except:
        pass
    return redirect('lista_jugadores')

# ----------------------------
# CRUD Equipo
# ----------------------------

# CREAR
def equipo_create_valid(formularioE):
    # Valida y guarda el formulario y los jugadores y sus datos por la tabla intermedia.
    # Devuelve True si se guardó correctamente, False si hubo error.

    equipo_creado = False
    # Comprueba si el formulario es valido
    if formularioE.is_valid():
        try:
            equipo = formularioE.save()
            jugadores_seleccionados = formularioE.cleaned_data.get('jugadores',[])
            for jugador in jugadores_seleccionados:
                EquipoJugador.objects.create(
                equipo=equipo,
                jugador=jugador,
                fecha_ingreso=date.today(),
            )
            
            equipo_creado = True
        except Exception as e:
            print("Error al guardar equipo: ", e)
    else:
        print("Formulario no valido: ", formularioE.errors)
    return equipo_creado

@login_required
@permission_required('eventos_deportivos.add_equipo')
def equipo_create(request):
    # si la peticion es GET se crea el formulario vacio
    # en el caso de set POST se crea el formulario con datos
    datosFormulario = None
    if request.method == "POST":
        datosFormulario = request.POST
        
    formularioE = EquipoModelForm(datosFormulario)
    
    if (request.method == "POST"):
        equipo_creado = equipo_create_valid(formularioE)
        if(equipo_creado):
            messages.success(request, 'Se a creado el equipo'+formularioE.cleaned_data.get('nombre')+" correctamente")
            return redirect("lista_equipos")
    return render(request, 'eventos_deportivos/equipos/equipo_create.html',{"formularioE":formularioE})

# LEER
def equipo_buscar(request):
    mensaje_busqueda = ""
    equipos = Equipo.objects.none() # Por defecto vacio
    formularioJ = BusquedaJugadorForm(request.GET or None)
    formularioE = BusquedaEquipoForm(request.GET or None)
    formularioES = BusquedaEstadioForm(request.GET or None)
    formularioSP = BusquedaSponsorForm(request.GET or None)
    formularioP = BusquedaPartidoForm(request.GET or None)
    formularioT = BusquedaTorneoForm(request.GET or None)
    
    if(len(request.GET)>0):
        
        if formularioE.is_valid():
            nombreBusqueda=formularioE.cleaned_data.get('nombreBusqueda')
            ciudadBusqueda=formularioE.cleaned_data.get('ciudadBusqueda')
            activoBusqueda=formularioE.cleaned_data.get('activoBusqueda')
            
            # --- mensaje de filtros  ---
            filtros_aplicados = []
            if nombreBusqueda:
                filtros_aplicados.append(f"Nombre contiene '{nombreBusqueda}'")
            if ciudadBusqueda:
                filtros_aplicados.append(f"Ciudad contiene '{ciudadBusqueda}'")
            filtros_aplicados.append(f"Activo= '{activoBusqueda}'")
            mensaje_busqueda = " | ".join(filtros_aplicados)
            
            # --- Construccion del filtro ---
            filtros = Q(activo=activoBusqueda) # Posicion obligatoria
            if nombreBusqueda:
                filtros &= Q(nombre__icontains=nombreBusqueda)
            if ciudadBusqueda:
                filtros &= Q(ciudad__icontains=ciudadBusqueda)
            if activoBusqueda is not None:
                filtros &= Q(activo=activoBusqueda)
                
            equipos = Equipo.objects.filter(filtros).select_related("estadio_principal")
    
            return render(request, 'eventos_deportivos/equipos/equipo_buscar.html', {"formularioE":formularioE,"texto_busqueda":mensaje_busqueda,"equipos":equipos})
    
    return render(
        request, 
        "eventos_deportivos/index.html",
        {
            "formularioJ":formularioJ,
            "formularioE":formularioE,
            "formularioES":formularioES,
            "formularioSP":formularioSP,
            "formularioP":formularioP,
            "formularioT":formularioT,
        }
    )

# EDITAR/ACTUALIZAR
@login_required
@permission_required('eventos_deportivos.change_equipo')
def equipo_editar(request,equipo_id):
    equipo = Equipo.objects.get(id=equipo_id)
    
    datosFormulario=None
    
    if request.method=="POST":
        datosFormulario=request.POST
        
    formularioE=EquipoModelForm(datosFormulario,instance=equipo)
    
    if (request.method=="POST"):
        if formularioE.is_valid():
            formularioE.save()
            try:
                formularioE.save()
                messages.success(request, 'Se ha editado el equipo'+formularioE.cleaned_data.get('nombre')+" correctamente")
                return redirect('lista_equipos')
            except Exception as e:
                print(e)
    return render(request, 'eventos_deportivos/equipos/equipo_editar.html',{"formularioE":formularioE,"equipo":equipo})

# ELIMINAR
@login_required
@permission_required('eventos_deportivos.delete_equipo')
def equipo_eliminar(request,equipo_id):
    equipo=Equipo.objects.get(id=equipo_id)
    try:
        equipo.delete()
    except:
        pass
    return redirect('lista_equipos')

# ----------------------------
# CRUD Estadio
# ----------------------------

def estadio_create_valid(formularioES):
    # Valida y guarda el formulario
    # Devuelve True si se guardó correctamente, False si hubo error.

    estadio_creado = False
    # Comprueba si el formulario es valido
    if formularioES.is_valid():
        try:
            formularioES.save()
            estadio_creado = True
        except Exception as e:
            print("Error al guardar estadio: ", e)
    else:
        print("Formulario no valido: ", formularioES.errors)
    return estadio_creado

@login_required
@permission_required('eventos_deportivos.add_estadio')
def estadio_create(request):
    # si la peticion es GET se crea el formulario vacio
    # en el caso de set POST se crea el formulario con datos
    datosFormulario = None
    if request.method == "POST":
        datosFormulario = request.POST
        
    formularioES = EstadioModelForm(datosFormulario,files=request.FILES) # <-- Aquí se recogen los archivos
    
    if (request.method == "POST"):
        estadio_creado = estadio_create_valid(formularioES)
        if(estadio_creado):
            messages.success(request, 'Se a creado el estadio'+formularioES.cleaned_data.get('nombre')+" correctamente")
            return redirect("lista_estadios")
    return render(request, 'eventos_deportivos/estadios/estadio_create.html',{"formularioES":formularioES})

# LEER
def estadio_buscar(request):
    mensaje_busqueda = ""
    estadios = Estadio.objects.none() # Por defecto vacio
    formularioJ = BusquedaJugadorForm(request.GET or None)
    formularioE = BusquedaEquipoForm(request.GET or None)
    formularioES = BusquedaEstadioForm(request.GET or None)
    formularioSP = BusquedaSponsorForm(request.GET or None)
    formularioP = BusquedaPartidoForm(request.GET or None)
    formularioT = BusquedaTorneoForm(request.GET or None)
    
    if(len(request.GET)>0):
        
        if formularioES.is_valid():
            nombreBusqueda=formularioES.cleaned_data.get('nombreBusqueda')
            capacidadBusqueda=formularioES.cleaned_data.get('capacidadBusqueda')
            cubiertoBusqueda=formularioES.cleaned_data.get('cubiertoBusqueda')
            
            # --- mensaje de filtros  ---
            filtros_aplicados = []
            if nombreBusqueda:
                filtros_aplicados.append(f"Nombre contiene '{nombreBusqueda}'")
            if capacidadBusqueda:
                filtros_aplicados.append(f"Capacidad contiene '{capacidadBusqueda}'")
            filtros_aplicados.append(f"Cubierto= '{cubiertoBusqueda}'")
            mensaje_busqueda = " | ".join(filtros_aplicados)
            
            # --- Construccion del filtro ---
            filtros = Q() # Posicion obligatoria
            if nombreBusqueda:
                filtros &= Q(nombre__icontains=nombreBusqueda)
            if capacidadBusqueda:
                filtros &= Q(capacidad__lte=capacidadBusqueda)
            if cubiertoBusqueda:
                filtros &= Q(cubierto=cubiertoBusqueda)
                
            estadios = Estadio.objects.filter(filtros)
    
            return render(request, 'eventos_deportivos/estadios/estadio_buscar.html', {"formularioES":formularioES,"texto_busqueda":mensaje_busqueda,"estadios":estadios})

    return render(
        request, 
        "eventos_deportivos/index.html",
        {
            "formularioJ":formularioJ,
            "formularioE":formularioE,
            "formularioES":formularioES,
            "formularioSP":formularioSP,
            "formularioP":formularioP,
            "formularioT":formularioT,
        }
    )

# EDITAR/ACTUALIZAR
@login_required
@permission_required('eventos_deportivos.change_estadio')
def estadio_editar(request,estadio_id):
    estadio = Estadio.objects.get(id=estadio_id)
    
    datosFormulario=None
    
    if request.method=="POST":
        datosFormulario=request.POST
        
    formularioES=EstadioModelForm(datosFormulario,files=request.FILES,instance=estadio)
    
    if (request.method=="POST"):
        if formularioES.is_valid():
            formularioES.save()
            try:
                formularioES.save()
                messages.success(request, 'Se ha editado el estadio'+formularioES.cleaned_data.get('nombre')+" correctamente")
                return redirect('lista_estadios')
            except Exception as e:
                print(e)
    return render(request, 'eventos_deportivos/estadios/estadio_editar.html',{"formularioES":formularioES,"estadio":estadio})

# ELIMINAR
@login_required
@permission_required('eventos_deportivos.delete_estadio')
def estadio_eliminar(request,estadio_id):
    estadio=Estadio.objects.get(id=estadio_id)
    try:
        estadio.delete()
    except:
        pass
    return redirect('lista_estadios')

# ----------------------------
# CRUD Sponsors
# ----------------------------

def sponsor_create_valid(formularioSP):
    # Valida y guarda el formulario
    # Devuelve True si se guardó correctamente, False si hubo error.

    sponsor_creado = False
    # Comprueba si el formulario es valido
    if formularioSP.is_valid():
        try:
            formularioSP.save()
            sponsor_creado = True
        except Exception as e:
            print("Error al guardar sponsor: ", e)
    else:
        print("Formulario no valido: ", formularioSP.errors)
    return sponsor_creado

@login_required
@permission_required('eventos_deportivos.add_sponsor')
def sponsor_create(request):
    # si la peticion es GET se crea el formulario vacio
    # en el caso de set POST se crea el formulario con datos
    datosFormulario = None
    if request.method == "POST":
        datosFormulario = request.POST
        
    formularioSP = SponsorModelForm(datosFormulario)
    
    if (request.method == "POST"):
        sponsor_creado = sponsor_create_valid(formularioSP)
        if(sponsor_creado):
            messages.success(request, 'Se a creado el sponsor '+formularioSP.cleaned_data.get('nombre')+" correctamente")
            return redirect("lista_sponsors")
    return render(request, 'eventos_deportivos/sponsors/sponsor_create.html',{"formularioSP":formularioSP})

# LEER
def sponsor_buscar(request):
    mensaje_busqueda = ""
    sponsors = Sponsor.objects.none() # Por defecto vacio
    formularioJ = BusquedaJugadorForm(request.GET or None)
    formularioE = BusquedaEquipoForm(request.GET or None)
    formularioES = BusquedaEstadioForm(request.GET or None)
    formularioSP = BusquedaSponsorForm(request.GET or None)
    formularioP = BusquedaPartidoForm(request.GET or None)
    formularioT = BusquedaTorneoForm(request.GET or None)
    
    if(len(request.GET)>0):
        
        if formularioSP.is_valid():
            nombreBusqueda=formularioSP.cleaned_data.get('nombreBusqueda')
            paisBusqueda=formularioSP.cleaned_data.get('paisBusqueda')
            montoBusqueda=formularioSP.cleaned_data.get('montoBusqueda')
            
            # --- mensaje de filtros  ---
            filtros_aplicados = []
            if nombreBusqueda:
                filtros_aplicados.append(f"Nombre contiene '{nombreBusqueda}'")
            if montoBusqueda is not None:
                filtros_aplicados.append(f"Monto <= '{montoBusqueda}'")
            if paisBusqueda:
                filtros_aplicados.append(f"Pais contiene '{paisBusqueda}'")
            mensaje_busqueda = " | ".join(filtros_aplicados)
            
            # --- Construccion del filtro ---
            filtros = Q() # Posicion obligatoria
            if nombreBusqueda:
                filtros &= Q(nombre__icontains=nombreBusqueda)
            if montoBusqueda is not None:
                filtros &= Q(monto__lte=montoBusqueda)
            if paisBusqueda:
                filtros &= Q(pais__icontains=paisBusqueda)
                
            sponsors = Sponsor.objects.filter(filtros)
    
            return render(request, 'eventos_deportivos/sponsors/sponsor_buscar.html', {"formularioSP":formularioSP,"texto_busqueda":mensaje_busqueda,"sponsors":sponsors})

    return render(
        request, 
        "eventos_deportivos/index.html",
        {
            "formularioJ":formularioJ,
            "formularioE":formularioE,
            "formularioES":formularioES,
            "formularioSP":formularioSP,
            "formularioP":formularioP,
            "formulario":formularioT,
        }
    )

# EDITAR/ACTUALIZAR
@login_required
@permission_required('eventos_deportivos.change_sponsor')
def  sponsor_editar(request,sponsor_id):
    sponsor = Sponsor.objects.get(id=sponsor_id)
    
    datosFormulario=None
    
    if request.method=="POST":
        datosFormulario=request.POST
        
    formularioSP=SponsorModelForm(datosFormulario,instance=sponsor)
    
    if (request.method=="POST"):
        if formularioSP.is_valid():
            formularioSP.save()
            try:
                formularioSP.save()
                messages.success(request, 'Se ha editado el sponsor'+formularioSP.cleaned_data.get('nombre')+" correctamente")
                return redirect('lista_sponsors')
            except Exception as e:
                print(e)
    return render(request, 'eventos_deportivos/sponsors/sponsor_editar.html',{"formularioSP":formularioSP,"sponsor":sponsor})

# ELIMINAR
@login_required
@permission_required('eventos_deportivos.delete_sponsor')
def sponsor_eliminar(request,sponsor_id):
    sponsor=Sponsor.objects.get(id=sponsor_id)
    try:
        sponsor.delete()
    except:
        pass
    return redirect('lista_sponsors')

# ----------------------------
# CRUD Partidos
# ----------------------------

def partido_create_valid(formularioP):
    # Valida y guarda el formulario
    # Devuelve True si se guardó correctamente, False si hubo error.

    partido_creado = False
    # Comprueba si el formulario es valido
    if formularioP.is_valid():
        try:
            formularioP.save()
            partido_creado = True
        except Exception as e:
            print("Error al guardar partido: ", e)
    else:
        print("Formulario no valido: ", formularioP.errors)
    return partido_creado

@login_required
@permission_required('eventos_deportivos.add_partido')
def partido_create(request):
    # si la peticion es GET se crea el formulario vacio
    # en el caso de set POST se crea el formulario con datos
    datosFormulario = None
    if request.method == "POST":
        datosFormulario = request.POST
        
    formularioP = PartidoModelForm(datosFormulario)
    
    if (request.method == "POST"):
        partido_creado = partido_create_valid(formularioP)
        if(partido_creado):
            # Obtener los objetos Equipo
            equipo_local = formularioP.cleaned_data.get('equipo_local')
            equipo_visitante = formularioP.cleaned_data.get('equipo_visitante')
            
            messages.success(request, f"Se a creado el partido {equipo_local} VS {equipo_visitante} correctamente")
            return redirect("lista_partidos")
    return render(request, 'eventos_deportivos/partidos/partido_create.html',{"formularioP":formularioP})

# LEER
def partido_buscar(request):
    mensaje_busqueda = ""
    partidos = Partido.objects.none() # Por defecto vacio
    formularioJ = BusquedaJugadorForm(request.GET or None)
    formularioE = BusquedaEquipoForm(request.GET or None)
    formularioES = BusquedaEstadioForm(request.GET or None)
    formularioSP = BusquedaSponsorForm(request.GET or None)
    formularioP = BusquedaPartidoForm(request.GET or None)
    formularioT = BusquedaTorneoForm(request.GET or None)
    
    if(len(request.GET)>0):
        
        if formularioP.is_valid():
            hastaFechaBusqueda=formularioP.cleaned_data.get('hastaFechaBusqueda')
            desdeFechaBusqueda=formularioP.cleaned_data.get('desdeFechaBusqueda')
            torneoBusqueda=formularioP.cleaned_data.get('torneoBusqueda')
            
            # --- mensaje de filtros  ---
            filtros_aplicados = []
            if hastaFechaBusqueda:
                filtros_aplicados.append(f"fecha hasta: '{hastaFechaBusqueda}'")
            if desdeFechaBusqueda:
                filtros_aplicados.append(f"fecha desde: '{desdeFechaBusqueda}'")
            if torneoBusqueda:
                filtros_aplicados.append(f"torneo: '{torneoBusqueda}'")
            mensaje_busqueda = " | ".join(filtros_aplicados)
            
            # --- Construccion del filtro ---
            filtros = Q() # Posicion obligatoria
            if desdeFechaBusqueda:
                filtros &= Q(fecha__gte=desdeFechaBusqueda)
            if hastaFechaBusqueda:
                filtros &= Q(fecha__lte=hastaFechaBusqueda)
            if torneoBusqueda:
                filtros &= Q(torneo=torneoBusqueda)
                
            partidos = Partido.objects.filter(filtros).select_related('equipo_local','equipo_visitante','torneo')
    
            return render(request, 'eventos_deportivos/partidos/partido_buscar.html', {"formularioP":formularioP,"texto_busqueda":mensaje_busqueda,"partidos":partidos})
    
    return render(
        request, 
        "eventos_deportivos/index.html",
        {
            "formularioJ":formularioJ,
            "formularioE":formularioE,
            "formularioES":formularioES,
            "formularioSP":formularioSP,
            "formularioP":formularioP,
            "formularioT":formularioT,
        }
    )

# EDITAR/ACTUALIZAR
@login_required
@permission_required('eventos_deportivos.change_partido')
def  partido_editar(request,partido_id):
    partido = Partido.objects.get(id=partido_id)
    
    datosFormulario=None
    
    if request.method=="POST":
        datosFormulario=request.POST
        
    formularioP=PartidoModelForm(datosFormulario,instance=partido)
    
    if (request.method=="POST"):
        if formularioP.is_valid():
            formularioP.save()
            try:
                formularioP.save()
                # Obtener los objetos Equipo
                equipo_local = formularioP.cleaned_data.get('equipo_local')
                equipo_visitante = formularioP.cleaned_data.get('equipo_visitante')
            
                messages.success(request, f"Se a modificado el partido {equipo_local} VS {equipo_visitante} correctamente")
                return redirect('lista_partidos')
            except Exception as e:
                print(e)
    return render(request, 'eventos_deportivos/partidos/partido_editar.html',{"formularioP":formularioP,"partido":partido})

# ELIMINAR
@login_required
@permission_required('eventos_deportivos.delete_partido')
def partido_eliminar(request,partido_id):
    partido=Partido.objects.get(id=partido_id)
    try:
        partido.delete()
    except:
        pass
    return redirect('lista_partidos')

# ----------------------------
# CRUD Torneos
# ----------------------------
# CREAR
def torneo_create_valid(formularioT):
    # Valida y guarda el formulario
    # Devuelve True si se guardó correctamente, False si hubo error.

    torneo_creado = False
    # Comprueba si el formulario es valido
    if formularioT.is_valid():
        try:
            formularioT.save()
            torneo_creado = True
        except Exception as e:
            print("Error al guardar el torneo: ", e)
    else:
        print("Formulario no valido: ", formularioT.errors)
    return torneo_creado

@login_required
@permission_required('eventos_deportivos.add_torneo')
def torneo_create(request):
    # si la peticion es GET se crea el formulario vacio
    # en el caso de set POST se crea el formulario con datos
    datosFormulario = None
    if request.method == "POST":
        datosFormulario = request.POST
        
    formularioT = TorneoModelForm(datosFormulario)
    
    if (request.method == "POST"):
        torneo_creado = torneo_create_valid(formularioT)
        if(torneo_creado):
            
            messages.success(request, 'Se a creado el torneo '+formularioT.cleaned_data.get('nombre')+" correctamente")
            return redirect("lista_torneos")
    return render(request, 'eventos_deportivos/torneos/torneo_create.html',{"formularioT":formularioT})

# LEER
def torneo_buscar(request):
    mensaje_busqueda = ""
    torneos = Torneo.objects.none()  # vacio por defecto

    formularioJ = BusquedaJugadorForm(request.GET or None)
    formularioE = BusquedaEquipoForm(request.GET or None)
    formularioES = BusquedaEstadioForm(request.GET or None)
    formularioSP = BusquedaSponsorForm(request.GET or None)
    formularioP = BusquedaPartidoForm(request.GET or None)
    formularioT = BusquedaTorneoForm(request.GET or None)

    if len(request.GET) > 0:

        if formularioT.is_valid():
            paisBusqueda = formularioT.cleaned_data.get('paisBusqueda')
            fechaBusqueda = formularioT.cleaned_data.get('fechaDesdeBusqueda')
            nombreBusqueda = formularioT.cleaned_data.get('nombreBusqueda')

            # --- mensaje de filtros ---
            filtros_aplicados = []
            if paisBusqueda:
                filtros_aplicados.append(f"Pais = '{paisBusqueda}'")
            if fechaBusqueda:
                filtros_aplicados.append(f"Fecha desde = '{fechaBusqueda}'")
            if nombreBusqueda:
                filtros_aplicados.append(f"Nombre = '{nombreBusqueda}'")
            mensaje_busqueda = " | ".join(filtros_aplicados)

            # --- Construccion del filtro ---
            filtros = Q()
            if paisBusqueda:
                filtros &= Q(pais__icontains=paisBusqueda)
            if fechaBusqueda:
                filtros &= Q(fecha_inicio__gte=fechaBusqueda)
            if nombreBusqueda:
                filtros &= Q(nombre__icontains=nombreBusqueda)

            torneos = Torneo.objects.filter(filtros)

            return render(request,'eventos_deportivos/torneos/torneo_buscar.html',{"formularioT": formularioT,"texto_busqueda": mensaje_busqueda,"torneos": torneos})

    # Si no hay GET: volver al index con todos los formularios
    return render(
        request,
        "eventos_deportivos/index.html",
        {
            "formularioJ": formularioJ,
            "formularioE": formularioE,
            "formularioES": formularioES,
            "formularioSP": formularioSP,
            "formularioP": formularioP,
            "formularioT": formularioT
        }
    )
    
# EDITAR/ACTUALIZAR
@login_required
@permission_required('eventos_deportivos.change_torneo')
def  torneo_editar(request,torneo_id):
    torneo = Torneo.objects.get(id=torneo_id)
    
    datosFormulario=None
    
    if request.method=="POST":
        datosFormulario=request.POST
        
    formularioT=TorneoModelForm(datosFormulario,instance=torneo)
    
    if (request.method=="POST"):
        if formularioT.is_valid():
            formularioT.save()
            try:
                formularioT.save()
                messages.success(request, 'Se ha editado el torneo'+formularioT.cleaned_data.get('nombre')+" correctamente")
                return redirect('lista_torneos')
            except Exception as e:
                print(e)
    return render(request, 'eventos_deportivos/torneos/torneo_editar.html',{"formularioT":formularioT,"torneo":torneo})

# ELIMINAR
@login_required
@permission_required('eventos_deportivos.delete_torneo')
def torneo_eliminar(request,torneo_id):
    torneo=Torneo.objects.get(id=torneo_id)
    try:
        torneo.delete()
    except:
        pass
    return redirect('lista_torneos')

# ------------------------------------
# Autenticacion, Sesiones y Permisos 
# ------------------------------------
def registrar_usuario(request):
    if request.method=='POST':
        formularioRegistro = RegistroForm(request.POST)
        if formularioRegistro.is_valid():
            user=formularioRegistro.save()
            rol=int(formularioRegistro.cleaned_data.get('rol'))
            
            if rol == Usuario.ARBITRO:
                # Asignar grupo Arbitro
                arbitro_group = Group.objects.get(name='Arbitros')
                user.groups.add(arbitro_group)
                
                # Crear perfil de árbitro con los campos obligatorios
                arbitro = Arbitro.objects.create(
                    usuario=user,
                    nombre=user.first_name or 'NombreArbitro',
                    apellido=user.last_name or 'ApellidoArbitro',
                    licencia=f"LIC-{user.id:04d}"  # Genera una licencia única
                )
                arbitro.save()
            elif(rol==Usuario().MANAGER):
                # Asignar grupo Manager
                manager_group = Group.objects.get(name='Managers')
                user.groups.add(manager_group)
                
                # Crear perfil de manager
                manager=Manager.objects.create(usuario=user)
                manager.save()
            return redirect('login')
    else:
        formularioRegistro=RegistroForm()
    return render(request, 'registration/signup.html',{'formularioRegistro':formularioRegistro})

