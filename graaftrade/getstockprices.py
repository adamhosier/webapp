from yahoo_finance import Share
from datetime import datetime
from django.db import transaction
import sched
import time
import json
import threading
import psycopg2
import csv
import atexit
import sys

SATURDAY = 5
SECS_MIN = 60
conn = psycopg2.connect("dbname=graaftrade user=dan host=localhost password=password") 
cursor = conn.cursor()
minprices = {}
maxprices = {}
data = {}
s = sched.scheduler(time.time, time.sleep)

def set_interval(func, sec, stocks, csvs):
  s.enter(1, 1, func, argument=(stocks, csvs)) 
  s.run()
  set_interval(func, sec, stocks, csvs)
  
  #def func_wrapper():
  #      set_interval(func, sec, stocks, csvs)
  #      func(stocks, csvs)
  #t = threading.Timer(sec, func_wrapper)
  #t.start()
  #return t

def exec_query(stock, currprice, openprice):
  query = "UPDATE graaftrade_stock SET price = " + str(currprice) + ", opening = " + str(openprice) + " where ticker = '" + stock + "'"
  try:
    if stock == 'BA.L':
      print(currprice)
    cursor.execute(query)
    conn.commit()
  except psycopg2.DataError:
    print(query)
    conn.rollback()

def get_time_past_min():
  now = datetime.now()
  midnight = now.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
  return (now - midnight).seconds

def loop(stocks, csvs):  
  day = datetime.now().weekday()
  _, fs = open_files(stocks, 'a')
  if(day < SATURDAY):
    i = 0
    was = False
    for stock in stocks:
      share = Share(stock)
      curr_price = float(share.get_price())
      if (get_time_past_min() % SECS_MIN == 0 or was):
        data[stock].append([datetime.now().strftime("%Y-%m-%d %H:%M"), curr_price, 0, 0, 0, 0])
        was = True
        if (len(data[stock]) > 1):
          if stock == 'BA.L':
            print(data[stock][-1])
            print(data[stock][-2])
            data[stock][-2][2] = maxprices[stock]
            data[stock][-2][3] = minprices[stock]
            data[stock][-2][4] = curr_price
            data[stock][-2][5] = share.get_volume() #might need to be change in vol
            minprices[stock] = float(curr_price)
            maxprices[stock] = float(curr_price)
            fs[i].write(str(data[stock][-2][0]) + "," + str(data[stock][-2][1]) + "," + str(data[stock][-2][2]) + "," + str(data[stock][-2][3]) + "," + str(data[stock][-2][4]) + "," + str(data[stock][-2][5]) + "\n")
            fs[i].flush()
            fs[i].close()
            print(data[stock][-1])
            print(data[stock][-2])
      openprice = share.get_open()
      if openprice == None:
        openprice = 0
      exec_query(stock, float(share.get_price()), float(openprice))
      minprices[stock] = min(minprices[stock], curr_price)
      maxprices[stock] = max(maxprices[stock], curr_price)
      i = i + 1

def close_all(fs): 
  for f in fs:
    f.close()

def get_stocks():
  query = "SELECT ticker FROM graaftrade_stock ORDER BY id"
  cursor.execute(query)
  result = cursor.fetchall()
  li = [x[0] for x in result]
  return li

def open_files(stocks, op):
  csvs = list()
  files = list()
  for stock in stocks:
    f = open("../assets/data/" + stock + ".csv", op)
    if (op == 'w'):
      f.write("Date,Open,High,Low,Close,Volume\n")
      f.flush()
    files.append(f)
    csvs.append(csv.writer(f, quoting=csv.QUOTE_ALL))
  return csvs,files

def main():
  stocks = get_stocks()
  for stock in stocks:
    minprices[stock] = 0
    maxprices[stock] = 0
    data[stock] = []
  csvs, files = open_files(stocks, 'w')
  atexit.register(close_all, files)
  set_interval(loop, 5, stocks, csvs)

if __name__ == "__main__": main()
