"""Authenticate Flutter WebSockets using the same hashed mobile API tokens."""
import hashlib

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def _user_for_token(raw_token):
    from chat.models import MobileAPIToken
    digest = hashlib.sha256(raw_token.encode()).hexdigest()
    token = MobileAPIToken.objects.select_related('user').filter(token_hash=digest).first()
    return token.user if token and token.user.is_active else AnonymousUser()


class MobileTokenAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        user = AnonymousUser()
        for protocol in scope.get('subprotocols', []):
            if protocol.startswith('campus-token.'):
                user = await _user_for_token(protocol[len('campus-token.'):])
                break
        scope['user'] = user
        return await self.app(scope, receive, send)
