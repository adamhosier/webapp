#!/usr/bin/env python3

import feedparser, psycopg2, time, sched

s = sched.scheduler(time.time, time.sleep)
conn = psycopg2.connect("dbname=graaftrade user=dan host=localhost password=password")
cursor = conn.cursor()
NEWS_REFRESH_RATE = 1000


# gives an array parsed from xml of the 20 newest stories based on given stock 
# ticker/s 
def get_ticker_news():
  s.enter(NEWS_REFRESH_RATE, 1, get_ticker_news)
 
  # Main News Feed 
  rssfeed = 'http://feeds.skynews.com/feeds/rss/business.xml'
  news = feedparser.parse(rssfeed)

  for entry in news['entries']:
    cursor.execute("SELECT title FROM graaftrade_news WHERE title=%s", (entry['title'],))
    i = cursor.fetchone()
    if not i:
      title   =  entry['title'] 
      image   =  entry['media_thumbnail'][0]['url']
      link    =  entry['link']
      summary =  entry['summary']
      pubDate =  entry['published'] 
      cursor.execute("INSERT INTO graaftrade_news (title, summary, link, image, published) VALUES (%s,%s,%s,%s,%s)",(title, summary, link, image, pubDate))
  conn.commit()

  # Stock News Feed
  all_stocks = get_stocks()
  
  for stock in all_stocks:
    rssStockfeed = 'http://finance.yahoo.com/rss/headline?s='+stock
    stockNews = feedparser.parse(rssStockfeed)
   
    for entry in stockNews['entries']:
      title = entry['title']
      if title[0] == '[' : title = title[5:]
      cursor.execute("SELECT title FROM graaftrade_stock_news WHERE title=%s", (title,))
      i = cursor.fetchone()
      if not i:
        link = entry['link']
        pubDate = entry['published']
        cursor.execute("INSERT INTO graaftrade_stock_news (stock_id, title, link, published) VALUES ((SELECT id FROM graaftrade_stock WHERE ticker=%s),%s,%s,%s)",(stock, title, link, pubDate))
  conn.commit()      

# gets a list of tickers in the database
def get_stocks():
  cursor.execute("SELECT ticker FROM graaftrade_stock ORDER BY id")
  return [x[0] for x in cursor.fetchall()]

get_ticker_news()
s.run()
