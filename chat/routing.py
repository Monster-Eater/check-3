from django.urls import path
from .consumers import CampusConsumer

websocket_urlpatterns = [path('ws/app/', CampusConsumer.as_asgi())]
