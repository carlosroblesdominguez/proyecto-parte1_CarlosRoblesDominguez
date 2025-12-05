from django.core.management.base import BaseCommand
from faker import Faker
import random
from datetime import timedelta, date, datetime

from eventos_deportivos.models import (
    Usuario, Manager, Arbitro,
    EstadisticasJugador, Jugador,
    Equipo, EquipoJugador,
    Torneo, Partido, Estadio,
    Sponsor, Premio
)

fake = Faker()

class Command(BaseCommand):
    help = "Genera datos de prueba para la app eventos_deportivos"

    def handle(self, *args, **kwargs):
        self.stdout.write("Generando usuarios...")
        usuarios = []
        for _ in range(5):
            u = Usuario.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='123456',
                rol=Usuario.MANAGER
            )
            Manager.objects.create(usuario=u)
            usuarios.append(u)

        for _ in range(5):
            u = Usuario.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='123456',
                rol=Usuario.ARBITRO
            )
            Arbitro.objects.create(
                usuario=u,
                nombre=fake.first_name(),
                apellido=fake.last_name(),
                licencia=fake.unique.bothify(text='LIC-#####')
            )
            usuarios.append(u)

        self.stdout.write("Generando estadisticas y jugadores...")
        jugadores = []
        for _ in range(20):
            stats = EstadisticasJugador.objects.create(
                partidos_jugados=random.randint(0, 50),
                goles=random.randint(0, 30),
                asistencias=random.randint(0, 20),
                tarjetas=random.randint(0, 10)
            )
            jugador = Jugador.objects.create(
                nombre=fake.first_name(),
                apellido=fake.last_name(),
                fecha_nacimiento=fake.date_of_birth(minimum_age=18, maximum_age=40),
                posicion=random.choice(['DEL','MED','DEF','POR']),
                estadisticas=stats
            )
            jugadores.append(jugador)

        self.stdout.write("Generando estadios...")
        estadios = []
        for _ in range(5):
            estadio = Estadio.objects.create(
                nombre=fake.city() + " Stadium",
                ciudad=fake.city(),
                capacidad=random.randint(5000, 50000),
                cubierto=random.choice([True, False])
            )
            estadios.append(estadio)

        self.stdout.write("Generando equipos...")
        equipos = []
        for i in range(5):
            equipo = Equipo.objects.create(
                nombre=fake.company(),
                ciudad=fake.city(),
                fundacion=fake.date_this_century(before_today=True, after_today=False),
                activo=True,
                estadio_principal=random.choice(estadios)
            )
            # asignar jugadores aleatorios
            for j in random.sample(jugadores, k=4):
                EquipoJugador.objects.create(
                    jugador=j,
                    equipo=equipo,
                    fecha_ingreso=fake.date_between(start_date='-5y', end_date='today'),
                    capitan=random.choice([True, False])
                )
            equipos.append(equipo)

        self.stdout.write("Generando torneos...")
        torneos = []
        arbitros = Arbitro.objects.all()
        for _ in range(3):
            torneo = Torneo.objects.create(
                nombre=fake.word() + " Cup",
                pais=fake.country(),
                fecha_inicio=fake.date_this_decade(),
                fecha_fin=fake.date_this_decade(),
                arbitro_principal=random.choice(arbitros)
            )
            torneos.append(torneo)

        self.stdout.write("Generando partidos...")
        partidos = []
        for torneo in torneos:
            for _ in range(5):
                e1, e2 = random.sample(equipos, 2)
                partido = Partido.objects.create(
                    equipo_local=e1,
                    equipo_visitante=e2,
                    fecha=fake.date_time_this_year(),
                    resultado=f"{random.randint(0,5)}-{random.randint(0,5)}",
                    torneo=torneo
                )
                # asignar arbitros aleatorios
                partido_arbitros = random.sample(list(arbitros), k=1)
                for a in partido_arbitros:
                    a.partidos.add(partido)
                partidos.append(partido)

        self.stdout.write("Generando sponsors...")
        for _ in range(5):
            sponsor = Sponsor.objects.create(
                nombre=fake.company(),
                monto=random.uniform(1000, 50000),
                pais=fake.country()
            )
            sponsor.equipos.set(random.sample(equipos, k=2))

        self.stdout.write("Generando premios...")
        for torneo in torneos:
            Premio.objects.create(
                nombre=fake.word() + " Award",
                monto=random.uniform(500, 10000),
                torneo=torneo,
                ganador=random.choice(equipos)
            )

        self.stdout.write(self.style.SUCCESS("¡Datos de prueba generados con éxito!"))
