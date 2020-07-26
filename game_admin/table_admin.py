import logging
import random

from game_admin.common import *
from game_admin.game_player import GamePlayer, PlayerStatus
from game_admin.game_functions  import GameController

log = logging.getLogger(__name__)

class Chair:
    def __init__(self, table, seat_no):
        self.table = table
        self.seat_no = seat_no
        self.player = None
        self.turn = False
        self.cards = []

    def deal_cards(self, cards, deal_pos):
        self.cards.append(cards)
        self.player.send_message("deal{0}{1}{2}{3}".format(SEP, deal_pos, SEP, ",".join(cards)))

    @classmethod
    def addChairs(cls, table, num_chairs):
        chairs = []
        for i in range(num_chairs):
            chairs.append(Chair(table, i))
        return chairs

class TableAdmin:
    def __init__(self, table_number, num_seats):
        self.table_number = table_number
        self.num_seats = num_seats
        self.seats = Chair.addChairs(self, num_seats)
        self.gamers = {}
        self.game = GameController(self)
        
        self.deck = "SJ,S9,SA,S1,SK,DQ,S8,S7,HJ,H9,HA,H1,HK,HQ,H8,H7,CJ,C9,CA,C1,CK,CQ,C8,C7,DJ,D9,DA,D1,DK,DQ,D8,D7".split(",")
        if num_seats == 6:
            self.deck.append("S6,H6,C6,D6".split(","))
        self.dealer_index = -1
        self.player_index = -1
        self.bidder_index = -1
        self.bid_point = -1
        self.evenTeamCards = []
        self.oddTeamCards = []

    def add_player(self, name, conn):
        new_player = player = self.check_returning_player(name)
        
        if new_player is None:
            log.info("{} is new to the table".format(name))
            new_player = GamePlayer(name, self)

        seat_no, player_status = self.assign_seat(new_player)
        new_player.accept_connection(conn, seat_no, player_status)

        self.process_new_message(new_player, "{0}{1}{2}".format("newp", SEP, int(player is None)))
     
        return new_player

    def check_returning_player(self, name):
        if self.gamers.get(name) is None:
            return None
        if  self.gamers[name].status != PlayerStatus.InActive:
            log.warn("One {} already playing in table_{}".format(name, self.table_number))
            return None # Todo: accept connection, send error and close connection/redirect

        log.info("{} joining back".format(name))
        return self.gamers[name]

    def assign_seat(self, player):
        if not self.gamers.get(player.name) is None and self.seats[player.seat].player is None:
            log.info("Assigning {0} to seat number {1}".format(player.name, player.seat))
            self.seats[player.seat].player = player
            return player.seat, PlayerStatus.Active

        self.gamers[player.name] = player
        for i in range(len(self.seats)):
            if self.seats[i].player is None:
                self.seats[i].player = player
                return i, PlayerStatus.Active
        return NO_SEAT, PlayerStatus.Spectator
        
    def send_current_players_info(self, to_player):
        player_info = ""
        for i in range(len(self.seats)):
            if not self.seats[i].player is None:
                player = self.seats[i].player
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

    def send_everyone(self, msg_type, msg):
        for _, player in self.gamers.items():
            if player.status != PlayerStatus.InActive:
                player.send_message("{0}{1}{2}".format(msg_type, SEP, msg), False)
        log.info("Sent Everyone: {}:{}".format(msg_type, msg))

    def set_everyones_turn(self, enable):
        for seat in self.seats:
            seat.turn = enable


    def remove_player(self, leaving_player):
        leaving_player.set_inactive()

        if leaving_player.seat != NO_SEAT:
            self.seats[leaving_player.seat].player = None

    def check_anyone_playing(self):
        for _, player in self.gamers.items():
            if player.status != PlayerStatus.InActive:
                return True
        return False

    def process_new_message(self, player, msg):
        if msg.startswith("chat:"):
            self.send_everyone("chat", "{0}{1}{2}".format(player.name, SEP, msg[5:])) # strip 'chat:' from msg
        else:
            self.game.process_message(player, msg)

    def next_player_index(self, player_index):
        if player_index == len(self.seats) - 1:
            return 0

        return player_index + 1

    def assign_card_to_team(self, cards_played):
        for seat_index, card in cards_played.items():
            log.info("{0} played {1}".format(self.seats[seat_index].player.name, card))
        return next(iter(cards_played))


    tables = {}
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
    #     for id, player in self.gamers.items():
    #         if not player is this_player:
    #             player.send_message("{}: {}".format(source_name, msg))
    #     log.info("Send except {}: {}: {}".format(this_player.name, source_name, msg))
