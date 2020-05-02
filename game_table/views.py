from django.shortcuts import render

def game_table(request):
    return render(request, 'game_table.html', {})

