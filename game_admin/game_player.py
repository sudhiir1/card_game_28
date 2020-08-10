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
        self.loop = None
        self.name = name
        self.table = table
        self.seat = NO_SEAT
        self.status = PlayerStatus.InActive
        self.turn = True


    def accept_connection(self, send_conn, seat, status):
        self.send_conn = send_conn
        self.seat = seat
        self.status = status
        
        if self.send_conn is None:
            log.warn("Player {} in table {} is not connected so can't accept the person", self.name, self.table.table_number)
            return

        self.loop = asyncio.get_event_loop()
        task = self.loop.create_task(self.send_conn({'type': 'websocket.accept'}))
        
    def send_message(self, msg, yes_log=True):
        if self.send_conn is None:
            log.warn("Player {} in table {} is not connected", self.name, self.table.table_number)
            return

        task = self.loop.create_task(self.send_conn({'type': 'websocket.send', 'text': msg}))
        if yes_log:
            log.info("Sent {0}: {1}".format(self.name, msg))


    def set_inactive(self):
        self.status = PlayerStatus.InActive
        self.send_conn = None

