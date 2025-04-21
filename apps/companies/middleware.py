import uuid
from urllib.parse import parse_qs
from django.core.cache import caches
from django.contrib.auth.models import AnonymousUser
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import UntypedToken


class ConnectionTrackerMiddleware:
    def __init__(self, app):
        self.app = app
        self.cache = caches["default"]

    async def __call__(self, scope, receive, send):
        if scope["type"] != "websocket":
            return await self.app(scope, receive, send)

        try:
            # 1. Authentication
            query = parse_qs(scope.get("query_string", b"").decode())
            token = query.get("token", [None])[0]

            if not token:
                await send({"type": "websocket.close", "code": 4001})
                return

            scope["user"] = await self.get_user_from_token(token)

            # 2. Connection Tracking
            connection_id = f"{scope['path']}-{str(uuid.uuid4())}"
            company = await self.get_company(scope["user"])

            if not company:
                await send({"type": "websocket.close", "code": 4003})
                return

            await self.cache.aset(
                f"connection_filters:{connection_id}",
                scope.get("filters", {}),
                timeout=3600,
            )
            
            await self.cache.aadd(
                f"company:{company.id}:connections",
                connection_id,
                timeout=3600
            )

            scope.update({"connection_id": connection_id, "company": company})

            return await self.app(scope, receive, send)

        except InvalidToken:
            await send({"type": "websocket.close", "code": 4003})
        except Exception as e:
            print(f"Connection failed: {e}")
            await send({"type": "websocket.close", "code": 4000})

    @database_sync_to_async
    def get_company(self, user):
        return getattr(user, "company", None)

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            validated_token = UntypedToken(token)
            user = JWTAuthentication().get_user(validated_token)
            return user
        except Exception:
            return AnonymousUser


def ConnectionTrackerStack(inner):
    return ConnectionTrackerMiddleware(AuthMiddlewareStack(inner))
