# proyecto-parte1_CarlosRoblesDominguez

# Proyecto Django: Gestión de Torneos Deportivos

## Descripción del proyecto

Este proyecto consiste en una plataforma de gestión de **torneos deportivos**, donde se pueden gestionar **jugadores, equipos, partidos, torneos, árbitros, estadios, sponsors y premios**.  
El proyecto está desarrollado en **Django**, y permite:  

- Crear y relacionar modelos complejos con relaciones OneToOne, ManyToOne y ManyToMany.  
- Generar datos de prueba automáticamente con **Faker**.  
- Realizar backups de la base de datos mediante fixtures.  

---

## Modelos

### 1. Jugador
- **Descripción:** Representa a un jugador de un equipo participante en torneos.  
- **Atributos:**  
  - `nombre` (CharField, max_length=100)  
  - `apellido` (CharField, max_length=100)  
  - `fecha_nacimiento` (DateField)  
  - `posicion` (CharField, choices)  
  - `estadisticas` (OneToOne con EstadisticasJugador)  

---

### 2. EstadisticasJugador
- **Descripción:** Guarda estadísticas individuales de cada jugador.  
- **Atributos:**  
  - `partidos_jugados` (IntegerField)  
  - `goles` (IntegerField)  
  - `asistencias` (IntegerField)  
  - `tarjetas` (IntegerField)  

---

### 3. Equipo
- **Descripción:** Representa un equipo participante en los torneos.  
- **Atributos:**  
  - `nombre` (CharField, max_length=100)  
  - `ciudad` (CharField, max_length=100)  
  - `fundacion` (DateField)  
  - `activo` (BooleanField)  
- **Relaciones:**  
  - `jugadores` (ManyToMany con tabla intermedia `EquipoJugador` con atributos `fecha_ingreso` y `capitan`)  

---

### 4. EquipoJugador *(tabla intermedia ManyToMany)*
- **Descripción:** Relación entre jugadores y equipos, con información extra.  
- **Atributos:**  
  - `jugador` (ForeignKey a Jugador)  
  - `equipo` (ForeignKey a Equipo)  
  - `fecha_ingreso` (DateField)  
  - `capitan` (BooleanField)  

---

### 5. Torneo
- **Descripción:** Representa un torneo deportivo.  
- **Atributos:**  
  - `nombre` (CharField)  
  - `pais` (CharField)  
  - `fecha_inicio` (DateField)  
  - `fecha_fin` (DateField)  

---

### 6. Partido
- **Descripción:** Representa un partido entre dos equipos.  
- **Atributos:**  
  - `equipo_local` (ForeignKey a Equipo)  
  - `equipo_visitante` (ForeignKey a Equipo)  
  - `fecha` (DateTimeField)  
  - `resultado` (CharField)  

---

### 7. Arbitro
- **Descripción:** Representa a los árbitros de los partidos.  
- **Atributos:**  
  - `nombre` (CharField)  
  - `apellido` (CharField)  
  - `licencia` (CharField, unique=True)  
  - `partidos` (ManyToMany con Partido)  

---

### 8. Estadio
- **Descripción:** Representa los estadios donde se juegan los partidos.  
- **Atributos:**  
  - `nombre` (CharField)  
  - `ciudad` (CharField)  
  - `capacidad` (IntegerField)  
  - `cubierto` (BooleanField)  

---

### 9. Sponsor
- **Descripción:** Empresas que patrocinan equipos.  
- **Atributos:**  
  - `nombre` (CharField)  
  - `monto` (DecimalField)  
  - `pais` (CharField)  
  - `equipos` (ManyToMany con Equipo)  

---

### 10. Premio
- **Descripción:** Premios otorgados a equipos ganadores de torneos.  
- **Atributos:**  
  - `nombre` (CharField)  
  - `monto` (DecimalField)  
  - `torneo` (ForeignKey a Torneo)  
  - `ganador` (ForeignKey a Equipo, null=True)  

---

## Parámetros usados en los atributos

- `max_length` (CharField)  
- `unique` (CharField)  
- `choices` (CharField)  
- `auto_now_add` (DateTimeField)  
- `null` (Boolean, ForeignKey)  
- `blank` (Boolean, ForeignKey)  
- `decimal_places` (DecimalField)  
- `max_digits` (DecimalField)  
- `default` (BooleanField)  
- `verbose_name` (opcional, todos los campos)  

---

## Código no visto en clase (Eliminatorio)

Algunos fragmentos de código que no se vieron en clase y requieren explicación:

### 1. Faker
- Librería de Python para generar datos falsos.
- Se instala con `pip install faker`.
- Permite crear nombres, fechas, ciudades, empresas y números aleatorios, lo que es útil para poblar la base de datos con datos de prueba.

### 2. Comandos personalizados de Django
- Se crean dentro de `torneos/management/commands/`.
- Heredan de `BaseCommand` de `django.core.management.base`.
- Se ejecutan con `python manage.py <nombre_del_comando>`.
- Permiten automatizar tareas como generar datos de prueba, limpiar la base de datos, crear backups, etc.

### 3. Funciones y parámetros usados
- `random.randint(a, b)`: Devuelve un entero aleatorio entre `a` y `b`.
- `Model.objects.create(...)`: Crea un objeto del modelo y lo guarda en la base de datos.
- `queryset.set([...])`: Asigna objetos a un campo ManyToMany.
- `fake.date_of_birth(minimum_age, maximum_age)`: Genera una fecha de nacimiento aleatoria.
- `fake.boolean()`: Genera True o False aleatoriamente.
- `fake.company()`, `fake.city()`, `fake.country()`, `fake.first_name()`, `fake.last_name()`: Generan nombres de empresas, ciudades, países o personas aleatorios.

---

## URLs implementadas

### 1 Lista de Jugadores

- **URL:** `/jugadores/`
- **Vista:** `lista_jugadores`
- **Método HTTP:** GET
- **Descripción:** 
  Muestra un listado de todos los jugadores registrados, incluyendo:
  - Nombre y Apellido
  - Fecha de nacimiento
  - Posición
  - Estadísticas (Goles, Asistencias)
  - Equipos asociados (a través de la tabla intermedia `EquipoJugador`)
- **QuerySet optimizado:** 
  - Se utiliza `select_related('estadisticas')` para obtener la relación OneToOne con `EstadisticasJugador`.
  - Se utiliza `prefetch_related('equipojugador_set')` para obtener los equipos asociados de manera eficiente.
- **Equivalente SQL (usando raw()):**
```python
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
```

---

### 2 Detalle de Jugador

- **URL:** `/jugadores/<int:jugador_id>/`
- **Vista:** `detalle_jugador`
- **Método HTTP:** GET
- **Descripción:**  
  Muestra el detalle completo de un jugador específico, incluyendo:  
  - Nombre y Apellido  
  - Fecha de nacimiento  
  - Posición  
  - Estadísticas completas (partidos jugados, goles, asistencias, tarjetas)  
  - Equipos asociados con fecha de ingreso y rol (capitán/jugador)  

- **QuerySet optimizado:**  
  - Se utiliza `select_related('estadisticas')` para obtener la relación OneToOne con `EstadisticasJugador`.  
  - Se utiliza `prefetch_related('equipos')` para obtener los equipos asociados de manera eficiente.  
  - Se usa `get_object_or_404` para obtener el jugador o devolver un error 404 si no existe.  
    Esto es mejor que usar `get()` porque:  
      - `get()` lanza una excepción `DoesNotExist` que habría que capturar manualmente para mostrar un error de página.  
      - `get_object_or_404` maneja automáticamente la excepción y devuelve una página 404 estándar si no se encuentra el objeto, haciendo el código más limpio y seguro.

- **Equivalente SQL (usando raw()):**  
```python
sql = """
SELECT j.id, j.nombre, j.apellido, j.fecha_nacimiento, j.posicion,
       es.partidos_jugados, es.goles, es.asistencias, es.tarjetas,
       e.id as equipo_id, e.nombre as equipo_nombre, ej.fecha_ingreso, ej.capitan
FROM eventos_deportivos_jugador j
INNER JOIN eventos_deportivos_estadisticasjugador es ON j.estadisticas_id = es.id
LEFT JOIN eventos_deportivos_equipojugador ej ON ej.jugador_id = j.id
LEFT JOIN eventos_deportivos_equipo e ON ej.equipo_id = e.id
WHERE j.id = %s;
"""
```
---

### 3 Detalle de Equipo

- **URL:** `/equipos/<int:equipo_id>/`
- **Vista:** `detalle_equipo`
- **Método HTTP:** GET
- **Descripción:** 
  Muestra todos los datos de un equipo específico, incluyendo:
  - Nombre, Ciudad, Fundación, Activo
  - Estadio principal
  - Lista de jugadores asociados con fecha de ingreso y rol (Capitán/Jugador)
- **QuerySet optimizado:** 
  - `select_related('estadio_principal')` para la relación OneToOne con Estadio.
  - `select_related('jugador')` en EquipoJugador para obtener los jugadores de forma eficiente.
- **Equivalente SQL (usando raw()):**
```python
sql = """
SELECT ej.id, j.nombre, j.apellido, ej.fecha_ingreso, ej.capitan
FROM eventos_deportivos_equipojugador ej
INNER JOIN eventos_deportivos_jugador j ON ej.jugador_id = j.id
WHERE ej.equipo_id = %s
ORDER BY ej.fecha_ingreso;
"""
```

---

### 4 Lista de Partidos

- **URL:** `/partidos/`
- **Vista:** `lista_partidos`
- **Método HTTP:** GET
- **Descripción:** 
  Muestra un listado de todos los partidos registrados, incluyendo:
  - Fecha del partido
  - Equipo local y visitante
  - Resultado
  - Torneo al que pertenece
- **QuerySet optimizado:** 
  - Se utiliza `select_related('equipo_local', 'equipo_visitante', 'torneo')` para optimizar las relaciones ManyToOne.
- **Equivalente SQL (usando raw()):**
```python
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
```

---

### 5 Detalle de Partido

- **URL:** `/partidos/<int:partido_id>/`
- **Vista:** `detalle_partido`
- **Método HTTP:** GET
- **Descripción:** 
  Muestra toda la información de un partido específico, incluyendo:
  - Equipo local y visitante
  - Resultado
  - Fecha
  - Torneo asociado
  - Árbitros del torneo
- **QuerySet optimizado:** 
  - Se utiliza `select_related("equipo_local", "equipo_visitante", "torneo")` para relaciones ManyToOne.
  - Se utiliza `prefetch_related("torneo__arbitro_set")` para relaciones ManyToMany de arbitros.
- **Equivalente SQL (usando raw()):**
```python
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
```

---

### 6 Detalle de Equipo

- **URL:** `/equipos/<int:id>/`
- **Vista:** `detalle_equipo`
- **Método HTTP:** GET
- **Descripción:** 
  Muestra la información completa de un equipo específico identificado por su `id`.  
  Incluye:
  - Nombre del equipo
  - Ciudad
  - Fecha de fundación
  - Estado activo/inactivo
  - Jugadores asociados (nombre, apellido, fecha de ingreso y rol: jugador o capitán)
- **QuerySet optimizado:** 
  - Se utiliza `prefetch_related('jugadores')` para obtener todos los jugadores asociados al equipo de manera eficiente (ManyToMany vía `EquipoJugador`).
  - Se utiliza `select_related('estadisticas')` en los jugadores para obtener las estadísticas de cada jugador en la misma consulta (OneToOne).
- **Equivalente SQL (usando raw()):**
```python
sql = f"""
SELECT e.id, e.nombre, e.ciudad, e.fundacion, e.activo,
       j.id AS jugador_id, j.nombre AS jugador_nombre, j.apellido AS jugador_apellido,
       ej.fecha_ingreso, ej.capitan,
       es.partidos_jugados, es.goles, es.asistencias, es.tarjetas
FROM eventos_deportivos_equipo e
LEFT JOIN eventos_deportivos_equipojugador ej ON ej.equipo_id = e.id
LEFT JOIN eventos_deportivos_jugador j ON ej.jugador_id = j.id
LEFT JOIN eventos_deportivos_estadisticasjugador es ON j.estadisticas_id = es.id
WHERE e.id = {id};
"""
```

---

### 7 Lista de Torneos por Nombre

- **URL:** `/torneos/<nombre_torneo>/`
- **Vista:** `detalle_torneo`
- **Método HTTP:** GET
- **Descripción:** 
  Muestra todos los torneos cuyo nombre coincide con el parámetro `nombre_torneo`.  
  Cada torneo incluye:
  - Nombre
  - País
  - Fecha de inicio y fin
  - Lista de partidos asociados (equipo local, equipo visitante y resultado)  
  Se devuelve **toda la información de todos los torneos que coincidan**, incluso si hay más de uno con el mismo nombre.
- **QuerySet optimizado:** 
  - Se utiliza `prefetch_related` para obtener los partidos asociados de manera eficiente (ManyToOne).
  - Dentro de `prefetch_related` usamos `Prefetch` junto con `select_related` para obtener la información de los equipos de cada partido en la misma consulta y evitar consultas N+1.
  - `from django.db.models import Prefetch` se importa específicamente para crear el objeto `Prefetch` que permite personalizar el queryset de la relación.
- **Equivalente SQL (usando raw()):**
```python
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
```

---

### 8 Lista de Torneos

- **URL:** `/torneos/`
- **Vista:** `lista_torneos`
- **Método HTTP:** GET
- **Descripción:** 
  Muestra un listado de todos los torneos registrados, incluyendo:
  - Nombre del torneo
  - País
  - Fecha de inicio y fin
  - Partidos asociados con equipos locales y visitantes
- **QuerySet optimizado:** 
  - Se utiliza `prefetch_related` con `Prefetch` para obtener todos los partidos asociados a cada torneo.
  - Se utiliza `select_related` dentro del Prefetch para optimizar la obtención de los equipos (ManyToOne).
- **Equivalente SQL (usando raw()):**
```python
sql = """
SELECT t.id, t.nombre, t.pais, t.fecha_inicio, t.fecha_fin,
       p.id AS partido_id, p.resultado, p.fecha,
       el.nombre AS equipo_local, ev.nombre AS equipo_visitante
FROM eventos_deportivos_torneo t
LEFT JOIN eventos_deportivos_partido p ON p.torneo_id = t.id
LEFT JOIN eventos_deportivos_equipo el ON p.equipo_local_id = el.id
LEFT JOIN eventos_deportivos_equipo ev ON p.equipo_visitante_id = ev.id
ORDER BY t.fecha_inicio;
"""
```

---

### 9 Detalle de Árbitro en un Torneo

- **URL:** `/arbitros/<int:arbitro_id>/torneo/<int:torneo_id>/`
- **Vista:** `detalle_arbitro_torneo`
- **Método HTTP:** GET
- **Descripción:** 
  Muestra los detalles de un árbitro específico y todos los partidos que dirigió en un torneo concreto.
- **Parámetros:**
  - `arbitro_id` (int): Identificador del árbitro.j
  - `torneo_id` (int): Identificador del torneo.
- **QuerySet optimizado:** 
  - Se utiliza `select_related('equipo_local', 'equipo_visitante', 'torneo')` para obtener los datos relacionados de manera eficiente.
  - Se filtra por torneo con `.filter(torneo_id=torneo_id)`.
- **Uso de `get_object_or_404`:** 
  - Se emplea para asegurar que el árbitro existe en la base de datos.
  - Es más seguro que `get()` porque devuelve un error 404 automáticamente si no se encuentra el registro, evitando excepciones no controladas.
- **Equivalente SQL (usando raw()):**
```python
sql = f"""
SELECT a.id AS arbitro_id, a.nombre, a.apellido, a.licencia,
       p.id AS partido_id, p.fecha, p.resultado,
       el.nombre AS equipo_local, ev.nombre AS equipo_visitante,
       t.nombre AS torneo_nombre
FROM eventos_deportivos_arbitro a
INNER JOIN eventos_deportivos_partido_partidos a ON a.id = pa.arbitro_id
INNER JOIN eventos_deportivos_partido p ON pa.partido_id = p.id
INNER JOIN eventos_deportivos_equipo el ON p.equipo_local_id = el.id
INNER JOIN eventos_deportivos_equipo ev ON p.equipo_visitante_id = ev.id
INNER JOIN eventos_deportivos_torneo t ON p.torneo_id = t.id
WHERE a.id = {arbitro_id} AND p.torneo_id = {torneo_id}
ORDER BY p.fecha;
"""
```

---

### 10 Lista de Sponsors por país y monto mínimo

- **URL:** `/sponsors/<str:pais>/<int:monto_min>/`
- **Vista:** `lista_sponsors`
- **Método HTTP:** GET
- **Descripción:** 
  Muestra todos los sponsors cuyo país coincide con el parámetro `pais` y cuyo monto es mayor o igual a `monto_min`.  
  Incluye los equipos asociados a cada sponsor (relación ManyToMany).
- **Parámetros:**
  - `pais` (str): País del sponsor.
  - `monto_min` (int): Monto mínimo del sponsor.
- **QuerySet optimizado:** 
  - Se filtra primero por país y luego por monto con filtros encadenados (AND implícito).  
  - Se utiliza `prefetch_related('equipos')` para obtener los equipos asociados de manera eficiente.  
  - Se ordena por nombre del sponsor (`order_by('nombre')`).  
- **Uso de `get_object_or_404`:** 
  - Se podría usar si se quisiera obtener un sponsor único por ID, asegurando que si no existe devuelve automáticamente un 404.  
  - En este caso, como devolvemos varios registros, se utiliza `filter()` para listar todos los sponsors que cumplen los criterios.
  ## Uso de `.filter()` y `.exclude()` en Django QuerySets

Django proporciona métodos muy útiles para filtrar registros en QuerySets:

### `.filter()`
- **Descripción:** Devuelve un QuerySet que contiene solo los objetos que cumplen las condiciones especificadas.  
- **Sintaxis básica:**
```python
Modelo.objects.filter(campo1=valor1, campo2=valor2)
```

### `.exclude()`
- **Descripción:** Devuelve un QuerySet excluyendo los objetos que cumplen las condiciones especificadas.
- **Sintaxis básica:**
```python
Modelo.objects.exclude(campo1=valor1)
```

- **Equivalente SQL (usando raw()):**
```python
sql = f"""
SELECT s.id, s.nombre, s.monto, s.pais, e.id AS equipo_id, e.nombre AS equipo_nombre
FROM eventos_deportivos_sponsor s
LEFT JOIN eventos_deportivos_sponsor_equipos se ON s.id = se.sponsor_id
LEFT JOIN eventos_deportivos_equipo e ON se.equipo_id = e.id
WHERE s.pais = '{pais}' AND s.monto >= {monto_min}
ORDER BY s.nombre;
"""
```

---

## Esquema Modelo Entidad-Relación (ER)

```text
Jugador 1 --- 1 EstadisticasJugador
Jugador M --- M Equipo (a través de EquipoJugador)
EquipoJugador -> atributos: fecha_ingreso, capitan
Equipo 1 --- M Partido (como local o visitante)
Torneo 1 --- M Partido
Premio 1 --- 1 Torneo
Premio 1 --- 1 Equipo (ganador)
Arbitro M --- M Partido
Sponsor M --- M Equipo
```