import logging
import asyncio
from game_admin.common import *

log = logging.getLogger(__name__)

class GamePlayer:

    def __init__(self, id, name, send_conn, table):
        self.id = id
        self.name = name
        self.send_conn = send_conn
        self.table = table

    def accept_connection(self):
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.send_conn({'type': 'websocket.accept'}))
        self.send_message("{}:your_id:{}".format(server_name, self.id))
        
    def send_message(self, msg):
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.send_conn({'type': 'websocket.send', 'text': msg}))