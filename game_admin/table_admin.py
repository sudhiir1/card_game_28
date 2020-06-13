import logging
from game_admin.common import *
from game_admin.game_player import GamePlayer

log = logging.getLogger(__name__)

class TableAdmin:

    tables = {}

    def __init__(self, table_number):
        self.table_number = table_number
        self.player_count = 0
        self.players = {}

    def add_player(self, player_name, player_conn):
        player = self.search_player_by_name(player_name)
        if player is None:
            log.info("Adding new player to the table_{}. Welcome {}".format(self.table_number, player_name))
            self.player_count += 1
            player = GamePlayer(self.player_count, player_name, player_conn, self)
            self.players[self.player_count] = player
        else:
            log.warn("Looks like {} has been playing in table_{}".format(player_name, self.table_number))

        log.info("Accepting {} to table_{}".format(player_name, self.table_number))
        player.accept_connection()

        player.table.send_everyone(server_name, "{} joined".format(player.name))

        return player

    def search_player_by_name(self, player_name):
        for _, player in self.players.items():
            if player.name == player_name:
                return player
        return None

    def say_goodbye(self, leaving_player):
        self.send_everyone_except(leaving_player, server_name, "{} left the table".format(leaving_player.name))

        self.players.pop(leaving_player.id)

        if len(self.players) == 0:
            log.info("Everyone left, cleaning up table_{}".format(self.table_number))
            TableAdmin.tables.pop(self.table_number)

    def send_everyone(self, source_name, msg):
        for id, player in self.players.items():
            player.send_message("{}: {}".format(source_name, msg))
        log.info("Send everyone: {}: {}".format(source_name, msg))

    def send_everyone_except(self, this_player, source_name, msg):
        for id, player in self.players.items():
            if not player is this_player:
                player.send_message("{}: {}".format(source_name, msg))
        log.info("Send except {}: {}: {}".format(this_player.name, source_name, msg))

    @classmethod
    def accept_player(cls, table_number, player_name, player_conn):
        if table_number not in cls.tables:
            log.info("Setting up new table, number is {}".format(table_number))
            cls.tables[table_number] = TableAdmin(table_number)
        
        table = cls.tables[table_number]
        return table.add_player(player_name, player_conn)
