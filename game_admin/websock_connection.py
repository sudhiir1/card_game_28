import logging
import asyncio
from game_admin.table_admin import TableAdmin

log = logging.getLogger(__name__)

async def websocket_application(scope, receive, send):
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
            player.table.process_new_message(player, event['text'])

def accept_new_connection(query_string, player_conn):
    player_info_list = query_string.decode().replace('&', '=').split('=')
    if len(player_info_list) <  4:
        log.warn("Invalid connection query received. Ignoring player acceptance. Query:{}".format(query_string))
        return
    player_info_dict = {player_info_list[i]: player_info_list[i + 1] for i in range(0, len(player_info_list), 2)} 

    if "player" not in player_info_dict or "table" not in player_info_dict:
        log.warn("Unknown connection query received. Ignoring player acceptance. Query:{}".format(query_string))
    else:
        return TableAdmin.accept_player(player_info_dict["table"], player_info_dict["player"], player_conn)

    return None

