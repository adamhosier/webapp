from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import auth
from . import models

# index/login page
def login(request):
  if 'login-submit' in request.POST: # if form has been submitted
    loginUser = request.POST['login-username']
    loginPass = request.POST['login-password']

    # TODO: validation of username + password

    # query db
    # SELECT * FROM user WHERE username=loginUser AND password=loginPass
    success = len(models.User.objects.filter(username=loginUser, password=loginPass)) == 1
    if success:
      return HttpResponseRedirect('/home')
    else:
      return HttpResponseRedirect('/invalid')
  else: # if form not submitted
    return render(request, 'index.html')  

def register(request):
  return render(request, "register.html");

def home(request):
  return render(request, 'home.html');
