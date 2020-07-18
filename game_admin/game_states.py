import logging

from game_admin.common import *

from game_admin.game_player import GamePlayer, PlayerStatus

log = logging.getLogger(__name__)

class GameState:
    def __init__(self, cmd):
        self.cmd = cmd

    def setup(self, next_state):
        return self

    def init_game_state(self, table, prev_state):
        pass

    def action(self, table, player, msg):
        return None

class WaitForFullTable(GameState):
    def __init__(self, cmd):
        super().__init__(cmd)

    def setup(self, next_state):
        self.wait_start_state = next_state
        return self

    def action(self, table, player, msg):
        for seat in reversed(table.seats):
            if seat is None:
                log.info("Waiting for full table at Table {0}".format(table.table_number))
                return self

        return self.wait_start_state

class WaitForGameStart(GameState):

    def setup(self, next_state):
        self.deal_card_state = next_state
        return self

    def init_game_state(self, table, prev_state):
        log.info("Sending every one to open status popup..")
        table.set_everyones_turn(True)
        table.send_everyone("stat", "")
        
    def action(self, table, player, msg):
        player.turn = False
        for seat in table.seats:
            if seat is None or seat.turn:
                log.info("Waiting for others to say start")
                return self
        return self.deal_card_state

class DealCards(GameState):
    def setup(self, next_state):
        self.bidding_state = next_state
        return self

    def init_game_state(self, table, prev_state):
        log.info("Dealing every one {0} cards each on table {1}".format(len(table.seats), table.table_number))
        table.set_everyones_turn(True)
        # send each player cards: dealer_index+1: 4/3 cards
        table.send_everyone("deal", "")

    def action(self, table, player, msg):
        player.turn = False
        for seat in table.seats:
            if seat is None or seat.turn:
                log.info("Waiting for others to finish dealing cards")
                return self
        return self.bidding_state

class BidPoints(GameState):
    def setup(self, next_state):
        self.bidding_state = next_state
        return self

    def init_game_state(self, table, prev_state):
        if table.bidder_index == -1:
            table.bidder_index = table.next_player_index(table.dealer_index)
            table.bid_point = 14

        self.send_bidding_message(table)

    def action(self, table, player, msg):
        table.bid_point = int(msg[1])
        if table.bid_point == 28:
            return self
        table.seats[table.bidder_index].turn = False
        table.bidder_index = table.next_player_index(table.bidder_index)

        self.send_bidding_message(table)
        return self

    def send_bidding_message(self, table):
        bidder = table.seats[table.bidder_index]
        log.info("Inviting {0} for {1} point bidding on table {2}".format(bidder.name, table.bid_point, table.table_number))
        bidder.turn = True
        bidder.send_message("shbd{0}{1}".format(SEP, table.bid_point))