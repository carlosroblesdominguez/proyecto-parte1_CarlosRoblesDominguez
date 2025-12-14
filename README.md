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

### Páginas de Error Personalizadas

Se han creado páginas de error personalizadas para los 4 tipos de error más comunes en Django. Todas heredan de `error_base.html` y mantienen un estilo uniforme con el resto del proyecto.

#### Archivos de Templates
- **`error_base.html`**  
  Plantilla base para los errores. Incluye:
  - Estructura HTML común.
  - Bloques `{% block title %}` y `{% block content %}` para sobreescribir el título y contenido específico de cada error.
  - Estilo uniforme (fuente Arial, fondo gris claro, botón de volver al inicio).

- **`error_400.html`**  
  - Hereda de `error_base.html`.
  - Muestra un mensaje de "Bad Request" indicando que la solicitud no puede ser procesada por el servidor.
  
- **`error_403.html`**  
  - Hereda de `error_base.html`.
  - Muestra un mensaje de "Forbidden" indicando que el usuario no tiene permisos para acceder a la página.
  
- **`error_404.html`**  
  - Hereda de `error_base.html`.
  - Muestra un mensaje de "Not Found" indicando que la página solicitada no existe.

- **`error_500.html`**  
  - Hereda de `error_base.html`.
  - Muestra un mensaje de "Internal Server Error" indicando que se produjo un error en el servidor.

#### Funcionamiento
- Cada página utiliza los bloques de `error_base.html` para personalizar el título y el contenido del error.
- Se proporciona un enlace de navegación para volver a la página principal.
- Permite mantener un diseño coherente con los demás templates del proyecto.
- Para probar los errores:
  - **404:** acceder a una URL inexistente.
  - **400:** enviar una solicitud inválida.
  - **403:** intentar acceder a un recurso sin permisos.
  - **500:** provocar un fallo interno en una vista.

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

# Proyecto Django — Uso de Template Tags y Filters

Este proyecto utiliza múltiples **template tags**, **operadores en condicionales** y **template filters** para mostrar la información de manera clara y dinámica.

---

## 1. Template Tags usados (al menos 5)

| Tag             | Páginas donde se usa                     | Comentario |
|-----------------|----------------------------------------|------------|
| `{% for ... %}` | Todas las páginas de listas y detalles | Para iterar sobre QuerySets, por ejemplo jugadores, equipos, partidos, torneos, sponsors, árbitros. |
| `{% empty %}`   | Todas las páginas de listas             | Para mostrar un mensaje cuando no hay registros. Ej.: `No hay jugadores registrados`. |
| `{% if ... %}`  | `lista_equipos.html`, `detalle_jugador.html` | Para mostrar valores por defecto o controlar visualización. |
| `{% else %}`    | `lista_equipos.html`, `detalle_jugador.html` | Complementa los if para casos alternativos. |
| `{% block ... %}` | Todas las páginas principales         | Para definir bloques heredables de `base.html` (contenido, cabecera, título). |
| `{% extends ... %}` | Todas las páginas principales       | Para heredar la estructura de `base.html`. |
| `{% load static %}` | `base.html`                          | Para cargar archivos estáticos (CSS, JS, imágenes). |

---

## 2. Operadores diferentes usados en los `if` (al menos 5)

| Operador        | Página donde se usa                       | Ejemplo |
|-----------------|-----------------------------------------|---------|
| `==`             | `detalle_jugador.html`                  | `{% if jugador.posicion == "Delantero" %}` |
| `!=`             | `lista_equipos.html`                    | `{% if equipo.activo != False %}` |
| `>`              | `lista_sponsors.html`                    | `{% if sponsor.monto > 10000 %}` |
| `<`              | `lista_sponsors.html`                    | `{% if sponsor.monto < 50000 %}` |
| `>=`             | `lista_sponsors.html`                    | `{% if sponsor.monto >= 20000 %}` |
| `<=`             | `detalle_jugador.html`                   | `{% if jugador.estadisticas.goles <= 0 %}` |
| `and`            | `detalle_arbitro_torneo.html`            | `{% if partidos|length > 0 and arbitro.nombre %}` |
| `or`             | `detalle_partido.html`                    | `{% if arbitros|length == 0 or partido.resultado == None %}` |

> Nota: Se han usado **8 operadores distintos**, cumpliendo y superando el mínimo de 5.

---

## 3. Template Filters usados (al menos 10)

| Filter                  | Páginas donde se usa                     | Comentario |
|--------------------------|----------------------------------------|------------|
| `date:"d/m/Y"`           | Todas las páginas con fechas (`detalle_jugador`, `lista_equipos`, `detalle_partido`, etc.) | Formato de fecha día/mes/año. |
| `time:"H:i"`             | `detalle_partido.html`, `lista_partidos.html` | Mostrar solo hora y minutos de la fecha. |
| `upper`                  | `detalle_jugador.html`, `detalle_arbitro_torneo.html` | Para poner en mayúsculas nombres o posiciones. |
| `lower`                  | `lista_torneos.html`, `lista_sponsors.html` | Para mostrar el país en minúsculas. |
| `default_if_none:"0"`    | `lista_jugadores.html`, `detalle_jugador.html` | Mostrar valor 0 si el campo es None. |
| `default:"Desconocida"`  | `detalle_jugador.html`                  | Valor por defecto si no hay posición. |
| `truncatechars:10`       | `lista_jugadores.html`                  | Trunca nombres largos a 10 caracteres. |
| `yesno:"Sí,No"`          | `lista_equipos.html`                     | Mostrar "Sí" o "No" para booleanos. |
| `floatformat:2`          | `lista_sponsors.html`                    | Mostrar monto con 2 decimales. |
| `length`                 | `lista_equipos.html`, `lista_torneos.html`, `lista_sponsors.html` | Mostrar número de elementos en ManyToMany o listas. |
| `safe` (opcional)        | No usado actualmente, se puede usar para contenido HTML | Permitir renderizar HTML en templates. |

> Total de **10 filters usados** efectivamente en diferentes páginas.

---

## Resumen

- **Template tags:** Se usan todos los principales (`for`, `if`, `else`, `empty`, `block`, `extends`, `load static`), cumpliendo el requisito mínimo.  
- **Operadores en if:** Se usan `==, !=, >, <, >=, <=, and, or` — más de 5.  
- **Template filters:** Se usan 10 filters diferentes para fechas, textos, valores por defecto y longitud de listas.  

---

# FORMULARIOS

# Validaciones y Widgets de la Aplicación

## 1. Jugador
**Validaciones:**
- Nombre y apellido únicos: no puede existir otro jugador con el mismo nombre y apellido.
- En la búsqueda: al menos un campo debe estar rellenado; si se rellena nombre o apellido, mínimo 3 caracteres.
- Estadísticas (partidos_jugados, goles, asistencias, tarjetas) como enteros positivos.

**Widgets:**
- `TextInput` para nombre y apellido con clase `form-control`.
- `DateInput` para fecha de nacimiento (`type="date"`, clase `form-control`).
- `Select` para posición con clase `form-select`.
- `NumberInput` para estadísticas con clase `form-control`.

---

## 2. Equipo
**Validaciones:**
- Nombre y ciudad únicos: no puede existir otro equipo con el mismo nombre y ciudad.
- En la búsqueda: al menos un campo debe estar rellenado; nombre y ciudad mínimo 3 caracteres.

**Widgets:**
- `TextInput` para nombre y ciudad con clase `form-control`.
- `DateInput` para fundación (`type="date"`, clase `form-control`).
- `CheckboxInput` para activo (`class="form-check-input"`).
- `Select` para estadio principal y `SelectMultiple` para jugadores con clase `form-select`.

---

## 3. Estadio
**Validaciones:**
- Nombre y ciudad únicos.
- En la búsqueda: al menos un campo debe estar rellenado.
- Capacidad mínima 1.
- Para la imagen, usar `ClearableFileInput` (permite subir/limpiar imagen).

**Widgets:**
- `TextInput` para nombre y ciudad con clase `form-control`.
- `NumberInput` para capacidad con clase `form-control`.
- `CheckboxInput` para cubierto con clase `form-check-input`.
- `ClearableFileInput` para imagen con clase `form-control`.

---

## 4. Sponsor
**Validaciones:**
- Nombre único.
- En la búsqueda: al menos un campo debe estar rellenado.
- Monto mínimo 1.

**Widgets:**
- `TextInput` para nombre y país con clase `form-control`.
- `NumberInput` para monto con clase `form-control`.
- `Select` para equipos con clase `form-select`.

---

## 5. Partido
**Validaciones:**
- Fecha única (no puede haber otro partido en la misma fecha).
- Resultado con formato `x-x` (ej: 2-1).
- En la búsqueda: al menos un campo debe estar rellenado.
- Fecha hasta no puede ser anterior a fecha desde.

**Widgets:**
- `DateTimeInput` para fecha (`type="datetime-local"`, clase `form-control`).
- `Select` para equipo local, visitante y torneo con clase `form-control`.
- `TextInput` para resultado con clase `form-control`.

---

## 6. Torneo
**Validaciones:**
- Nombre único.
- Fecha fin no puede ser anterior a fecha inicio.
- En la búsqueda: al menos un campo debe estar rellenado.
- País no puede contener números.

**Widgets:**
- `TextInput` para nombre y país con clase `form-control`.
- `DateInput` para fecha_inicio y fecha_fin (`type="date"`, clase `form-control`).
- `Select` para árbitro principal con clase `form-control`.

---

## Subida de imágenes
Para cualquier modelo que incluya imágenes (ej: `Estadio`):
1. En el formulario usar `ClearableFileInput`.
2. En la vista al crear o editar, recoger archivos con `files=request.FILES`.
3. Asegurarse de configurar `MEDIA_URL` y `MEDIA_ROOT` en `settings.py` y añadir `urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)` en `urls.py`.

---

**Resumen de Widgets por Modelo:**
- **Jugador:** TextInput, DateInput, Select, NumberInput.
- **Equipo:** TextInput, DateInput, CheckboxInput, Select, SelectMultiple.
- **Estadio:** TextInput, NumberInput, CheckboxInput, ClearableFileInput.
- **Sponsor:** TextInput, NumberInput, Select.
- **Partido:** DateTimeInput, Select, TextInput.
- **Torneo:** TextInput, DateInput, Select.

---

# Proyecto Deportes - Roles y Permisos

## Tipos de usuario y funcionalidades

En la aplicación existen **dos roles/usuarios principales**: **Managers** y **Arbitros**.  

---

### 1. Grupo: Arbitros
Usuarios que pertenecen a este grupo pueden gestionar **estadios, partidos y torneos**.  

**Permisos asociados:**

| Modelo   | Permiso            |
|----------|--------------------|
| Estadio  | Can add estadio    |
| Estadio  | Can change estadio |
| Estadio  | Can delete estadio |
| Partido  | Can add partido    |
| Partido  | Can change partido |
| Partido  | Can delete partido |
| Torneo   | Can add torneo     |
| Torneo   | Can change torneo  |
| Torneo   | Can delete torneo  |

**Funcionalidades:**
- Crear, modificar y eliminar estadios.
- Crear, modificar y eliminar partidos.
- Crear, modificar y eliminar torneos.
- Ver solo los objetos asignados o creados por ellos (si aplica).
- Gestionar solo los objetos que ellos mismos han creado (`creado_por=user`).

---

### 2. Grupo: Managers
Usuarios que pertenecen a este grupo pueden gestionar **equipos, jugadores y sponsors**.  

**Permisos asociados:**

| Modelo   | Permiso            |
|----------|--------------------|
| Equipo   | Can add equipo     |
| Equipo   | Can change equipo  |
| Equipo   | Can delete equipo  |
| Jugador  | Can add jugador    |
| Jugador  | Can change jugador |
| Jugador  | Can delete jugador |
| Sponsor  | Can add sponsor    |
| Sponsor  | Can change sponsor |
| Sponsor  | Can delete sponsor |

**Funcionalidades:**
- Crear, modificar y eliminar equipos.
- Crear, modificar y eliminar jugadores.
- Crear, modificar y eliminar sponsors.
- Ver solo los objetos asignados o creados por ellos (si aplica).
- Gestionar solo los objetos que ellos mismos han creado (`creado_por=user`).

---