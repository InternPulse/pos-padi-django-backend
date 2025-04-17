from django.core.cache import caches
from channels.auth import AuthMiddlewareStack


class ConnectionTrackerMiddleware:
    def __init__(self, app):
        self.app = app
        self.cache = caches["default"]

    async def __call__(self, scope, receive, send):
        # Store connection info before handling
        if scope["type"] == "websocket":
            connection_id = scope["path"] + str(hash(scope["headers "]))
            group_name = f"metrics_{scope["company"].id}"

            await self.cache.set_async(
                f"connection_filters:{connection_id}",
                scope.get("filters", {}),
                timeout=3600,
            )

            await self.cache.add_async(
                f"company:{scope["company"].id}:connections",
                connection_id,
            )

            return await self.app(scope, receive, send)
        

def ConnectionTrackerStack(inner):
    return ConnectionTrackerMiddleware(AuthMiddlewareStack(inner))