from django.core.management.base import BaseCommand
from eventos_deportivos.models import *
from faker import Faker
import random

fake = Faker()

class Command(BaseCommand):
    help = 'Generar datos de prueba sin violar UNIQUE/OneToOne'

    def handle(self, *args, **kwargs):

        # --- USUARIOS ---
        usuarios = []
        for _ in range(5):
            rol = random.choice([Usuario.MANAGER, Usuario.ARBITRO])
            u = Usuario.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='1234',
                rol=rol
            )
            usuarios.append(u)
            if rol == Usuario.ARBITRO:
                Arbitro.objects.create(
                    usuario=u,
                    nombre=fake.first_name(),
                    apellido=fake.last_name(),
                    licencia=fake.unique.bothify(text='LIC-#####')
                )
            else:
                Manager.objects.create(usuario=u)

        # --- ESTADIOS ---
        estadios = []
        for _ in range(3):
            e = Estadio.objects.create(
                nombre=fake.company(),
                ciudad=fake.city(),
                capacidad=random.randint(5000, 50000),
                cubierto=random.choice([True, False])
            )
            estadios.append(e)

        # --- EQUIPOS ---
        equipos = []
        for i in range(len(estadios)):
            eq = Equipo.objects.create(
                nombre=fake.company(),
                ciudad=fake.city(),
                fundacion=fake.date_between(start_date='-100y', end_date='-10y'),
                activo=True,
                estadio_principal=estadios[i]  # cada equipo un estadio
            )
            equipos.append(eq)

        # --- JUGADORES ---
        jugadores = []
        for _ in range(10):
            stats = EstadisticasJugador.objects.create(
                partidos_jugados=random.randint(0, 100),
                goles=random.randint(0, 50),
                asistencias=random.randint(0, 50),
                tarjetas=random.randint(0, 20)
            )
            j = Jugador.objects.create(
                nombre=fake.first_name(),
                apellido=fake.last_name(),
                fecha_nacimiento=fake.date_of_birth(minimum_age=18, maximum_age=40),
                posicion=random.choice([p[0] for p in Jugador.POSICIONES]),
                estadisticas=stats
            )
            jugadores.append(j)

        # --- ASIGNAR JUGADORES A EQUIPOS ---
        for eq in equipos:
            eq_jugadores = random.sample(jugadores, k=3)
            for j in eq_jugadores:
                EquipoJugador.objects.create(
                    jugador=j,
                    equipo=eq,
                    fecha_ingreso=fake.date_between(start_date='-5y', end_date='today'),
                    capitan=random.choice([True, False])
                )

        # --- TORNEOS ---
        arbitros = list(Arbitro.objects.all())
        torneos = []
        for i, arb in enumerate(arbitros):
            t = Torneo.objects.create(
                nombre=fake.company(),
                pais=fake.country(),
                fecha_inicio=fake.date_between(start_date='-2y', end_date='today'),
                fecha_fin=fake.date_between(start_date='today', end_date='+1y'),
                arbitro_principal=arb  # cada torneo un árbitro distinto
            )
            torneos.append(t)

        # --- PARTIDOS ---
        for _ in range(5):
            Partido.objects.create(
                equipo_local=random.choice(equipos),
                equipo_visitante=random.choice([e for e in equipos if e != equipos[0]]),
                fecha=fake.date_time_between(start_date='-1y', end_date='now'),
                resultado=f"{random.randint(0,5)}-{random.randint(0,5)}",
                torneo=random.choice(torneos)
            )

        # --- SPONSORS ---
        for _ in range(3):
            s = Sponsor.objects.create(
                nombre=fake.company(),
                monto=random.uniform(1000, 50000),
                pais=fake.country()
            )
            s.equipos.set(random.sample(equipos, k=2))

        # --- PREMIOS ---
        for t in torneos:
            Premio.objects.create(
                nombre=fake.catch_phrase(),
                monto=random.uniform(1000, 50000),
                torneo=t,
                ganador=random.choice(equipos)
            )

        self.stdout.write(self.style.SUCCESS('Datos generados correctamente.'))
