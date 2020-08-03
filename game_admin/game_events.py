import logging

from game_admin.common import *

from game_admin.game_player import GamePlayer, PlayerStatus

log = logging.getLogger(__name__)

class ProcessPlayerJoin():
    def setup(self, next_state):
        self.wait_full_table = next_state
        return self

    def action(self, table, player, msg, game_state):
        is_new = msg[1]
        log.info("Adding player to seat {} of the table_{}. Welcome {}".format(player.seat, table.table_number, player.name))
        table.send_everyone("newp", "{0}{1}{2}{3}{4}".format(player.name, SEP, player.status.value, SEP, player.seat))
        table.send_current_players_info(player)
        
        if is_new:
            return None, False

        return game_state, False

class ProcessPlayerExit():
    def setup(self, next_state):
        self.wait_full_table = next_state
        return self

    def action(self, table, player, msg, game_state):
        player_status = player.status
        log.info("Processing {0}'s exit from Table {1}".format(player.name, table.table_number))
        
        table.say_goodbye(player)
        if player_status == PlayerStatus.Active:
            log.info("Waiting for new player to take {0}'s place at Table {1}".format(player.name, table.table_number))
            return self.wait_full_table, False
        return None, True

class ProcessTrumpRequest():
    def setup(self):
        return self

    def action(self, table, player, msg, game_state):
        player_status = player.status
        log.info("Processing trump request from {0} at Table {1}".format(player.name, table.table_number))

        if not game_state.expected_command(SHOW_TRUMP) :
            log.warn("Current state is not expecting showing trump card request. Requested by {0} at table {1}".format(player.name, table.table_number))
            return None, False

        table.send_everyone("tmis", "{0}{1}{2}".format(table.trump.card, SEP, table.trump.seat))
        table.trump.shown = True
        return None, False

