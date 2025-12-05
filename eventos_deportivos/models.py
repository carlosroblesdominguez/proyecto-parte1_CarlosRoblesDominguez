from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Usuario(AbstractUser):
    MANAGER=1
    ARBITRO=2
    ROLES=(
        (MANAGER,'manager'),
        (ARBITRO,'arbitro'),
    )
    
    rol=models.PositiveSmallIntegerField(
        choices=ROLES,default=0
    )

class Manager(models.Model):
    usuario=models.OneToOneField(Usuario,on_delete=models.CASCADE)

# Estadisticas Jugador
class EstadisticasJugador(models.Model):
    partidos_jugados = models.IntegerField()
    goles = models.IntegerField()
    asistencias = models.IntegerField()
    tarjetas = models.IntegerField()
    
    def __str__(self):
        return f"Estadisticas de jugador #{self.id}"

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
class Equipo(models.Model):
    nombre = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    fundacion = models.DateField()
    activo = models.BooleanField(default=True)
    jugadores = models.ManyToManyField(
        Jugador, 
        through='EquipoJugador',
    )
    estadio_principal = models.OneToOneField(
        'Estadio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='torneo_dirigido'
    )
    
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
    fecha_ingreso = models.DateField()
    capitan = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.jugador.nombre} {self.jugador.apellido} - {self.equipo.nombre} ({'Capitán' if self.capitan else 'Jugador'})"
    
# Torneo
class Torneo(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.CharField(max_length=50)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    arbitro_principal = models.OneToOneField(
        'Arbitro',
        on_delete=models.SET_NULL,
        null=True,
        related_name='torneo_dirigido'
    )
    
    def __str__(self):
        return f"{self.nombre}"
    
# Partido
class Partido(models.Model):
    equipo_local = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        related_name='partidos_local'
    )
    equipo_visitante = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        related_name='partidos_visitante'
    )
    fecha = models.DateTimeField()
    resultado = models.CharField(max_length=20)
    torneo = models.ForeignKey(
        Torneo,
        on_delete=models.CASCADE
    )
    
    def __str__(self):
        return f"{self.equipo_local.nombre} vs {self.equipo_visitante.nombre}"

# Arbitro    
class Arbitro(models.Model):
    usuario=models.OneToOneField(Usuario,on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    licencia = models.CharField(
        max_length=50,
        unique=True
    )
    partidos = models.ManyToManyField(Partido)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
# Estadio
class Estadio(models.Model):
    nombre = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    capacidad = models.IntegerField()
    cubierto = models.BooleanField(default=False)
    imagen = models.ImageField(upload_to='eventos_deportivos/estadios/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre}"
    
# Sponsor
class Sponsor(models.Model):
    nombre = models.CharField(max_length=100)
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    pais = models.CharField(max_length=50)
    equipos = models.ManyToManyField(Equipo)
    
    def __str__(self):
        return f"{self.nombre}"
    
class Premio(models.Model):
    nombre = models.CharField(max_length=100)
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    torneo = models.ForeignKey(
        Torneo,
        on_delete=models.CASCADE
    )
    ganador = models.ForeignKey(
        Equipo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    def __str__(self):
        return f"{self.nombre}"