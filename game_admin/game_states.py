import logging
import random

from game_admin.common import *

from game_admin.game_player import GamePlayer, PlayerStatus

log = logging.getLogger(__name__)

class GameState:
    def __init__(self, expected_cmds):
        self.expected_cmds = expected_cmds

    def expected_command(self, cmd):
        if cmd in self.expected_cmds:
            return True
        return False

    def init_game_state(self, table, prev_state):
        pass

    def action(self, table, player, msg):
        return None

class WaitForFullTable(GameState):
    def __init__(self):
        super().__init__([PLAYER_READY])

    def init_game_state(self, table, prev_state):
        log.info("Getting ready to accept players")
        table.set_everyones_turn(True)

    def action(self, table, player, msg):
        table.seats[player.seat].turn = False
        for seat in reversed(table.seats):
            if seat.player is None:
                log.info("Waiting for full table at Table {0}".format(table.table_number))
                return

        return START_GAME

class WaitForGameStart(GameState):
    def __init__(self):
        super().__init__([START_GAME])

    def init_game_state(self, table, prev_state):
        log.info("Sending every one to open status popup..")
        table.set_everyones_turn(True)
        table.send_everyone("stat", "")
        
    def action(self, table, player, msg):
        table.seats[player.seat].turn = False
        for seat in table.seats:
            if seat.player is None or seat.turn:
                log.info("Waiting for others to say start")
                return

        self.prep_for_new_game(table)
        return DEAL_CARDS

    def prep_for_new_game(self, table):
        random.shuffle(table.deck)
        table.dealer_index = random.randrange(table.num_seats)
        table.bidder_index = -1
        table.player_index = -1
        table.evenTeamCards = []
        table.oddTeamCards = []
        table.trump.reset()

class DealCards(GameState):
    def __init__(self):
        super().__init__([DEAL_CARDS])

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
                return
        return BID_POINTS

class BidPoints(GameState):
    def __init__(self):
        super().__init__([BID_POINTS])

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
            return KEEP_TRUMP

        self.send_bidding_message(table, table.seats[new_bidder_index], table.bid_point)
        return

    def send_bidding_message(self, table, bidder_seat, bid_point):
        log.info("Inviting {0} for bid from {1} point on table {2}".format(bidder_seat.player.name, bid_point, table.table_number))
        bidder_seat.turn = True
        bidder_seat.player.send_message("shbd{0}{1}".format(SEP, bid_point))
        table.send_everyone("chat", "Waiting for bidding from {0}".format(bidder_seat.player.name))

class KeepTrumpCard(GameState):
    def __init__(self):
        super().__init__([KEEP_TRUMP])

    def init_game_state(self, table, prev_state):
        bidder_seat = table.seats[table.bidder_index]
        bidder_seat.turn = True
        bidder_seat.player.send_message("ktrm{0}".format(SEP))
        table.send_everyone("chat", "Waiting on {0} to keep trump card".format(bidder_seat.player.name))

    def action(self, table, player, msg):
        table.seats[player.seat].turn = False
        log.info("{0} kept trump on table {1}".format(player.name, table.table_number))
        if len(table.deck) == 0:
            return PLAY_CARD
        else:
            return DEAL_CARDS


class PlayCards(GameState):
    card_value_priority = "J,9,A,1,K,Q,8,7,6".split(",")

    def __init__(self):
        super().__init__([PLAY_CARD, SHOW_TRUMP])
        self.cards_this_round = {}

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
        return

    def send_play_message(self, table, player_seat):
        log.info("Inviting {0} for play a card on table {1}".format(player_seat.player.name, table.table_number))
        player_seat.turn = True
        player_seat.player.send_message("play{0}".format(SEP))
        table.send_everyone("chat", "Waiting on {0} to play a card".format(player_seat.player.name))

    def process_card_played(self, table, player, card):
        self.cards_this_round[player.seat] = card
        player_index = table.next_player_index(player.seat)
        if len(self.cards_this_round) == len(table.seats):
            player_index = self.assign_cards_to_team(table, self.cards_this_round)
            self.cards_this_round = {}

        return player_index

    def assign_cards_to_team(self, table, cards_played):
        cards_to_consider = self.cards_to_consider(table, cards_played)
        winner_index = self.high_card_player(table, cards_to_consider)
        if winner_index % 2 == 0:
            table.evenTeamCards.extend(list(cards_played.values()))
        else:
            table.oddTeamCards.extend(list(cards_played.values()))

        log.info("EVEN TEAM:{}".format(",".join(table.evenTeamCards)))
        log.info("ODD TEAM:{}".format(",".join(table.oddTeamCards)))
        return winner_index

    def cards_to_consider(self, table, cards_played):
        trump_cards = {}
        same_type_cards = {}
        first_card = cards_played[next(iter(cards_played))]

        for seat_index, card in cards_played.items():
            log.info("{0} played {1}".format(table.seats[seat_index].player.name, card))
            if table.trump.shown and table.trump.card[0] == card[0]:
                trump_cards[seat_index] = card
            if first_card[0] == card[0]:
                same_type_cards[seat_index] = card
        if len(trump_cards) > 0:
            return trump_cards
        return same_type_cards

    def high_card_player(self, table, cards_to_consider):
        for card_value in PlayCards.card_value_priority:
            for seat_index, card in cards_to_consider.items():
                if card_value == card[1]:
                    log.info("This round goes to {0}: {1}".format(table.seats[seat_index].player.name, card))
                    return seat_index
        log.info("No high card, something wrong. {0}: {1}".format(table.seats[seat_index].player.name, table.table_number))
        return -1