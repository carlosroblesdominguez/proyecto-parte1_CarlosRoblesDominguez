from django.core.management.base import BaseCommand
from faker import Faker
from eventos_deportivos.models import (
    Jugador, EstadisticasJugador, Equipo, EquipoJugador,
    Torneo, Partido, Arbitro, Estadio, Sponsor, Premio
)
import random
from datetime import datetime, timedelta

fake = Faker()

class Command(BaseCommand):
    help = "Genera 10 datos aleatorios por cada modelo"

    def handle(self, *args, **kwargs):
        # EstadisticasJugador
        estadisticas_list = []
        for _ in range(10):
            e = EstadisticasJugador.objects.create(
                partidos_jugados=random.randint(0, 100),
                goles=random.randint(0, 50),
                asistencias=random.randint(0, 50),
                tarjetas=random.randint(0, 20)
            )
            estadisticas_list.append(e)

        # Jugador
        jugadores_list = []
        posiciones = ['DEL', 'MED', 'DEF', 'POR']
        for e in estadisticas_list:
            j = Jugador.objects.create(
                nombre=fake.first_name(),
                apellido=fake.last_name(),
                fecha_nacimiento=fake.date_of_birth(minimum_age=18, maximum_age=40),
                posicion=random.choice(posiciones),
                estadisticas=e
            )
            jugadores_list.append(j)

        # Equipo
        equipos_list = []
        for _ in range(10):
            eq = Equipo.objects.create(
                nombre=fake.company(),
                ciudad=fake.city(),
                fundacion=fake.date_between(start_date='-50y', end_date='today'),
                activo=fake.boolean()
            )
            equipos_list.append(eq)

        # EquipoJugador (tabla intermedia)
        for j in jugadores_list:
            eq = random.choice(equipos_list)
            EquipoJugador.objects.create(
                jugador=j,
                equipo=eq,
                fecha_ingreso=fake.date_between(start_date='-5y', end_date='today'),
                capitan=fake.boolean()
            )

        # Torneo
        torneos_list = []
        for _ in range(5):
            t = Torneo.objects.create(
                nombre=fake.word() + " Cup",
                pais=fake.country(),
                fecha_inicio=fake.date_between(start_date='-1y', end_date='today'),
                fecha_fin=fake.date_between(start_date='today', end_date='+1y')
            )
            torneos_list.append(t)

        # Partido
        partidos_list = []
        for _ in range(10):
            local, visitante = random.sample(equipos_list, 2)
            torneo = random.choice(torneos_list)
            p = Partido.objects.create(
                equipo_local=local,
                equipo_visitante=visitante,
                fecha=fake.date_time_this_year(),
                resultado=f"{random.randint(0,5)}-{random.randint(0,5)}",
                torneo=torneo
            )
            partidos_list.append(p)

        # Arbitro
        arbitros_list = []
        for _ in range(5):
            a = Arbitro.objects.create(
                nombre=fake.first_name(),
                apellido=fake.last_name(),
                licencia=fake.unique.bothify(text='LIC####')
            )
            # Asignar partidos al azar
            a.partidos.set(random.sample(partidos_list, k=3))
            arbitros_list.append(a)

        # Estadio
        for _ in range(5):
            Estadio.objects.create(
                nombre=fake.city() + " Stadium",
                ciudad=fake.city(),
                capacidad=random.randint(5000, 50000),
                cubierto=fake.boolean()
            )

        # Sponsor
        for _ in range(5):
            s = Sponsor.objects.create(
                nombre=fake.company(),
                monto=round(random.uniform(1000, 100000), 2),
                pais=fake.country()
            )
            s.equipos.set(random.sample(equipos_list, k=2))

        # Premio
        for t in torneos_list:
            Premio.objects.create(
                nombre=fake.word() + " Trophy",
                monto=round(random.uniform(5000, 50000), 2),
                torneo=t,
                ganador=random.choice(equipos_list)
            )

        self.stdout.write(self.style.SUCCESS("Datos generados correctamente"))
