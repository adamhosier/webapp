#!/usr/bin/env python3

import psycopg2, json, time, sched
from urllib import request
from datetime import datetime

DB_UPDATE_TIME = 1
FILE_UPDATE_TIME = 60
BASE_URL = "http://finance.yahoo.com/webservice/v1/symbols/{}/quote?format=json&view=detail"
CSV_URL = "graaftrade/assets/data/{}.csv"
conn = psycopg2.connect("dbname=graaftrade user=dan host=localhost password=password") 
cursor = conn.cursor()
s = sched.scheduler(time.time, time.sleep)
minprices = {}
maxprices = {}
stockdata = {}

# gets a list of tickers in the database
def get_stocks():
  cursor.execute("SELECT ticker FROM graaftrade_stock ORDER BY id")
  return [x[0] for x in cursor.fetchall()]

# converts list to comma separated string [1, 2, 3] => "1,2,3"
def list_to_string(l):
  return ",".join(l)

# gets the data for all the stocks in a single request
def get_stock_data():
  try:
    data = request.urlopen(BASE_URL.format(list_to_string(stocks)))
  except Exception:
    return get_stock_data()
  return json.loads(data.read().decode('utf-8'))['list']['resources']

# get the update query for a single stock
def get_update_query(data):
  r = data['resource']['fields']
  return "UPDATE graaftrade_stock SET price = {}, change = {} WHERE ticker = '{}';".format(r['price'], r['change'], r['symbol'])

# get the update queries for all the stock
def get_update_queries(data):
  return ''.join([get_update_query(d) for d in data])

# commit queries
def exec_queries(qs):
  cursor.execute(qs)
  conn.commit()

# init minprces and maxprices
def init_prices():
  for st in stocks:
    minprices[st] = 1 << 32
    maxprices[st] = 0
    stockdata[st] = []

# update price arrays
def update_prices(data):
  for i in range(len(stocks)):
    st = stocks[i]
    r = data[i]['resource']['fields']
    price = float(r['price'])
    minprices[st] = price if price < minprices[st] else minprices[st] 
    maxprices[st] = price if price > maxprices[st] else maxprices[st] 
    stockdata[st].append(r)
    
def reset_files():
  for st in stocks:
    with open(CSV_URL.format(st), 'w') as f:
      f.write('Date,Open,High,Low,Close,Volume\n')

# update database every second
def query_loop():
  # call the function again after a delay
  s.enter(DB_UPDATE_TIME, 1, query_loop)

  data = get_stock_data()
  update_prices(data)
  exec_queries(get_update_queries(data))


# write to files every minute
def file_loop():
  s.enter(FILE_UPDATE_TIME, 1, file_loop)
  for st in stocks:
    r = stockdata[st]
    with open(CSV_URL.format(st), 'a') as f:
      f.write("{},{},{},{},{},{}\n".format(
        time.strftime("%Y-%m-%d %H:%M"),  #date
        r[0]['price'],                    #open
        maxprices[st],                    #high
        minprices[st],                    #low
        r[-1]['price'],                   #close
        r[0]['volume']                    #volume
      ))
  
  # reset min/max prices and loop
  init_prices()

stocks = get_stocks()
init_prices()
#reset_files()

#start loop
query_loop()
file_loop()
s.run()
