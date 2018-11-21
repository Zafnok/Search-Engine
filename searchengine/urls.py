from django.urls import path
from . import views

urlpatterns = [path('search/<query>', views.search_result, name='search')]
