import logging
import random

from game_admin.common import *

from game_admin.game_player import GamePlayer, PlayerStatus
from game_admin.game_events import *
from game_admin.game_states import *

log = logging.getLogger(__name__)

class GameController:

    def __init__(self, table):
        self.table = table

        self.game_states = self.setup_game_states()
        self.game_state = self.game_states["redy"]

        self.game_events = self.setup_game_events()

    def setup_game_states(self):
        wait_for_full_table = WaitForFullTable("redy")
        wait_for_game_start = WaitForGameStart("strt")
        deal_cards = DealCards("delt")
        bid_points = BidPoints("bdpt")
        keep_trump = KeepTrumpCard("trmd")
        play_cards = PlayCards("card")

        game_states = {
            "redy": wait_for_full_table.setup([wait_for_game_start]),
            "strt": wait_for_game_start.setup([deal_cards]),
            "delt": deal_cards.setup([bid_points]),
            "bdpt": bid_points.setup([keep_trump]),
            "trmd": keep_trump.setup([deal_cards, play_cards]),
            "card": play_cards.setup([wait_for_game_start])
            # "trmp": WaitForTrumpDown(), # identify trumper | deal, send bid ready (bidder+next) / send round start (dealer+next)
            # "plyd": WaitForCardPlay(), # record card, send next player / calc high card, assign to team | show status popup
        }
        return game_states

    def setup_game_events(self):
        process_player_join = ProcessPlayerJoin()
        process_player_exit = ProcessPlayerExit()
        game_events = {
            "newp": process_player_join.setup(self.game_states["redy"]),
            "byep": process_player_exit.setup(self.game_states["redy"]),
        }
        return game_events

    def process_message(self, player, msg):
        log.info("New message in Table {0} from {1}: {2}".format(self.table.table_number, player.name, msg))
        msg_arr = msg.split(SEP)
        cmd = msg_arr[0]

        process_state = self.process_event(player, msg_arr)
        if not process_state:
            return

        if self.game_states.get(cmd) is not None:
            if cmd == self.game_state.cmd:
                return self.play_next(player, msg_arr)

        log.warn("Unexpected message in Table {0} from {1}. Message: {2}. Expected:{3}".format(self.table.table_number, player.name, msg, self.game_state.cmd))

    def process_event(self, player, msg):
        cmd = msg[0]
        if self.game_events.get(cmd) is None:
            return True

        game_event = self.game_events[cmd]
        game_state, process_state = game_event.action(self.table, player, msg, self.game_state)
        if game_state is not None:
            self.game_state = game_state
        
        return process_state

    def play_next(self, player, msg):
        cmd = msg[0]
        next_game_state = self.game_state.action(self.table, player, msg)

        if next_game_state is self.game_state:
            return

        next_game_state.init_game_state(self.table, self.game_state)
        self.game_state = next_game_state


def wait_for_bidding_request(table, player, msg):
    #show_bid popup (first bidder)

    return wait_for_bidding_amount


def wait_for_bidding_amount(table, player, msg):
    # broadcast bid amount
    # if bidders != player next player
        #return wait_for_bidding_amount(table, player+next player)

    # ask_to_keep_trump_card, bidder
    return wait_for_trump_card


def wait_for_trump_card(table, player, msg):
    # if any more card to deal
        # return deal_cards
    
    # ask play_hand: dealer+next player
    return ask_for_play_hand(table.round_starter)


def ask_for_play_hand(player):
    #send message

    return wait_for_play_hand


def wait_for_play_hand(table, player, msg):
    #if player.nextplayer != table.seats[table.round_starter]
        #return ask_for_play_hand

    return assign_cards_to_high_hand()


def assign_cards_to_high_hand():
    # find high hand and assign to team
    #if any more card to play
        # ask play_hand: high hand player
        # return ask_for_play_hand(table.round_starter)

    return show_game_status_popup()


def assign_players_to_team(table):
    log.info("Let us make team")
    return wait_for_players_say_start
