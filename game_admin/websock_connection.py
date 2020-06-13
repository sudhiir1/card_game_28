import logging
import asyncio

clients = {}
client_id = 0

log = logging.getLogger(__name__)

server_name = "card_28"

async def websocket_application(scope, receive, send):
    global clients
    global client_id
    my_id = 0
    while True:
        event = await receive()

        if event['type'] == 'websocket.connect':
            player = accept_new_connection(scope["query_string"], send)
            if player is None:
                break

        elif event['type'] == 'websocket.disconnect':
            player.table.say_goodbye(player)
            break

        elif event['type'] == 'websocket.receive':
            player.table.send_everyone(player.name, event['text'])

def accept_new_connection(query_string, player_conn):
    player_info_list = query_string.decode().replace('&', '=').split('=')
    if len(player_info_list) <  4:
        log.warn("Invalid connection query received. Ignoring player acceptance. Query:{}".format(query_string))
        return
    player_info_dict = {player_info_list[i]: player_info_list[i + 1] for i in range(0, len(player_info_list), 2)} 

    if "player" not in player_info_dict or "table" not in player_info_dict:
        log.warn("Unknown connection query received. Ignoring player acceptance. Query:{}".format(query_string))
    else:
        return GameTable.accept_player(player_info_dict["table"], player_info_dict["player"], player_conn)

    return None

class GameTable:
    log = logging.getLogger(__name__)

    tables = {}

    def __init__(self, table_number):
        self.table_number = table_number
        self.player_count = 0
        self.players = {}

    def add_player(self, player_name, player_conn):
        player = self.search_player_by_name(player_name)
        if player is None:
            log.info("Adding new player to the table_{}. Welcome {}".format(self.table_number, player_name))
            self.player_count += 1
            player = GamePlayer(self.player_count, player_name, player_conn, self)
            self.players[self.player_count] = player
        else:
            log.warn("Looks like {} has been playing in table_{}".format(player_name, self.table_number))

        log.info("Accepting {} to table_{}".format(player_name, self.table_number))
        player.accept_connection()

        player.table.send_everyone(server_name, "{} joined".format(player.name))

        return player

    def search_player_by_name(self, player_name):
        for _, player in self.players.items():
            if player.name == player_name:
                return player
        return None

    def say_goodbye(self, leaving_player):
        send_everyone_except(leaving_player, server_name, "{} left the table".format(leaving_player.name))

        self.players.pop(leaving_player.id)

    def send_everyone(self, source_name, msg):
        for id, player in self.players.items():
            player.send_message("{}: {}".format(source_name, msg))
        log.info("Send everyone: {}: {}".format(source_name, msg))

    def send_everyone_except(self, this_player, source_name, msg):
        for id, player in self.players.items():
            if not player is this_player:
                player.send_message("{}: {}".format(source_name, msg))
        log.info("Send except {}: {}: {}".format(this_player.name, source_name, msg))

    @classmethod
    def accept_player(cls, table_number, player_name, player_conn):
        if table_number not in cls.tables:
            log.info("Setting up new table, number is {}".format(table_number))
            cls.tables[table_number] = GameTable(table_number)
        
        table = cls.tables[table_number]
        return table.add_player(player_name, player_conn)
    
class GamePlayer:
    log = logging.getLogger(__name__)

    def __init__(self, id, name, send_conn, table):
        self.id = id
        self.name = name
        self.send_conn = send_conn
        self.table = table

    def accept_connection(self):
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.send_conn({'type': 'websocket.accept'}))
        self.send_message("{}:your_id:{}".format(server_name, self.id))
        
    def send_message(self, msg):
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.send_conn({'type': 'websocket.send', 'text': msg}))

