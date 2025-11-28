from django import forms
from .models import *

# Create your forms here.

# Jugador Create   
class JugadorModelForm(forms.ModelForm):
    # Campos de estadísticas que NO están en Jugador
    partidos_jugados = forms.IntegerField(
        label="Partidos Jugados",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    goles = forms.IntegerField(
        label="Goles",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    asistencias = forms.IntegerField(
        label="Asistencias",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    tarjetas = forms.IntegerField(
        label="Tarjetas",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Jugador
        fields = ['nombre', 'apellido', 'fecha_nacimiento', 'posicion']
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'fecha_naciemiento': 'Fecha de Nacimiento',
            'posicion': 'Posición',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Messi'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'posicion': forms.Select(attrs={'class': 'form-select'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        apellido = cleaned_data.get('apellido')

        if nombre and apellido:
            # Comprueba si ya existe un jugador con los mismos datos ignorandose a si mismo
            jugador_id = self.instance.id if self.instance else None
            if Jugador.objects.filter(nombre=nombre, apellido=apellido).exclude(id=jugador_id).exists():
                raise forms.ValidationError("Ya existe un jugador con ese nombre y apellido.")
        
        return cleaned_data
# Jugador buscar
class BusquedaJugadorForm(forms.Form):
    nombreBusqueda=forms.CharField(required=True)
    apellidoBusqueda=forms.CharField(required=False)
    posicionBusqueda=forms.ChoiceField(choices=Jugador.POSICIONES,required=True)
    
    def clean(self):
        cleaned_data = super().clean()
        
        nombre=self.cleaned_data.get('nombreBusqueda')
        apellido=self.cleaned_data.get('apellidosBusqueda')
        posicion=self.cleaned_data.get('posicionBusqueda')
        
        # Validación: al menos nombre o apellido debe estar rellenado
        if(not nombre):
            self.add_error('nombreBusqueda',"Debes introducir el nombre")
        
        # Validación de longitud mínima
        if (nombre and len(nombre)<3):
            self.add_error('nombreBusqueda',"Debe introducir al menos 3 caracteres")
        if (apellido and len(apellido)<3):
            self.add_error('apellidoBusqueda',"Debe introducir al menos 3 caracteres")
                        
        return cleaned_data
'''            
# Equipo
class EquipoForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    ciudad = forms.CharField(max_length=100)
    fundacion = forms.DateField()
    activo = forms.BooleanField(default=True)
    jugadores = forms.ManyToManyField(
        Jugador, 
        through='EquipoJugador',
    )
    estadio_principal = forms.OneToOneField(
        'Estadio',
        on_delete=forms.SET_NULL,
        null=True,
        blank=True,
        related_name='torneo_dirigido'
    )
    
# Torneo
class Torneo(forms.Form):
    nombre = forms.CharField(max_length=100)
    pais = forms.CharField(max_length=50)
    fecha_inicio = forms.DateField()
    fecha_fin = forms.DateField()
    arbitro_principal = forms.OneToOneField(
        'Arbitro',
        on_delete=forms.SET_NULL,
        null=True,
        related_name='torneo_dirigido'
    )
    
# Partido
class Partido(forms.Form):
    equipo_local = forms.ForeignKey(
        Equipo,
        on_delete=forms.CASCADE,
        related_name='partidos_local'
    )
    equipo_visitante = forms.ForeignKey(
        Equipo,
        on_delete=forms.CASCADE,
        related_name='partidos_visitante'
    )
    fecha = forms.DateTimeField()
    resultado = forms.CharField(max_length=20)
    torneo = forms.ForeignKey(
        Torneo,
        on_delete=forms.CASCADE
    )

# Arbitro    
class Arbitro(forms.Form):
    nombre = forms.CharField(max_length=100)
    apellido = forms.CharField(max_length=100)
    licencia = forms.CharField(
        max_length=50,
        unique=True
    )
    partidos = forms.ManyToManyField(Partido)
    
# Estadio
class Estadio(forms.Form):
    nombre = forms.CharField(max_length=100)
    ciudad = forms.CharField(max_length=100)
    capacidad = forms.IntegerField()
    cubierto = forms.BooleanField(required=False)
    
# Sponsor
class Sponsor(forms.Form):
    nombre = forms.CharField(max_length=100)
    monto = forms.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    pais = forms.CharField(max_length=50)
    equipos = forms.ManyToManyField(Equipo)
    
class Premio(forms.Form):
    nombre = forms.CharField(max_length=100)
    monto = forms.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    torneo = forms.ForeignKey(
        Torneo,
        on_delete=forms.CASCADE
    )
    ganador = forms.ForeignKey(
        Equipo,
        on_delete=forms.SET_NULL,
        null=True,
        blank=True
    )
'''