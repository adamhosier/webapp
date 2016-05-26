from django.db import models

class User(models.Model):
  username = models.CharField(max_length=32)
  password = models.CharField(max_length=128)
  salt = models.PositiveIntegerField(null=True)
  email = models.CharField(max_length=128, default='example@email.com')

class Stock(models.Model):
  ticker = models.CharField(max_length=8, default='X')

class Stock_Change(models.Model):
  stock_id = models.ForeignKey(Stock)
  timestamp = models.DateTimeField()
  newprice = models.FloatField(default=0)

class User_Stock(models.Model):
  stock_id = models.ForeignKey(Stock)
  user_id = models.ForeignKey(User) 
  amount = models.PositiveIntegerField(default=0)
