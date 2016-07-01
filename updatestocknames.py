#!/usr/bin/env python3

import psycopg2, json, time, sched
from urllib import request
from datetime import datetime

BASE_URL = "http://finance.yahoo.com/webservice/v1/symbols/{}/quote?format=json&view=detail"
conn = psycopg2.connect("dbname=graaftrade user=dan host=localhost password=password") 
cursor = conn.cursor()

# gets a list of tickers in the database
def get_stocks():
  cursor.execute("SELECT ticker FROM graaftrade_stock ORDER BY id")
  return [x[0] for x in cursor.fetchall()]

# converts list to comma separated string [1, 2, 3] => "1,2,3"
def list_to_string(l):
  return ",".join(l)

# gets the data for all the stocks in a single request
def get_stock_data():
  return json.loads(request.urlopen(BASE_URL.format(list_to_string(stocks))).read().decode('utf-8'))['list']['resources']

# get the update query for a single stock
def get_update_query(data):
  r = data['resource']['fields']
  return "UPDATE graaftrade_stock SET name = '{}' WHERE ticker = '{}';".format(r['name'].replace("'", "''"), r['symbol'])

# get the update queries for all the stock
def get_update_queries(data):
  return ''.join([get_update_query(d) for d in data])

# commit queries
def exec_queries(qs):
  cursor.execute(qs)
  conn.commit()

stocks = get_stocks()
exec_queries(get_update_queries(get_stock_data()))
