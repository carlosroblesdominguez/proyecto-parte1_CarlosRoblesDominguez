from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import *

# Create your forms here.

# Formulario autenticaciones
class RegisterForm(UserCreationForm):
    roles=(
        (Usuario.MANAGER,'manager'),
        (Usuario.EDITOR,'editor'),
        (Usuario.VISUALIZADOR,'visualizador'),
        (Usuario.ARBITRO,'arbitro'),
        (Usuario.ENTRENADOR,'entrenador'),
    )
    rol=forms.ChoiceField(choices=roles)
    class Meta:
        model = Usuario
        fields=('username','email','password1','password2','rol')

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
                self.add_error("Ya existe un jugador con ese nombre y apellido.")
        
        return cleaned_data
# Jugador buscar
class BusquedaJugadorForm(forms.Form):
    nombreBusqueda=forms.CharField(required=False)
    apellidoBusqueda=forms.CharField(required=False)
    posicionBusqueda=forms.ChoiceField(choices=Jugador.POSICIONES,required=False)
    
    def clean(self):
        cleaned_data = super().clean()
    
        nombre=self.cleaned_data.get('nombreBusqueda')
        apellido=self.cleaned_data.get('apellidoBusqueda')
        posicion=self.cleaned_data.get('posicionBusqueda')
        
        # Validación: al menos 1 de los 3 campos debe estar rellenado
        if(not nombre and not apellido and posicion == "" ):
            self.add_error('nombreBusqueda',"Al menos 1 campo debe estar relleno")
            self.add_error('apellidoBusqueda',"Al menos 1 campo debe estar relleno")
            self.add_error('posicionBusqueda',"Al menos 1 campo debe estar relleno")
        else:
            # Validación de longitud mínima
            if (nombre and len(nombre)<3):
                self.add_error('nombreBusqueda',"Debe introducir al menos 3 caracteres")
            if (apellido and len(apellido)<3):
                self.add_error('apellidoBusqueda',"Debe introducir al menos 3 caracteres")
                            
        return cleaned_data
    
# Equipo create
class EquipoModelForm(forms.ModelForm):
    jugadores = forms.ModelMultipleChoiceField(
        queryset=Jugador.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False
    )

    class Meta:
        model = Equipo
        fields = ['nombre', 'ciudad', 'fundacion', 'activo', 'estadio_principal']
        labels = {
            'nombre': 'Nombre',
            'ciudad': 'ciudad',
            'fundacion': 'fundacion',
            'activo': 'activo',
            'estadio_principal': 'estadio_principal',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Sevilla'}),
            'fundacion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'estadio_principal': forms.Select(attrs={'class': 'form-select'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        ciudad = cleaned_data.get('ciudad')
        

        if nombre and ciudad:
            # Comprueba si ya existe un equipo con los mismos datos ignorandose a si mismo
            equipo_id = self.instance.id if self.instance else None
            if Equipo.objects.filter(nombre=nombre, ciudad=ciudad).exclude(id=equipo_id).exists():
                self.add_error('nombre',"Ya existe un equipo con ese nombre")
                self.add_error('ciudad',"Ya existe un equipo con esta ciudad.")
        
        return cleaned_data
    
# Equipo buscar
class BusquedaEquipoForm(forms.Form):
    nombreBusqueda=forms.CharField(required=False)
    ciudadBusqueda=forms.CharField(required=False)
    opcionesBoolean = [
        ('---------', '---------'),
        (True, 'SI'),
        (False, 'NO')
    ]
    activoBusqueda=forms.ChoiceField(choices=opcionesBoolean,required=False)
   
    
    def clean(self):
        cleaned_data = super().clean()
        
        nombre=self.cleaned_data.get('nombreBusqueda')
        ciudad=self.cleaned_data.get('ciudadBusqueda')
        activo=self.cleaned_data.get('activoBusqueda')
        
        # Validación: al menos 1 de los 3 campos debe estar rellenado
        if(not nombre and not ciudad and activo == "---------"):
            self.add_error('nombreBusqueda',"Al menos 1 campo debe estar relleno")
            self.add_error('ciudadBusqueda',"Al menos 1 campo debe estar relleno")
            self.add_error('activoBusqueda',"Al menos 1 campo debe estar relleno")
        else:
            # Validación de longitud mínima
            if (nombre and len(nombre)<3):
                self.add_error('nombreBusqueda',"Debe introducir al menos 3 caracteres")

            if (ciudad and len(ciudad)<3):
                self.add_error('ciudadBusqueda',"Debe introducir al menos 3 caracteres")
    
        return cleaned_data
    
# Estadio create
class EstadioModelForm(forms.ModelForm):
    class Meta:
        model = Estadio
        fields = ['nombre', 'ciudad', 'capacidad', 'cubierto']
        labels = {
            'nombre': 'Nombre',
            'ciudad': 'ciudad',
            'capacidad': 'capacidad',
            'cubierto': 'cubierto',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Sevilla'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Introduce capacidad'}),
            'cubierto': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        ciudad = cleaned_data.get('ciudad')
        

        if nombre and ciudad:
            # Comprueba si ya existe un estadio con los mismos datos ignorandose a si mismo
            estadio_id = self.instance.id if self.instance else None
            if Estadio.objects.filter(nombre=nombre, ciudad=ciudad).exclude(id=estadio_id).exists():
                self.add_error('nombre',"Ya existe un estadio con ese nombre en esa ciudad")
        
        return cleaned_data
    
# Estadio buscar
class BusquedaEstadioForm(forms.Form):
    nombreBusqueda=forms.CharField(required=False)
    capacidadBusqueda=forms.IntegerField(required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Capacidad Maxima'})
    )
    opcionesBoolean = [
        ('---------', '---------'),
        (True, 'SI'),
        (False, 'NO')
    ]
    cubiertoBusqueda=forms.ChoiceField(choices=opcionesBoolean,required=False)
    
    
    def clean(self):
        cleaned_data = super().clean()
        
        nombre=self.cleaned_data.get('nombreBusqueda')
        capacidad=self.cleaned_data.get('capacidadBusqueda')
        cubierto=self.cleaned_data.get('cubiertoBusqueda')
        
        # Validación: al menos 1 de los 3 campos debe estar rellenado
        if(not nombre and not capacidad and cubierto == "---------"):
            self.add_error('nombreBusqueda',"Al menos 1 campo debe estar relleno")
            self.add_error('capacidadBusqueda',"Al menos 1 campo debe estar relleno")
            self.add_error('cubiertoBusqueda',"Al menos 1 campo debe estar relleno")
        else:
            # Validación de cantidad mínima
            if (capacidad and capacidad<1):
                self.add_error('capacidadBusqueda',"La capacidad no puede ser menor a 1")
    
        return cleaned_data

# Sponsor create
class SponsorModelForm(forms.ModelForm):
    class Meta:
        model = Sponsor
        fields = ['nombre', 'pais', 'monto', 'equipos']
        labels = {
            'nombre': 'Nombre',
            'pais': 'pais',
            'monto': 'monto',
            'equipos': 'equipos',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: España'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Introduce monto'}),
            'equipos': forms.Select(attrs={'class': 'form-select'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        
        if nombre:
            # Comprueba si ya existe un sponsor con los mismos datos ignorandose a si mismo
            sponsor_id = self.instance.id if self.instance else None
            if Estadio.objects.filter(nombre=nombre).exclude(id=sponsor_id).exists():
                self.add_error('nombre',"Ya existe un sponsor con ese nombre")
        
        return cleaned_data
    
# Sponsor buscar
class BusquedaSponsorForm(forms.Form):
    nombreBusqueda=forms.CharField(required=False)
    paisBusqueda=forms.CharField(required=False)
    montoBusqueda=forms.IntegerField(required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Monto sponsor'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        nombre=self.cleaned_data.get('nombreBusqueda')
        pais=self.cleaned_data.get('paisBusqueda')
        monto=self.cleaned_data.get('montoBusqueda')
        
        # Validación: al menos 1 de los 3 campos debe estar rellenado
        if(not nombre and not pais and not monto):
            self.add_error('nombreBusqueda',"Al menos 1 campo debe estar relleno")
            self.add_error('paisBusqueda',"Al menos 1 campo debe estar relleno")
            self.add_error('montoBusqueda',"Al menos 1 campo debe estar relleno")
        else:
            # Validación de cantidad mínima
            if (monto is not None and monto < 1):
                self.add_error('montoBusqueda',"el monto no puede ser menor a 1")
 
        return cleaned_data
    
# Partido create
class PartidoModelForm(forms.ModelForm):
    class Meta:
        model = Partido
        fields = ['fecha', 'equipo_local', 'equipo_visitante', 'torneo', 'resultado']
        labels = {
            'fecha': 'fecha',
            'equipo local': 'equipo local',
            'equipo visitante': 'equipo visitante',
            'torneo': 'torneo',
            'resultado': 'resultado',
        }
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'},format='%Y-%m-%dT%H:%M'),
            'equipo_local': forms.Select(attrs={'class': 'form-control'}),
            'equipo_visitante': forms.Select(attrs={'class': 'form-control'}),
            'torneo': forms.Select(attrs={'class': 'form-control'}),
            'resultado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'x-x'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        resultado = cleaned_data.get('resultado')
        
        # Validacion de fecha: no puede repetirse
        if fecha:
            partido_id = self.instance.id if self.instance else None
            if Partido.objects.filter(fecha=fecha).exclude(id=partido_id).exists():
                self.add_error('fecha', "Ya existe un partido en esa fecha")
        
        # Validacion del resultado: debe tener formato x-x (ej: 2-1)
        if resultado:
            import re
            if not re.match(r'^\d+-\d+$', resultado):
                self.add_error('resultado', "El resultado debe tener el formato x-x (EJ: 2-1)")

        return cleaned_data

# Partido buscar
class BusquedaPartidoForm(forms.Form):
    desdeFechaBusqueda=forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    hastaFechaBusqueda=forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})    
    )
    torneoBusqueda=forms.ModelChoiceField(
        Torneo.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        desde=self.cleaned_data.get('desdeFechaBusqueda')
        hasta=self.cleaned_data.get('hastaFechaBusqueda')
        torneo=self.cleaned_data.get('torneoBusqueda')
        
        # Validación: al menos 1 de los 3 campos debe estar rellenado
        if(not desde and not hasta and not torneo):
            self.add_error('desdeFechaBusqueda',"Al menos 1 de los campos debe estar relleno")
            self.add_error('hastaFechaBusqueda',"Al menos 1 de los campos debe estar relleno")
            self.add_error('torneoBusqueda',"Al menos 1 de los campos debe estar relleno")
        else:
            # Validacion: fecha hasta no puede ser superior a fecha desde
            if(desde and hasta):
                if desde > hasta:
                    self.add_error('hastaFechaBusqueda', "La fecha hasta no puede ser anterior a la fecha desde")
        
        return cleaned_data