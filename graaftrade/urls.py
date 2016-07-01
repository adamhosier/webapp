"""graaftrade URL Configuration

The `urlpatterns` list routes URLs to views_session. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views_session.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf.urls import url
from django.conf import settings
from django.contrib import admin
from . import views_session, views_home, views_stock, views_broker

urlpatterns = [
    url(r'^$', views_session.login),
    url(r'^invalid', views_session.login),
    url(r'^register$', views_session.register),
    url(r'^logout$', views_session.logout),
    
    url(r'^home$', views_home.home),
    url(r'^home/stocks$', views_home.stocks),
    url(r'^home/update/(\d+)$', views_home.update),
    url(r'^home/openchat/(\d+)$', views_home.open_chat),
    url(r'^chatupdate$', views_home.chat_update),

    url(r'^broker$', views_broker.home),
    url(r'^broker/update/([a-z]+)/([A-Za-z\d\.\-@\s]+)$', views_broker.update),

    url(r'^stock/([A-Z\.]+)$', views_stock.main),
    url(r'^stock/remove/([A-Z\.]+)$', views_stock.remove),
    url(r'^stock/search/(.+)$', views_stock.search),
    url(r'^stock/add/([A-Z\.]+)$', views_stock.add),
    url(r'^stock/update/([A-Z\.]+)/(\d+)$', views_stock.update),
    url(r'^stock/move/([A-Z\.]+)$', views_stock.move_watch),

    url(r'^compare/([A-Z\.]+)&([A-Z\.]+)$', views_stock.compare),

    url(r'^watch/add/([A-Z\.]+)$', views_stock.watch),
    url(r'^watch/move/([A-Z\.]+)$', views_stock.move),
    url(r'^watch/remove/([A-Z\.]+)$', views_stock.remove_watch),
 
    url(r'^broker/(\d+)$', views_broker.main),
   
    url(r'^admin/', admin.site.urls),
]
