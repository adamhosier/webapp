from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import auth
from django.forms.models import model_to_dict
from . import models
from .views_broker import getBrokerById
from .util import *
from datetime import datetime
import time, feedparser


def home(request):
  if not logged_in(request): return HttpResponseRedirect('/')
  if is_broker(request): return HttpResponseRedirect('/broker')
  return render(request, 'home.html', getHomeData(request))


def chat_update(request):
  if not logged_in(request): return HttpResponseRedirect('/')
  if 'msg' not in request.POST: return HttpResponseRedirect('/home')
  if is_broker(request):
    user = models.User.objects.get(id=int(request.POST['broker']))
    broker = models.Broker.objects.get(user_id=request.session['user']['id'])
    from_broker = True
  else: 
    user = models.User.objects.get(id=request.session['user']['id'])
    broker = getBrokerById(int(request.POST['broker']))
    from_broker = False
  chat = models.Chat.objects.get(user=user, broker=broker)
  chat_obj = models.Chat_Content(chat=chat, content=request.POST['msg'], from_broker=from_broker)
  chat_obj.save()
  return JsonResponse({'isBroker':  is_broker(request)}, safe=False)

def open_chat(request, id):
  if not logged_in(request): return HttpResponseRedirect('/')
  if id not in request.session['open_chats']:
    request.session['open_chats'].append(id)
    request.session.modified = True
    user = models.User.objects.get(id=request.session['user']['id'])
    broker = getBrokerById(id)
    if not models.Chat.objects.filter(user=user, broker=broker).exists():
      entry = models.Chat(user=user, broker=broker)
      entry.save();
    data = {
      'id'       : id,
      'name'     : broker.firstname + " " + broker.lastname,
      'chat_box' : getChatBox(request, broker),
    }
    return JsonResponse(data, safe=False)
  else:
    return JsonResponse([], safe=False)
  
def stocks(request):
  if not logged_in(request): return HttpResponseRedirect('/')
  return render(request, 'stocks.html')

def update(request, lastUpdate):
  if not logged_in(request): return HttpResponseRedirect('/')
  stockdata, _ = getStockData(request)
  chatdata = getChatUpdates(request, lastUpdate)
  return JsonResponse({'stock':stockdata, 'chat':chatdata, 'broker':is_broker(request)}, safe=False)
  
