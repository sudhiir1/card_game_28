from django.urls import path
from game_action import views

urlpatterns = [
    path('chat', views.new_chat_message, name='new_chat_message'),
    path('get_msg', views.wait_for_new_message, name='wait_for_new_message'),
]

