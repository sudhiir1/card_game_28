from enum import Enum 

server_name = "card_28"
SEP = ":"
NO_SEAT = 0

class GameStatus(Enum):
    GameWaiting = 0
    GameStarted = 1
    RoundStarted = 2
    RoundEnded = 3

PLAYER_READY = "redy"
START_GAME   = "strt"
DEAL_CARDS   = "delt"
BID_POINTS   = "bdpt"
KEEP_TRUMP   = "trmd"
PLAY_CARD    = "card"
SHOW_TRUMP   = "shtm"
