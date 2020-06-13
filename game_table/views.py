from django.shortcuts import render

def host_game(request):
    return render(request, 'host_game.html', {})

def game_link(request):
    return render(request, 'game_link.html', {})

def player_login(request):
    table_no =  request.GET.get("table", "")
    if table_no == "":
        return host_game(request) # Todo: no table, please host

    return render(request, 'player_login.html', {"table_number": table_no}) 

def game_table(request):
    if request.method == 'POST':
        table_no =  request.POST.get("table_number", "")
        player_name =  request.POST.get("player_name", "")

        return render(request, 'game_table.html', {"table_number": table_no, "player_name": player_name})
    else:
        return player_login(request)

