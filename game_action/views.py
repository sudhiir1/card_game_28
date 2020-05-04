from django.shortcuts import render
from threading import Event
from django.views.decorators.http import require_POST
from django.http import JsonResponse

action_event = Event()
action_event.clear()
latest_message = ''

#@require_POST
def new_chat_message(request):
    print(request.GET)
    action_event.latest_message = request.GET.get('msg')
    action_event.set()

    return JsonResponse({'status': 'success', 'test': latest_message})


def wait_for_new_message(request):
    action_event.wait(300)
    action_event.clear()
    
    return JsonResponse({'msg_type': 'chat', 'msg_text': action_event.latest_message})

