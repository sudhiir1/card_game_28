import logging
import random

from game_admin.common import *

from game_admin.game_player import GamePlayer, PlayerStatus

log = logging.getLogger(__name__)

class GameController:

    def __init__(self, table):
        self.table = table

        self.game_states = self.setup_game_states()
        self.game_state = self.game_states["redy"]

        self.game_commands = self.setup_game_commands()

    def setup_game_states(self):
        wait_for_full_table = WaitForFullTable()
        wait_for_all_say_start = WaitForAllSayStart()

        game_states = {
            "redy": wait_for_full_table.setup(wait_for_all_say_start), # | showStatuspopu
            # "strt": WaitForAllSayStart(), # | deal, send bid ready(1 player)
            # "deal": ProcessDealing(), # send bid popup, get bid, send bid ready(next player) | ask trump
            # "trmp": WaitForTrumpDown(), # identify trumper | deal, send bid ready (bidder+next) / send round start (dealer+next)
            # "plyd": WaitForCardPlay(), # record card, send next player / calc high card, assign to team | show status popup
        }
        return game_states

    def setup_game_commands(self):
        game_commands = {
            "byep": ProcessPlayerExit().setup(self.game_states["redy"]),
        }
        return game_commands

    def process_message(self, player, msg):
        log.info("New message from {0}-{1}: {2}".format(self.table.table_number, player.name, msg))
        msg_arr = msg.split(SEP)

        self.play_next(player, msg_arr)

    def play_next(self, player, msg):
        cmd = msg[0]
        next_game_state = self.game_state.action(self.table, player, msg)

        if next_game_state is self.game_state:
            return

        next_game_state.init_game_state(self.table, self.game_state)
        self.game_state = next_game_state

class GameState:
    def __init__(self):
        pass

    def setup(self, next_state):
        return self

    def init_game_state(self, table, prev_state):
        pass

    def action(self, table, player, msg):
        return None

class WaitForFullTable(GameState):
    def __init__(self):
        super().__init__()

    def setup(self, next_state):
        self.wait_start_state = next_state
        return self

    def action(self, table, player, msg):
        for seat in reversed(table.seats):
            if seat is None:
                log.info("Waiting for full table at Table {0}".format(table.table_number))
                return self

        return self.wait_start_state

class WaitForAllSayStart(GameState):

    def init_game_state(self, table, prev_state):
        log.debug("Sending every one to open status popup..")
        table.send_everyone("stat", "")
        
    def action(self, table, player, msg):
        player.turn = False
        for seat in table.seats:
            if seat is None or seat.turn:
                log.info("Waiting for others to say start")
                return self
        return self

class ProcessPlayerExit():
    def setup(self, next_state):
        self.wait_full_table = next_state

    def action(self, table, player, msg):
        pass


def deal_cards(table):
    # send each player cards: dealer_index+1: 4/3 cards
    
    #seats[dealer_index+1].turn = True
    return wait_for_bidding_request


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
