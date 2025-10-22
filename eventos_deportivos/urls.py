from django.urls import path
from . import views

urlpatterns = [
    # URL1: Lista todos los jugadores
    path('jugadores/', views.lista_jugadores, name='lista_jugadores'),
]