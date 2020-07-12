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
        wait_for_full_table = WaitForFullTable("redy")
        wait_for_all_say_start = WaitForAllSayStart("strt")
        deal_cards = DealCardsToAll("deal")

        game_states = {
            "redy": wait_for_full_table.setup(wait_for_all_say_start), # | showStatuspopu
            "strt": wait_for_all_say_start.setup(deal_cards), # | deal, send bid ready(1 player)
            "deal": deal_cards.setup(deal_cards), # send bid popup, get bid, send bid ready(next player) | ask trump
            # "trmp": WaitForTrumpDown(), # identify trumper | deal, send bid ready (bidder+next) / send round start (dealer+next)
            # "plyd": WaitForCardPlay(), # record card, send next player / calc high card, assign to team | show status popup
        }
        return game_states

    def setup_game_commands(self):
        process_player_exit = ProcessPlayerExit()
        game_commands = {
            "byep": process_player_exit.setup(self.game_states["redy"]),
        }
        return game_commands

    def process_message(self, player, msg):
        log.info("New message in Table {0} from {1}: {2}".format(self.table.table_number, player.name, msg))
        msg_arr = msg.split(SEP)
        cmd = msg_arr[0]

        if self.game_commands.get(cmd) is not None:
            game_command = self.game_commands[cmd]
            return game_command.action(self.table, player, msg)

        if self.game_states.get(cmd) is not None:
            if cmd == self.game_state.cmd:
                return self.play_next(player, msg_arr)

        log.warn("Unexpected message in Table {0} from {1}. Message: {2}. Expected:{3}".format(self.table.table_number, player.name, msg, self.game_state.cmd))

    def play_next(self, player, msg):
        cmd = msg[0]
        next_game_state = self.game_state.action(self.table, player, msg)

        if next_game_state is self.game_state:
            return

        next_game_state.init_game_state(self.table, self.game_state)
        self.game_state = next_game_state

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

class WaitForAllSayStart(GameState):

    def setup(self, next_state):
        self.deal_card_state = next_state
        return self

    def init_game_state(self, table, prev_state):
        log.debug("Sending every one to open status popup..")
        table.send_everyone("stat", "")
        
    def action(self, table, player, msg):
        player.turn = False
        for seat in table.seats:
            if seat is None or seat.turn:
                log.info("Waiting for others to say start")
                return self
        return self.deal_card_state

class ProcessPlayerExit():
    def setup(self, next_state):
        self.wait_full_table = next_state

        return self

    def action(self, table, player, msg):
        log.info("Processing {0} exit from Table {1}".format(player, table.table_number))
        if player.status == PlayerStatus.Active:
            return self.wait_full_table

class DealCardsToAll(GameState):
    # send each player cards: dealer_index+1: 4/3 cards
    
    #seats[dealer_index+1].turn = True
    # return wait_for_bidding_request
    def setup(self, next_state):
        self.wait_for_bidding_request = next_state

    def action(self, table, player, msg):
        pass


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
