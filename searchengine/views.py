# from django.shortcuts import render
from django.http import HttpResponse
import searchenginepy.SearchEngine

def index(request):
    search_result_list =


def search_result(request, query):
    return HttpResponse("You're looking at the search results for {}".format(query))
# Create your views here.
