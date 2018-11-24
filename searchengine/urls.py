from django.conf.urls import url
from searchengine import views

urlpatterns = [url(r'^search/$', views.search, name='search'), ]
# this makes the url /search/ for query and /search/?q=asdjahsda for the search result page
