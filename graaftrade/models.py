from django.db import models
from django.utils.timezone import now

class User(models.Model):
  username = models.CharField(max_length=32)
  password = models.CharField(max_length=512)
  salt = models.BigIntegerField(null=True)
  email = models.CharField(max_length=128, default='example@email.com')
  isBroker = models.BooleanField(default=0)

class Broker(models.Model):
  user = models.ForeignKey(User, null=True)
  firstname = models.CharField(max_length=32)
  lastname = models.CharField(max_length=32)
  fee = models.FloatField(default=0)
  performance = models.IntegerField(default=50)
  last_active = models.DateTimeField(auto_now_add=True, blank=True)
  account_created = models.DateTimeField(auto_now_add=True, blank=True)
  trusted_by = models.IntegerField(default=0)
  blocked_by = models.IntegerField(default=0)
  website = models.CharField(max_length=128, default='example.com')
  faqs = models.CharField(max_length=1500, default='')

class Stock(models.Model):
  ticker = models.CharField(max_length=8, default='X')
  name = models.CharField(max_length=128, default='STOCK')
  price = models.FloatField(default=0)
  change = models.FloatField(default=0)

class User_Stock(models.Model):
  stock = models.ForeignKey(Stock)
  user = models.ForeignKey(User) 
  amount = models.PositiveIntegerField(default=0)
  watching = models.BooleanField(default=0)

class News(models.Model):
  title = models.CharField(max_length=50, default='placeholder title')
  summary = models.CharField(max_length=300, default='placeholder summary')
  link = models.CharField(max_length=300, default='/')
  image = models.CharField(max_length=300, default='http://www.eonline.com/eol_images/Entire_Site/2013317/rs_560x415-130417122053-1024.DazedConfused.mh.041713.jpg')
  published = models.DateTimeField(auto_now_add=True)

class Stock_News(models.Model):
  stock = models.ForeignKey(Stock)
  title = models.CharField(max_length=300, default='NEWS JUST IN CYRUS IS A STONER')
  link = models.CharField(max_length=300, default='/')
  published = models.DateTimeField(auto_now_add=True)

class Chat(models.Model):
  user = models.ForeignKey(User)
  broker = models.ForeignKey(Broker)

class Chat_Content(models.Model):
  chat = models.ForeignKey(Chat)
  content = models.CharField(max_length=512, default='')
  from_broker = models.BooleanField(default=0)
  timestamp = models.DateTimeField(auto_now_add=True)
