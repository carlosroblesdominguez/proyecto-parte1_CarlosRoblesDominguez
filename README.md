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