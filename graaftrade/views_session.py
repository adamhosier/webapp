from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.forms.models import model_to_dict
from django.contrib import auth
from . import models
from .util import *
from random import randint
import hashlib , feedparser
from datetime import datetime

MAX_SALT_VAL = 999999999999999999
MIN_SALT_VAL = 100000000000000000

# helper function to sign a user in and set the session as their user record
def sign_in(request, loginUser):
  user = models.User.objects.get(username__iexact=loginUser)
  request.session['logged_in'] = True
  request.session['open_chats'] = []
  request.session['user'] = model_to_dict(user)

  if user.isBroker:
    broker = models.Broker.objects.get(user=user)
    broker.last_active = datetime.now()
    broker.save()

  return HttpResponseRedirect('/home')

def sign_out(request):
  request.session['logged_in'] = False
  request.user = None
  request.session['open_chats'] = [];
  return HttpResponseRedirect('/')

# index/login page
def login(request):
  if logged_in(request): return HttpResponseRedirect('/home')
  if 'login-submit' in request.POST: # if form has been submitted
    loginUser = request.POST['login-username']
    loginPass = request.POST['login-password']

    if loginUser is None:
      return HttpResponseRedirect('invalid')
    if loginPass is None:
      return HttpResponseRedirect('invalid')

    # check user exists
    entry = models.User.objects.filter(username__iexact=loginUser)
    if len(entry) == 0:
      return HttpResponseRedirect('invalid')
    else:
      # append salt and check encrypted passwords match
      entry = entry.first()
      saltVal = entry.salt
      passwordSalt = loginPass + str(saltVal)
      passwordSaltBytes = passwordSalt.encode('utf-8')
      hashedPasswordUser = hashlib.sha256(passwordSaltBytes).hexdigest()
      hashedPasswordTable = entry.password
    
    # SELECT * FROM user WHERE username=loginUser AND password=loginPass
    if hashedPasswordUser == hashedPasswordTable:
      return sign_in(request, loginUser)
    else:
      return HttpResponseRedirect('/invalid')
  else: # if form not submitted
    return render(request, 'index.html')  

def register(request):
  if logged_in(request): return HttpResponseRedirect('/home')
  if 'register-submit-user' in request.POST or 'register-submit-broker' in request.POST: # if register form has been submitted
    isUser = 'register-submit-user' in request.POST;
    registerUser = request.POST['register-username']
    registerEmail1 = request.POST['register-email-1']
    registerEmail2 = request.POST['register-email-2']
    registerPassword1 = request.POST['register-password-1']
    registerPassword2 = request.POST['register-password-2']
    
    successUniqueUser = len(models.User.objects.filter(username__iexact=registerUser))
    successUniqueEmail = len(models.User.objects.filter(email__iexact=registerEmail1))       

    # email confirmation
    emailMatch = registerEmail1 == registerEmail2
    # password confirmation
    passwordMatch = registerPassword1 == registerPassword2

    if not emailMatch or not passwordMatch:
      return render(request, 'register.html')
    elif not successUniqueUser and not successUniqueEmail: 
      # adding a salt to the password and hashing
      saltVal = randint(MIN_SALT_VAL, MAX_SALT_VAL)
      passwordSalt = registerPassword1 + str(saltVal)
      passwordSaltBytes = passwordSalt.encode('utf-8')
      hashedPassword = hashlib.sha256(passwordSaltBytes).hexdigest()
      # save the username, encrypted password and salt value tuple to table
      user = models.User(username=registerUser, password=hashedPassword, email=registerEmail1, salt=saltVal)
      if not isUser:
        user.isBroker = True
        user.save()
        broker = models.Broker(firstname='Firstname', lastname='Lastname', user=user)
        broker.save()
      else:
        user.save()
      return sign_in(request, registerUser)
    else:
      return HttpResponseRedirect('/register')
  else: # if form not submitted
    return render(request, 'register.html')

def logout(request):
  return sign_out(request)
