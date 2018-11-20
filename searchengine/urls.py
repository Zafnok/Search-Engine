from django.urls import path
from . import views

urlpatterns = [path('', views.index, name='index'), path('search/<query>', views.search_result, name='search')]
