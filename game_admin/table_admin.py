import logging
from game_admin.common import *
from game_admin.game_player import GamePlayer, PlayerStatus

log = logging.getLogger(__name__)

class TableAdmin:

    tables = {}

    def __init__(self, table_number, num_seats):
        self.table_number = table_number
        self.players = {}
        self.seats = [None] * num_seats

    def add_player(self, player_name, player_conn):
        new_player = None
        if not self.players.get(player_name) is None:
            if  self.players[player_name].status != PlayerStatus.InActive:
                log.warn("One {} already playing in table_{}".format(player_name, self.table_number))
                return None # Todo: accept connection, send error and close connection/redirect
            else:
                new_player = self.players[player_name]
        else:
            self.players[player_name] = new_player = GamePlayer(player_name, self)

        seat_no, player_status = self.assign_seat(new_player)
        new_player.accept_connection(player_conn, seat_no, player_status)

        log.info("Adding player to seat {} of the table_{}. Welcome {}".format(seat_no, self.table_number, player_name))
        self.send_everyone("newp", "{0}{1}{2}".format(player_name, SEP, seat_no))

        return new_player

    def say_goodbye(self, leaving_player):
        self.remove_player(leaving_player)
        
        if not self.check_anyone_playing():
            log.info("Everyone left, cleaning up table_{}".format(self.table_number))
            TableAdmin.tables.pop(self.table_number)
            return
        self.send_everyone("byep", "{0}{1}{2}".format(leaving_player.name, SEP, leaving_player.seat))

    def send_everyone(self, msg_type, msg):
        for _, player in self.players.items():
            if player.status != PlayerStatus.InActive:
                player.send_message("{0}{1}{2}".format(msg_type, SEP, msg))
        log.info("Sent: {}: {}".format(msg_type, msg))


    def assign_seat(self, new_player):
        if new_player.seat != NO_SEAT and self.seats[new_player.seat] is None:
            log.info("Assigning {} seat number {} the same seat he was earlier".format(new_player.name, new_player.seat))
            return new_player.seat, PlayerStatus.Active

        for i in range(len(self.seats)):
            if self.seats[i] is None:
                self.seats[i] = new_player
                return i, PlayerStatus.Active
        return NO_SEAT, PlayerStatus.Spectator

    def remove_player(self, leaving_player):
        # self.players.pop(leaving_player.name)
        leaving_player.set_inactive()

        if leaving_player.seat != NO_SEAT:
            self.seats[leaving_player.seat] = None

    def check_anyone_playing(self):
        for _, player in self.players.items():
            if player.status != PlayerStatus.InActive:
                return True
        return False

    def process_new_message(self, player, msg):
        if msg.startswith("chat:"):
            self.send_everyone("chat", "{}::{}".format(player.name, msg[5:])) # strip 'chat:' from msg

    @classmethod
    def accept_player(cls, table_number, player_name, player_conn):
        table_number = int(table_number)
        if table_number not in cls.tables:
            log.info("Setting up new table, number is {}".format(table_number))
            num_seats = cls.get_table_info(table_number)
            cls.tables[table_number] = TableAdmin(table_number, num_seats)
        
        table = cls.tables[table_number]
        return table.add_player(player_name, player_conn)

    @classmethod
    def get_table_info(cls, table_number):
        return 4 if table_number % 2 == 0 else 6


    # def send_everyone_except(self, this_player, source_name, msg):
    #     for id, player in self.players.items():
    #         if not player is this_player:
    #             player.send_message("{}: {}".format(source_name, msg))
    #     log.info("Send except {}: {}: {}".format(this_player.name, source_name, msg))
