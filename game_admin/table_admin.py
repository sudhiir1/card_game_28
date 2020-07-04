import logging
import random

from game_admin.common import *
from game_admin.game_player import GamePlayer, PlayerStatus
from game_admin.game_functions  import GameController

log = logging.getLogger(__name__)

class TableAdmin:

    tables = {}

    def __init__(self, table_number, num_seats):
        self.table_number = table_number
        self.players = {}
        self.seats = [None] * num_seats
        self.game = GameController(self)
        
        self.deck = "SJ,S9,SA,S1,SK,DQ,S8,S7,HJ,H9,HA,H1,HK,HQ,H8,H7,CJ,C9,CA,C1,CK,CQ,C8,C7,DJ,D9,DA,D1,DK,DQ,D8,D7".split(",")
        if num_seats == 6:
            self.deck.append("S6,H6,C6,D6".split(","))
        self.dealer_index = random.randrange(num_seats)
        self.round_start_index = self.next_player_index(self.dealer_index)
        self.bidder = None
        self.trump_card = None
        self.game_status = GameStatus.GameWaiting

    def add_player(self, player_name, player_conn):
        new_player = None
        if not self.players.get(player_name) is None:
            if  self.players[player_name].status != PlayerStatus.InActive:
                log.warn("One {} already playing in table_{}".format(player_name, self.table_number))
                return None # Todo: accept connection, send error and close connection/redirect
            else:
                log.info("{} joining back".format(player_name))
                new_player = self.players[player_name]
        else:
            log.info("{} is new to the table".format(player_name))
            new_player = GamePlayer(player_name, self)

        seat_no, player_status = self.assign_seat(new_player)
        new_player.accept_connection(player_conn, seat_no, player_status)

        log.info("Adding player to seat {} of the table_{}. Welcome {}".format(seat_no, self.table_number, player_name))
        self.send_everyone("newp", "{0}{1}{2}{3}{4}".format(player_name, SEP, player_status.value, SEP, seat_no))

        self.send_current_players_info(new_player)

        # self.game.process_message(new_player, "{0}{1}".format("redy", SEP))
     
        return new_player

    def send_current_players_info(self, to_player):
        player_info = ""
        for i in range(len(self.seats)):
            if not self.seats[i] is None:
                player = self.seats[i]
                player_info += "{0}{1}{2}{3}{4}{5}".format(SEP, player.name, SEP, player.status.value, SEP, i)
        if player_info != "":
            to_player.send_message("seat" + player_info)
            log.info("Sent msg: seat{}".format(player_info))

    def say_goodbye(self, leaving_player):
        self.remove_player(leaving_player)
        
        if not self.check_anyone_playing():
            log.info("Everyone left, cleaning up table_{}".format(self.table_number))
            TableAdmin.tables.pop(self.table_number)
            return
        self.send_everyone("byep", "{0}{1}{2}".format(leaving_player.name, SEP, leaving_player.seat))

        self.game.process_message(leaving_player, "{0}{1}".format("byep", SEP))

    def send_everyone(self, msg_type, msg):
        for _, player in self.players.items():
            if player.status != PlayerStatus.InActive:
                player.send_message("{0}{1}{2}".format(msg_type, SEP, msg))
        log.info("Sent: {}:{}".format(msg_type, msg))

    def assign_seat(self, player):
        if not self.players.get(player.name) is None and self.seats[player.seat] is None:
            log.info("Assigning {0} to seat number {1}".format(new_player.name, new_player.seat))
            self.seats[player.seat] = player
            return player.seat, PlayerStatus.Active

        self.players[player.name] = player
        for i in range(len(self.seats)):
            if self.seats[i] is None:
                self.seats[i] = player
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
            self.send_everyone("chat", "{0}{1}{2}".format(player.name, SEP, msg[5:])) # strip 'chat:' from msg
        else:
            self.game.process_message(player, msg)

    def set_players_turn(self, enable):
        for seat in self.seats:
            seat.turn = enable

    def next_player_index(self, player_index):
        if player_index == len(self.seats) - 1:
            return 0

        return player_index + 1

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
