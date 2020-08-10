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
        self.game_state = self.game_states[PLAYER_READY]
        self.game_state.init_game_state(self.table, None)

        self.game_events = self.setup_game_events()

    def setup_game_states(self):
        wait_for_full_table = WaitForFullTable()
        wait_for_game_start = WaitForGameStart()
        deal_cards = DealCards()
        bid_points = BidPoints()
        keep_trump = KeepTrumpCard()
        play_cards = PlayCards()

        game_states = {
            PLAYER_READY    : wait_for_full_table,
            START_GAME      : wait_for_game_start,
            DEAL_CARDS      : deal_cards,
            BID_POINTS      : bid_points,
            KEEP_TRUMP      : keep_trump,
            PLAY_CARD       : play_cards,
            SHOW_TRUMP      : play_cards,  
        }
        return game_states

    def setup_game_events(self):
        process_player_join = ProcessPlayerJoin()
        process_player_exit = ProcessPlayerExit()
        process_trump_request = ProcessTrumpRequest()

        game_events = {
            "newp": process_player_join.setup(self.game_states[PLAYER_READY]),
            "byep": process_player_exit.setup(self.game_states[PLAYER_READY]),
            SHOW_TRUMP: process_trump_request.setup()
        }
        return game_events

    def process_message(self, player, msg):
        log.info("New message in Table {0} from {1}: {2}".format(self.table.table_number, player.name, msg))
        msg_arr = msg.split(SEP)
        cmd = msg_arr[0]

        process_state = self.process_event(player, msg_arr)
        if not process_state:
            return

        if self.game_states.get(cmd) is None:
            log.warn("Unknown command: {0}  from {1} in Table {2}".format(msg, player.name, self.table.table_number))
            return

        if not self.table.seats[player.seat].turn:
            log.warn("Ignoring {0} command from {1} at Table {2} as it is not this players turn".format(msg, player.name, self.table.table_number))
            return

        if self.game_state.expected_command(cmd):
            return self.play_next(player, msg_arr)

        log.warn("Unexpected message in Table {0} from {1}. Message: {2}. State:{3}".format(self.table.table_number, player.name, msg, self.game_state.__class__.__name__))

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
        next_state_cmd = self.game_state.action(self.table, player, msg)
        if next_state_cmd is None:
            return # continuing on same state
        if self.game_states.get(next_state_cmd) is None:
            log.warn("Unknown command: {0} from game state. Player is {1} in Table {2}".format(next_state_cmd, player.name, self.table.table_number))
            return

        next_game_state = self.game_states[next_state_cmd]

        log.info("Changing state to {0}".format(next_state_cmd))
        next_game_state.init_game_state(self.table, self.game_state)
        self.game_state = next_game_state

