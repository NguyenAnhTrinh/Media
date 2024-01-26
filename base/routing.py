from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from base.consumers import ChatConsumer

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                path(r"ws/room/(?P<room_id>\d+)/$", ChatConsumer.as_asgi()),
            ]
        )
    ),
})
