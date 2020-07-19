import logging

from game_admin.common import *

from game_admin.game_player import GamePlayer, PlayerStatus

log = logging.getLogger(__name__)

class GameState:
    def __init__(self, cmd):
        self.cmd = cmd

    def setup(self, next_states):
        return self

    def init_game_state(self, table, prev_state):
        pass

    def action(self, table, player, msg):
        return None

class WaitForFullTable(GameState):
    def __init__(self, cmd):
        super().__init__(cmd)

    def setup(self, next_states):
        self.wait_start_state = next_states[0]
        return self

    def action(self, table, player, msg):
        for seat in reversed(table.seats):
            if seat is None:
                log.info("Waiting for full table at Table {0}".format(table.table_number))
                return self

        return self.wait_start_state

class WaitForGameStart(GameState):

    def setup(self, next_states):
        self.deal_state = next_states[0]
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
        return self.deal_state

class DealCards(GameState):
    def setup(self, next_states):
        self.bidding_state = next_states[0]
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
    def setup(self, next_states):
        self.keep_trump_state = next_states[0]
        return self

    def init_game_state(self, table, prev_state):
        if table.bidder_index == -1:
            table.bidder_index = table.next_player_index(table.dealer_index)
            table.bid_point = 14

        self.send_bidding_message(table, table.seats[table.bidder_index], table.bid_point)

    def action(self, table, player, msg):
        table.bid_point = int(msg[1])
        if table.bid_point == 20:
            return self.keep_trump_state
        if table.bid_point == 28:
            return self.keep_trump_state
        table.seats[table.bidder_index].turn = False
        table.bidder_index = table.next_player_index(table.bidder_index)

        self.send_bidding_message(table, table.seats[table.bidder_index], table.bid_point)
        return self

    def send_bidding_message(self, table, bidder, bid_point):
        log.info("Inviting {0} for {1} point bidding on table {2}".format(bidder.name, bid_point, table.table_number))
        bidder.turn = True
        bidder.send_message("shbd{0}{1}".format(SEP, bid_point))

class KeepTrumpCard(GameState):
    def setup(self, next_states):
        self.deal_state = next_states[0]
        self.play_state = next_states[1]
        return self

    def init_game_state(self, table, prev_state):
        bidder = table.seats[table.bidder_index]
        bidder.send_message("ktrm{0}".format(SEP))

    def action(self, table, player, msg):
        log.info("{0} kept trump on table {1}".format(player.name, table.table_number))
        if table.bid_point == 20:
            return self.deal_state
        else:
            return self.play_state

        return self


class PlayCards(GameState):
    def setup(self, next_states):
        self.wait_start_state = next_states[0]
        return self

    def init_game_state(self, table, prev_state):
        pass

    def action(self, table, player, msg):
        return self
