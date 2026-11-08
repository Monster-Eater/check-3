from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('updates/', views.updates, name='chat_updates'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/<int:group_id>/', views.group_room, name='group_room'),
    path('groups/<int:group_id>/details/', views.group_details, name='group_details'),
    path('groups/<int:group_id>/messages/', views.get_group_messages, name='get_group_messages'),
    path('api/<str:username>/', views.get_messages, name='get_messages'),
    path('presence/<str:username>/', views.chat_presence, name='chat_presence'),
    path('invite/<str:username>/', views.invite_user, name='invite_user'),
    path('accept-invite/<int:invite_id>/', views.accept_invite, name='accept_invite'),
    path('<str:username>/', views.chat_room, name='chat_room'),
]
