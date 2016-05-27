from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.forms.models import model_to_dict
from django.contrib import auth
from . import models
from random import randint
import hashlib 

MAXSALTVAL = 999999999999999999
MINSALTVAL = 100000000000000000

# helper function to sign a user in
def sign_in(request, loginUser):
  request.session['logged_in'] = True
  request.session['user'] = model_to_dict(models.User.objects.get(username=loginUser))
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

    if loginUser is None:
      return HttpResponseRedirect('invalid')
    if loginPass is None:
      return HttpResponseRedirect('invalid')

    
    # query db
    entry = models.User.objects.get(username=loginUser)
    saltVal = entry.salt
    passwordSalt = loginPass + str(saltVal)
    passwordSaltBytes = passwordSalt.encode('utf-8')
    hashedPasswordUser = hashlib.sha256(passwordSaltBytes).hexdigest()
    hashedPasswordTable = entry.password
    print(hashedPasswordTable)
    print(saltVal)
    
    # SELECT * FROM user WHERE username=loginUser AND password=loginPass
    # success = len(models.User.objects.filter(username=loginUser, password=loginPass)) == 1
    if hashedPasswordUser == hashedPasswordTable:
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

      # adding a salt to the password and hashing
      saltVal = randint(MINSALTVAL, MAXSALTVAL)
      passwordSalt = registerPassword1 + str(saltVal)
      passwordSaltBytes = passwordSalt.encode('utf-8')
      hashedPassword = hashlib.sha256(passwordSaltBytes).hexdigest()
      print(hashedPassword)
      print(saltVal)
      # save the username, encrypted password and salt value tuple to table
      user = models.User(username=registerUser, password=hashedPassword, email=registerEmail1, salt=saltVal)
      user.save()
      return sign_in(request, registerUser)

  else: # if form not submitted
    return render(request, 'register.html')

def logout(request):
  return sign_out(request)
