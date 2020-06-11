from django.urls import path
from game_table import views

urlpatterns = [
        path('', views.game_table, name='game_table'),
        ]

