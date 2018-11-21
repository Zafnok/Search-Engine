from django.shortcuts import render
from searchenginepy import SearchEngine

SearchEngine.initialize_dicts()


def search_result(request, query):
    search_result_list = SearchEngine.search_keys(query)
    context = {'search_result_list': search_result_list}
    return render(request, 'searchengine/search.html', context)
# Create your views here.
