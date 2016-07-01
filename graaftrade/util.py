from pytz import utc
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import auth
from django.forms.models import model_to_dict
from . import models
from datetime import datetime
import feedparser

NUM_BROKERS_ON_LEADERBOARD = 5
SECONDS_IN_DAY = 86400 
NEWS_STORIES = 6

def logged_in(request):
  return 'logged_in' in request.session and request.session['logged_in']

def is_broker(request):
  return request.session['user']['isBroker']

def fix_date(date):
  now = datetime.utcnow().replace(tzinfo=utc)
  d = date #datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
  s = round((now - d).total_seconds())
  if s < 120: 
    return "{}s ago".format(s)
  if s < 60 * 60:
    return "{}m ago".format(s // 60)
  if s < 60 * 60 * 24:
    return "{}h ago".format(s // (60 * 60))
  if s < 60 * 60 * 24 * 7:
    return "{}d ago".format(s // (60 * 60 * 24))
  return ">7d ago"

def getBrokerById(id):
  return models.Broker.objects.get(id=id);

def getStockData(request):
  userStocks = models.User_Stock.objects.filter(user_id=request.session['user']['id']).select_related('stock').order_by('id')
  stockdata, watchdata = [], []
  for s in userStocks:
    currentPrice = round(s.stock.price, 2)
    change = s.stock.change
    if s.watching:
      watchdata.append({
        'ticker' : s.stock.ticker,
        'price'  : currentPrice,
	'change' : change 
      })
    else:
      stockdata.append({
        'ticker' : s.stock.ticker,
        'amount' : s.amount,
        'price'  : currentPrice,
        'value'  : currentPrice * s.amount,
        'change' : change
      })
  return stockdata, watchdata

def getChatUpdates(request, lastUpdate):
  data = {}
  updated = datetime.fromtimestamp(int(lastUpdate))
  if is_broker(request): 
    chats = models.Chat.objects.filter(broker=models.Broker.objects.get(user_id=request.session['user']['id'])).select_related('user')
    for c in chats:
      newmessages = models.Chat_Content.objects.filter(chat=c, from_broker=False, timestamp__gt=updated).order_by('timestamp')
      data[c.user.id] = [msg.content for msg in newmessages]
  else:
    user = models.User.objects.get(id=request.session['user']['id'])
    for bid in request.session['open_chats']:
      broker = models.Broker.objects.get(id=bid)
      c = models.Chat.objects.get(user=user, broker=broker)
      newmessages = models.Chat_Content.objects.filter(chat=c, from_broker=True, timestamp__gt=updated).order_by('timestamp')
      data[bid] = [msg.content for msg in newmessages]
  return data

def getUserBrokerData(request):
  brokers = models.Broker.objects.all().order_by('-performance')[:NUM_BROKERS_ON_LEADERBOARD]
  data = []
  for b in brokers:
    data.append({
      'id'          : b.id,
      'name'        : b.firstname + " " + b.lastname,
      'fee'         : b.fee,
      'performance' : b.performance,
    })
  return data

def getChatBox(request, partner):
  return render_to_string('chat_box.html', {
    'id'    : partner.id,
    'data'  : getChat(request, partner),
  })

def getChat(request, partner):
  if is_broker(request):
    user = partner
    broker = models.Broker.objects.get(user_id=request.session['user']['id'])
  else:
    user = models.User.objects.get(id=request.session['user']['id'])
    broker = partner
  c = models.Chat.objects.get(user=user, broker=broker)
  data = models.Chat_Content.objects.filter(chat=c).order_by('timestamp').values()
  for d in data:
    d['from_partner'] = is_broker(request) != d['from_broker']
  return data

def getHomeData(request):
  # stock page data
  stockdata, watchdata = getStockData(request)
  totalvalue = 0;
  totalchange = 0;
  for d in stockdata:
    totalvalue += d['value']
    totalchange += d['change'] * d['amount']
  
  # news data
  rssfeed = 'http://feeds.skynews.com/feeds/rss/business.xml'
  news = feedparser.parse(rssfeed)
   
  request.session.modify = True
  request.session['news'] = news['entries']

  # chat data
  openChats = []
  if is_broker(request):
    chats = models.Chat.objects.filter(broker=models.Broker.objects.get(user_id=request.session['user']['id'])).select_related('user')
    for c in chats:
      openChats.append({
	'id'       : c.user.id,
	'name'     : c.user.username,
	'chat_box' : getChatBox(request, c.user),
      })
  else:
    for id in request.session['open_chats']:
      broker = getBrokerById(id) 
      openChats.append({
        'id'       : id,
        'name'     : broker.firstname + " " + broker.lastname,
        'chat_box' : getChatBox(request, broker),
      })
  
  # broker data
  brokerdata = getUserBrokerData(request)

  # news
  news = models.News.objects.all().order_by('-published')[:NEWS_STORIES]
  newsdata = [{'image':n.image, 'link':n.link, 'title':n.title, 'summary':n.summary, 'published':fix_date(n.published)} for n in news]

  return {
    'username'             : request.session['user']['username'],
    'user_stock_list'      : stockdata,
    'total_value'          : totalvalue,
    'total_change'         : totalchange,
    'total_change_percent' : 0 if totalvalue == 0 else (totalchange / totalvalue * 100),
    'broker_list'          : brokerdata,
    'user_watch_list'      : watchdata,
    'open_chats'           : openChats,
    'news'                 : newsdata
  }
