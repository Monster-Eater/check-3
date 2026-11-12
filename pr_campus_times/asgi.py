"""
ASGI config for pr_campus_times project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pr_campus_times.settings")

from django.conf import settings
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import (
    AllowedHostsOriginValidator,
    OriginValidator,
)

django_asgi_app = get_asgi_application()

from pr_campus_times.ws_auth import MobileTokenAuthMiddleware
import chat.routing


websocket_app = MobileTokenAuthMiddleware(
    URLRouter(chat.routing.websocket_urlpatterns)
)

if settings.WS_ALLOWED_ORIGINS:
    origin_checked_app = OriginValidator(
        websocket_app,
        settings.WS_ALLOWED_ORIGINS,
    )
else:
    origin_checked_app = AllowedHostsOriginValidator(websocket_app)


class AllowOriginlessNativeApp:
    def __init__(self, app, origin_checked):
        self.app = app
        self.origin_checked = origin_checked

    async def __call__(self, scope, receive, send):
        has_origin = any(
            name.lower() == b"origin"
            for name, _ in scope.get("headers", [])
        )

        app = self.origin_checked if has_origin else self.app
        return await app(scope, receive, send)


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowOriginlessNativeApp(
        websocket_app,
        origin_checked_app,
    ),
})
