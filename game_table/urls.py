from django.urls import path
from game_table import views

urlpatterns = [
        path('', views.host_game, name='host_game'), # cardgame28.com
        path('link', views.game_link, name='game_link'), # Todo: page with game link
        path('play', views.player_login, name='player_login'), # Player join page
        path('table', views.game_table, name='game_table'), # game table
        ]

