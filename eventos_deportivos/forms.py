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
                self.add_error("Ya existe un jugador con ese nombre y apellido.")
        
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
    ciudadBusqueda=forms.CharField(required=True)
    activoBusqueda=forms.BooleanField(required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        
        nombre=self.cleaned_data.get('nombreBusqueda')
        ciudad=self.cleaned_data.get('ciudadBusqueda')
        activo=self.cleaned_data.get('activoBusqueda')
        
        # Validación: al menos ciudad debe estar rellenado
        if(not ciudad):
            self.add_error('ciudadBusqueda',"Debes introducir la ciudad")
        
        # Validación de longitud mínima
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
    capacidadBusqueda=forms.IntegerField(required=True)
    cubiertoBusqueda=forms.BooleanField(required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        
        nombre=self.cleaned_data.get('nombreBusqueda')
        capacidad=self.cleaned_data.get('capacidadBusqueda')
        cubierto=self.cleaned_data.get('cubiertoBusqueda')
        
        # Validación: capacidad debe estar rellenado
        if(not capacidad):
            self.add_error('capacidadBusqueda',"Debes introducir al menos un valor de 1")
        
        # Validación de longitud mínima
        if (capacidad and len(capacidad)<1):
            self.add_error('capacidadBusqueda',"La capacidad no puede ser menor a 1")
 
        return cleaned_data
