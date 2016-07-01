from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.forms.models import model_to_dict
from django.template.loader import render_to_string
from .util import *
from . import models

def getBrokerData(request, broker_id):
  brokerData = getBrokerById(broker_id) 
  return {
    'id'            : broker_id,
    'firstname'     : brokerData.firstname,
    'lastname'      : brokerData.lastname,
    'full_name'     : brokerData.firstname + " " + brokerData.lastname,
    'website'       : brokerData.website,
    'email'         : request.session['user']['email'] if is_broker(request) else models.User.objects.get(id=brokerData.user_id).email,
    'creation_date' : brokerData.account_created,
    'last_active'   : brokerData.last_active,
    'trusted_by'    : brokerData.trusted_by,
    'blocked_by'    : brokerData.blocked_by,
    'faqs'          : brokerData.faqs
  }

def home(request):
  if not logged_in(request): return HttpResponseRedirect('/')
  if not is_broker(request): return HttpResponseRedirect('/home')
  broker = models.Broker.objects.get(user=models.User.objects.get(id=request.session['user']['id']))
  data = getHomeData(request)
  brokerdata = getBrokerData(request, broker.id)
  brokerdata['broker'] = True
  data['profile'] = render_to_string('brokerprofile.html', brokerdata)
  return render(request, 'broker.html', data)

def main(request, broker_id):
  if not logged_in(request): return HttpResponseRedirect('/')
  brokerdata = getBrokerData(request, broker_id)
  brokerdata['broker'] = False
  return render(request, 'brokerprofile.html', brokerdata)

def update(request, field, value):
  user = models.User.objects.get(id=request.session['user']['id']);
  b = models.Broker.objects.get(user=user)
  broker = getBrokerById(b.id)
  if field == 'website':
    broker.website = value
    broker.save()
  if field == 'email':
    user.email = value;
    request.session['user']['email'] = value;
    request.session.modified = True;
    user.save()
  if field == 'faq':
    broker.faqs = value;
    broker.save()
  if field == 'firstname':
    broker.firstname = value;
    broker.save()
  if field == 'lastname':
    broker.lastname = value;
    broker.save()
    
  return HttpResponseRedirect('/broker')
