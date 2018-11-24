from django.conf.urls import url
from searchengine import views

urlpatterns = [url(r'^search/$', views.search, name='search'), ]  # should change to path later
# this makes the url /search/ for query and /search/?q=sampletext for the search result page
