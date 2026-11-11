"""
ASGI config for pr_campus_times project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pr_campus_times.settings')

django_asgi_app = get_asgi_application()
from pr_campus_times.ws_auth import MobileTokenAuthMiddleware
import chat.routing

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': (
        OriginValidator(MobileTokenAuthMiddleware(URLRouter(chat.routing.websocket_urlpatterns)), settings.WS_ALLOWED_ORIGINS)
        if settings.WS_ALLOWED_ORIGINS
        else AllowedHostsOriginValidator(MobileTokenAuthMiddleware(URLRouter(chat.routing.websocket_urlpatterns)))
    ),
})
