from django.shortcuts import render
from searchenginepy import SearchEngine
from django.core.paginator import Paginator

"""
Author: Nicholas Wentz
"""
SearchEngine.initialize_dicts()  # needed otherwise dicts aren't initialized and every query shows no results


# all Django code learned from https://docs.djangoproject.com/en/2.1/intro/tutorial01/
def search(request):
    """
    This view is used for the first loading of the search page - returns the query HTML form - and for the loading of
    search results - loads a page of 10 results.
    :param request: HttpRequest
    :return: A rendered page
    """
    # combined query and search forms
    error = False
    if 'q' in request.GET:  # checks if a query is empty or not
        q = request.GET['q']
        if not q:  # same as above (probably minor difference)
            error = True
        else:
            search_result_list = SearchEngine.search_keys(q)
            paginator = Paginator(search_result_list, 10)
            page = request.GET.get('page')
            results = paginator.get_page(page)
            context = {'results': results, 'query': q, 'search_result_list': search_result_list}
            # context needed for showing correctly rendered HTML
            return render(request, 'searchengine/search.html', context)
    return render(request, 'searchengine/query.html', {'error': error})  # show error if no query
