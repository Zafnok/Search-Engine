from django.shortcuts import render
from searchenginepy import SearchEngine
from django.core.paginator import Paginator

SearchEngine.initialize_dicts()  # needed otherwise dicts aren't initialized and every query shows no results


# all Django code learned from Django tutorials on their url - TODO add later
def search(request):  # combined query and search forms
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
