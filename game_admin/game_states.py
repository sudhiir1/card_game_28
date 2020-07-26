import logging
import random

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

    def init_game_state(self, table, prev_state):
        log.info("Getting ready to accept players")
        table.set_everyones_turn(True)

    def action(self, table, player, msg):
        table.seats[player.seat].turn = False
        for seat in reversed(table.seats):
            if seat.player is None:
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
        table.seats[player.seat].turn = False
        for seat in table.seats:
            if seat.player is None or seat.turn:
                log.info("Waiting for others to say start")
                return self

        self.prep_for_new_game(table)
        return self.deal_state

    def prep_for_new_game(self, table):
        random.shuffle(table.deck)
        table.dealer_index = random.randrange(table.num_seats)
        table.bidder_index = -1
        table.player_index = -1
        table.evenTeamCards = []
        table.oddTeamCards = []

class DealCards(GameState):
    def setup(self, next_states):
        self.bidding_state = next_states[0]
        return self

    def init_game_state(self, table, prev_state):
        cards_to_deal = 3 if len(table.seats) == 6 else 4
        log.info("Dealing every one {0} cards each on table {1}".format(cards_to_deal, table.table_number))
        table.set_everyones_turn(True)

        deal_index = table.dealer_index
        for i in range(table.num_seats):
            deal_index = table.next_player_index(deal_index)
            table.seats[deal_index].deal_cards(table.deck[:cards_to_deal], i)
            del table.deck[:cards_to_deal]

    def action(self, table, player, msg):
        table.seats[player.seat].turn = False
        for seat in table.seats:
            if seat.player is None or seat.turn:
                log.info("Waiting for others to finish dealing cards")
                return self
        return self.bidding_state

class BidPoints(GameState):
    def setup(self, next_states):
        self.keep_trump_state = next_states[0]
        return self

    def init_game_state(self, table, prev_state):
        bidder_index = table.bidder_index
        if bidder_index == -1:
            bidder_index = table.dealer_index
            table.bid_point = -1
        bidder_index = table.next_player_index(bidder_index)
        bidding_seat = table.seats[bidder_index]
        self.send_bidding_message(table, bidding_seat, table.bid_point)

    def action(self, table, player, msg):
        bid_point = int(msg[1])
        table.seats[player.seat].turn = False
        if bid_point != -1:
            table.bid_point = bid_point
            table.bidder_index = player.seat
            table.send_everyone("chat", "{0} bid for {1}".format(player.name, bid_point))

        new_bidder_index = table.next_player_index(player.seat)
        if new_bidder_index == table.bidder_index: # any bidding this round, else play
            return self.keep_trump_state

        self.send_bidding_message(table, table.seats[new_bidder_index], table.bid_point)
        return self

    def send_bidding_message(self, table, bidder_seat, bid_point):
        log.info("Inviting {0} for bid from {1} point on table {2}".format(bidder_seat.player.name, bid_point, table.table_number))
        bidder_seat.turn = True
        bidder_seat.player.send_message("shbd{0}{1}".format(SEP, bid_point))
        table.send_everyone("chat", "Waiting for bidding from {0}".format(bidder_seat.player.name))

class KeepTrumpCard(GameState):
    def setup(self, next_states):
        self.deal_state = next_states[0]
        self.play_state = next_states[1]
        return self

    def init_game_state(self, table, prev_state):
        bidder_seat = table.seats[table.bidder_index]
        bidder_seat.turn = True
        bidder_seat.player.send_message("ktrm{0}".format(SEP))
        table.send_everyone("chat", "Waiting on {0} to keep trump card".format(bidder_seat.player.name))

    def action(self, table, player, msg):
        table.seats[player.seat].turn = False
        log.info("{0} kept trump on table {1}".format(player.name, table.table_number))
        if len(table.deck) == 0:
            return self.play_state
        else:
            return self.deal_state


class PlayCards(GameState):
    def __init__(self, cmd):
        super().__init__(cmd)
        self.cards_this_round = {}

    def setup(self, next_states):
        self.wait_start_state = next_states[0]
        return self

    def init_game_state(self, table, prev_state):
        play_index = table.player_index
        if play_index == -1:
            play_index = table.dealer_index
            self.cards_this_round = {}
        table.player_index = table.next_player_index(play_index)
        playing_seat = table.seats[table.player_index]
        self.send_play_message(table, playing_seat)

    def action(self, table, player, msg):
        card = msg[1]
        table.send_everyone("chat", "{0} played {1}".format(player.name, card))

        table.seats[player.seat].turn = False
        table.player_index = self.process_card_played(table, player, card)

        playing_seat = table.seats[table.player_index]
        self.send_play_message(table, playing_seat)
        return self

    def send_play_message(self, table, player_seat):
        log.info("Inviting {0} for play a card on table {1}".format(player_seat.player.name, table.table_number))
        player_seat.turn = True
        player_seat.player.send_message("play{0}".format(SEP))
        table.send_everyone("chat", "Waiting on {0} to play a card".format(player_seat.player.name))

    def process_card_played(self, table, player, card):
        self.cards_this_round[player.seat] = card
        player_index = table.next_player_index(player.seat)
        if len(self.cards_this_round) == len(table.seats):
            player_index = table.assign_card_to_team(self.cards_this_round)
            self.cards_this_round = {}

        return player_index