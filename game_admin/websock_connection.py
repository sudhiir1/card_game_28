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

