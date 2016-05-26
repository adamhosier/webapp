from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import auth
from . import models

# helper function to sign a user in
def sign_in(request, loginUser):
  request.session['logged_in'] = True
  request.session['username'] = loginUser
  return HttpResponseRedirect('/home')

def sign_out(request):
  request.session['logged_in'] = False
  return HttpResponseRedirect('/')

# index/login page
def login(request):
  if 'logged_in' in request.session and request.session['logged_in']:
    return HttpResponseRedirect('/home')
  if 'login-submit' in request.POST: # if form has been submitted
    loginUser = request.POST['login-username']
    loginPass = request.POST['login-password']

    # TODO: validation of username + password

    # query db
    # SELECT * FROM user WHERE username=loginUser AND password=loginPass
    success = len(models.User.objects.filter(username=loginUser, password=loginPass)) == 1
    if success:
      return sign_in(request, loginUser)
    else:
      return HttpResponseRedirect('/invalid')
  else: # if form not submitted
    return render(request, 'index.html')  

def register(request):
  if 'register-submit' in request.POST: # if register form has been submitted
    registerUser = request.POST['register-username']
    registerEmail1 = request.POST['register-email-1']
    registerEmail2 = request.POST['register-email-2']
    registerPassword1 = request.POST['register-password-1']
    registerPassword2 = request.POST['register-password-2']
    
    # email confirmation
    emailMatch = registerEmail1 == registerEmail2
    # password confirmation
    passwordMatch = registerPassword1 == registerPassword2
    if (not emailMatch or not passwordMatch):
      return render(request, 'register.html')
    else:
      user = models.User(username=registerUser, password=registerPassword1, email=registerEmail1)
      user.save()
      return sign_in(request, registerUser)
  else: # if form not submitted
    return render(request, 'register.html')

def home(request):
  # {{ username }} => request.session['username']
  return render(request, 'home.html', {'username':request.session['username']});

def logout(request):
  return sign_out(request)
