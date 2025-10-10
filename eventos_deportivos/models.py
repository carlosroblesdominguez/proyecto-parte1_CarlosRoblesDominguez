from django.db import models

# Create your models here.

# Estadisticas Jugador
class EstadisticasJugador(models.Model):
    partidos_jugados = models.IntegerField()
    goles = models.IntegerField()
    asistencias = models.IntegerField()
    tarjetas = models.IntegerField()
    
    def __str__(self):
        return f"Estadisticas de jugador ID {self.id}"

# Jugador    
class Jugador(models.Model):
    POSICIONES = [
        ('DEL', 'Delanteros'),
        ('MED', 'Mediocampista'),
        ('DEF', 'Defensa'),
        ('POR', 'Portero'),
    ]
    
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    posicion = models.CharField(
        max_length=3, 
        choices=POSICIONES
    )
    estadisticas = models.OneToOneField(
        EstadisticasJugador,
        on_delete=models.CASCADE
    )
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# Equipo
class Equipo(models.model):
    nombre = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    fundacion = models.DateField()
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre}"
    
# Equipo Jugador (tabla intermedia)
class EquipoJugador(models.Model):
    jugador = models.ForeignKey(
        Jugador,
        on_delete=models.CASCADE
    )
    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE
    )
    
    def __str__(self):
        return f"{self.jugador} en {self.equipo}"
    
# Torneo
class Torneo(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.CharField(max_length=50)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    def __str__(self):
        return f"{self.nombre}"
    
# Partido
class Partido(models.Model):
    equipo_local = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        related_name='partidos_local'
    )
    equipo_visitante
    