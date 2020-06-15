import logging
import asyncio
from enum import Enum 
from game_admin.common import *

log = logging.getLogger(__name__)

class PlayerStatus(Enum):
    InActive = 0
    Active = 1
    Spectator = 2

class GamePlayer:

    def __init__(self, name, table):
        self.name = name
        self.table = table
        self.seat = NO_SEAT
        self.status = PlayerStatus.InActive


    def accept_connection(self, send_conn, seat, status):
        self.send_conn = send_conn
        self.seat = seat
        self.status = status
        
        if self.send_conn is None:
            log.warn("Player {} in table {} is not connected so can't accept the person", self.name, self.table.table_number)
            return

        loop = asyncio.get_event_loop()
        task = loop.create_task(self.send_conn({'type': 'websocket.accept'}))

        self.send_message("seat:{0}{1}{2}".format(self.seat, SEP, self.status.value))
        
    def send_message(self, msg):
        if self.send_conn is None:
            log.warn("Player {} in table {} is not connected", self.name, self.table.table_number)
            return
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.send_conn({'type': 'websocket.send', 'text': msg}))

    def set_inactive(self):
        self.status = PlayerStatus.InActive
        self.send_conn = None
