"""
ASGI config for card_game_28 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'card_game_28.settings')

django_application = get_asgi_application()

async def application(scope, receive, send):
    if scope['type'] == 'http':
        await django_application(scope, receive, send)
    elif scope['type'] == 'websocket':
        await websocket_application(scope, receive, send)
    else:
        raise NotImplementedError(f"Unknown scope type {scope['type']}")

clients = {}
client_id = 0

async def websocket_application(scope, receive, send):
    global clients
    global client_id
    my_id = 0
    while True:
        event = await receive()

        if event['type'] == 'websocket.connect':
            client_id += 1
            my_id = client_id
            clients[my_id] = send
            print("Connected: " + str(my_id))
            await send({
                'type': 'websocket.accept'
            })

        if event['type'] == 'websocket.disconnect':
            print("Disconnected: " + str(my_id))
            clients.pop(my_id)
            break

        if event['type'] == 'websocket.receive':
            for id, send_fn in clients.items():
                if id != my_id:
                    await send_fn({
                        'type': 'websocket.send',
                        'text': event['text']
                    })

