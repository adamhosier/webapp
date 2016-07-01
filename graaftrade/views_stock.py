from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.forms.models import model_to_dict
from django.db.models import Q
from .util import *
from . import models

def ticker_exists(ticker):
  return models.Stock.objects.get(ticker=ticker) != None

def get_user_stock(request, ticker):
  return models.User_Stock.objects.filter(stock=models.Stock.objects.get(ticker=ticker),user=models.User.objects.get(id=request.session['user']['id']))

def user_has_ticker(request, ticker):
  return ticker_exists(ticker) and len(get_user_stock(request, ticker)) != 0

def add_user_stock(request, ticker, amount, watching):
  stock = models.User_Stock(stock=models.Stock.objects.get(ticker=ticker),user=models.User.objects.get(id=request.session['user']['id']), amount=amount, watching=watching);
  stock.save()
    
def main(request, ticker):
  if not logged_in(request): return HttpResponseRedirect('/')
  return render(request, 'stock.html', {'ticker':ticker, 'stock_news': get_stock_news(ticker)}) 

def remove(request, ticker):
  if not logged_in(request): return HttpResponseRedirect('/')
  user_stock = get_user_stock(request, ticker)
  #check if the user has that particular stock.
  if user_stock != None:
    user_stock.delete()
  #remove that stock for that user.
  return HttpResponseRedirect('/home');

def search(request, s):
  if not logged_in(request): return HttpResponseRedirect('/')
  data = models.Stock.objects.filter(Q(ticker__istartswith=s) | Q(name__istartswith=s))[:5]
  results = [{'ticker':d.ticker, 'name':d.name} for d in data]
  return JsonResponse(results, safe=False)

def add(request, ticker):
  if not logged_in(request): return HttpResponseRedirect('/')
  if not user_has_ticker(request, ticker):
    #Add a single stock to the users list of stocks.
    add_user_stock(request, ticker, 1, 0)
  return HttpResponseRedirect('/home?added=' + ticker)

def update(request, ticker, value):
  if not logged_in(request): return HttpResponseRedirect('/')
  if user_has_ticker:
    stock = get_user_stock(request, ticker).first()
    stock.amount = value
    stock.save()
  return HttpResponseRedirect('/home')
  
def watch(request, ticker):
  if not logged_in(request): return HttpResponseRedirect('/')
  if not user_has_ticker(request, ticker):
    add_user_stock(request, ticker, 0, 1) 
  return HttpResponseRedirect('/home')

def move(request, ticker):
  if not logged_in(request): return HttpResponseRedirect('/')
  if user_has_ticker:
    stock = get_user_stock(request, ticker).first()
    stock.watching = 0
    stock.amount = 1
    stock.save()
  return HttpResponseRedirect('/home?added=' + ticker)

def move_watch(request, ticker):
  if not logged_in(request): return HttpResponseRedirect('/')
  if user_has_ticker:
    stock = get_user_stock(request, ticker).first()
    stock.watching = 1
    stock.amount = 0
    stock.save()
  return HttpResponseRedirect('/home')
  
  
def remove_watch(request, ticker):
  if not logged_in(request): return HttpResponseRedirect('/')
  if user_has_ticker:
    stock = get_user_stock(request, ticker).first()
    stock.watching = 0
    stock.delete()
  return HttpResponseRedirect('/home')

def compare(request, ticker1, ticker2):
  if not logged_in(request): return HttpResponseRedirect('/')  
  return render(request, 'compare.html', {'ticker1': ticker1, 'ticker2': ticker2})

def get_stock_news(ticker):
  news = models.Stock_News.objects.filter(stock=models.Stock.objects.get(ticker=ticker)).order_by('-published')[:12]
  newsdata = [{'link':n.link, 'title':n.title, 'published':fix_date(n.published)} for n in news]
  return newsdata
