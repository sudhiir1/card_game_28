from enum import Enum 

server_name = "card_28"
SEP = ":"
NO_SEAT = 0

class GameStatus(Enum):
    GameWaiting = 0
    GameStarted = 1
    RoundStarted = 2
    RoundEnded = 3
