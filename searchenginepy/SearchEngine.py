import operator
import inflect
import NoSQLdb
from collections import Counter
import itertools
import re
import regex

# TODO quoted strings no longer work - should somehow store relevancy dictionary by order?
"""
Author: Nicholas Wentz
This module describes a search engine that uses a dictionary of tag : Site pairs
The dictionary's values are sets of Sites and the keys are string tags
"""

inflect_engine = inflect.engine()
# inflect is used for natural language processing, turns plurals into singulars and vice versa
site_dict = dict()
search_dict = dict()


def initialize_dicts():
    """
    This function initializes the dictionaries used. This is necessary as otherwise the dictionaries would be
    initialized to None and would cause errors in modules that rely on SearchEngine (i.e. WebCrawler, which
    populates the NoSQLdb)
    :return: None
    """
    global site_dict, search_dict
    site_dict = {k: [v[1], v[2]] for k, v in
                 NoSQLdb.get_all_site_db_data().items()}  # TODO NoSQL calls later maybe impact perf
    search_dict = NoSQLdb.get_all_search_db_data()


# TODO this is WIP, trying to make more factors for ranking
def search_ranking_algorithm(list_num):
    """
    This function takes a number and converts it into a relevancy score
    :param list_num: list of numbers to convert using algorithm
    :return: number converted using algorithm
    """
    # return -abs(num - 10) + 10 TODO this needs to be refined, ethics page returns large negative number
    return pow(2 * list_num[0] + list_num[1], 2) + list_num[2]


def clean_string(user_string):
    """
    This function cleans a string by removing whitespace and punctuation and converting it to lowercase
    :param user_string: string to clean
    :return: string.strip().lower()
    """
    return regex.sub(r"(?V1)[[^\w\s]--[()\".\-]]", "", user_string.lower().strip('.'), regex.UNICODE)


def order_dictionary(dictionary):
    """
    This function orders the dictionary's hit results by using the operator's sorted function.
    The reverse=True is due to the dictionary's hit results being ordered 1,2,3 rather than 3,2,1
    :param dictionary: search result's dictionary to sort by hits
    :return: the sorted dictionary
    """
    return sorted(list(dictionary.items()), key=operator.itemgetter(1), reverse=True)


def search_keys(user_input):
    """
    This function checks the user input delimited by spaces against the class-level dictionary and returns the
    results of the search. This function calls create_results_set and order_dictionary as well as conditionally
    calls add_to_dictionary.
    :param user_input: the string inputted by the user to check against the class-level search_dictionary
    :return: a formatted string that shows the sites and number of hits - sorted by number of hits
    """
    if len(user_input.strip()) > 0:
        results = order_dictionary(create_results_set(interpret_input(clean_string(user_input))))
        return [[result[0], site_dict[result[0]][0]] for result in results]
    else:
        return "Invalid input, please try again."


def interpret_input(user_input):
    """
    This function takes the user input string, converts it to post-fix, and returns it.
    :param user_input: user input string passed by search_keys
    :return: post-fix string
    """
    postfix_string = ""
    operator_stack = []
    # inner-most list comprehension splits based on quotes
    # next-level out list comprehension conditionally splits - if the index is even, it will split on spaces,
    # other-wise (quoted strings) it will return a list of the one element, enclosed by quotes - FILTER MOVED HERE:
    # filters to check if the strip returns an empty string
    # final-level could have been done with comprehension but would be slower -
    # basically flattens the list of lists to make one single list
    ls = list(itertools.chain.from_iterable(
        [outer_string.split() if outer_index % 2 == 0 else ["\"" + outer_string + "\""] for
         outer_index, outer_string in enumerate(
            [inner_string.strip() for inner_string in clean_string(user_input).split("\"")
             ]) if len(outer_string.strip()) > 0 and not outer_string.strip().isspace()]))
    i = 0
    while i < len(ls):
        if i < len(ls):
            if re.match("^[(]+$", ls[i]):
                # this regex matches only open parentheses, and only if the whole word is
                # made up of them. The below regex is the same but with closed parentheses.
                ls[i:i + 2] = [''.join(ls[i:i + 2])]
                i -= 1
            elif re.match("^[)]+$", ls[i]):
                ls[i - 1:i + 1] = [''.join(ls[i - 1:i + 1])]
                i -= 1
            elif ls[i][0] == '-' and i % 2 == 1:
                ls.insert(i, 'and')
            elif (ls[i] != 'or' and ls[i] != 'and' and ls[i][0] != '-') and i % 2 == 1:
                # TODO the more complicated queries are working but somehow or is being inserted for blah -blah
                ls.insert(i, 'or')
        i += 1
    for word in ls:
        has_added_word = False
        while word[0] == '(':
            operator_stack.append(word[0])
            word = word[word.index('(') + 1:]
        if word[-1] == ')':
            word = word[:word.index(')')]
            postfix_string += word + " "
            has_added_word = True
            while operator_stack[-1] != '(':
                postfix_string += operator_stack.pop() + " "
            operator_stack.pop()
        if word == "and" or word == "or":
            if len(operator_stack) > 0 and operator_stack[-1] != '(':
                postfix_string += operator_stack.pop() + " "
            operator_stack.append(word)
        elif not has_added_word:
            postfix_string += word + " "
    while len(operator_stack) > 0:
        if operator_stack[-1] == '(':
            operator_stack.pop()
        else:
            postfix_string += operator_stack.pop() + " "
    return postfix_string
    # TODO NOT operator - should be done, but maybe add NOT instead of just -


# TODO in testing, a -b works but a - b doesn't. also, a -b works, a and b works, but (a -b) and c does not work
# TODO - should work now
# (a -b) and c returns same result as (a -b) a = philosophy b = feminism c = mathematics
def create_results_set(user_input):
    """
    This function is called by search_keys and creates the actual results set used by search_keys to make the
    formatted return string. By using the - operator, the word will be added to a dictionary that is subtracted
    from the normal result set. This function calls send_to_helper.
    :param user_input: user_input is  also sent by search_keys and is used to check each word against the
    class-level's search_dictionary keys.
    :return: the results_set - excluded_from_results_set which is another dictionary populated by the user_input
    words which start with the - operator.
    """
    remove_flag_single_char = False
    dictionary_stack = []
    for word in clean_string(user_input).split():
        if word == "or" or word == "and":
            if len(dictionary_stack) > 1:
                dict_one_list = dictionary_stack.pop()
                dict_two_list = dictionary_stack.pop()
                if word == "and":
                    dictionary_stack.append([{key: dict_one_list[0][key] for key in dict_one_list[0] if
                                              key in dict_two_list[0]}, dict_one_list[1] | dict_two_list[1]])
                else:
                    dictionary_stack.append(
                        [dict(Counter(dict_one_list[0]) + Counter(dict_two_list[0])),
                         dict_one_list[1] & dict_two_list[1]])
        else:
            remove_flag = False
            if remove_flag_single_char:
                remove_flag = True
                remove_flag_single_char = False
            if word[0] == '-':
                remove_flag = True
                word = word[1:]
                if len(word) == 0:
                    remove_flag_single_char = True
            if not remove_flag_single_char:
                if word[-1] == '*':
                    word = word[0:-1]
                    counter = 0
                    for key in search_dict:
                        if key.startswith(word):
                            create_results_set_helper(dictionary_stack, key, remove_flag)
                            counter += 1
                            if counter >= 2:
                                dict_one_list = dictionary_stack.pop()
                                dict_two_list = dictionary_stack.pop()
                                dictionary_stack.append(
                                    [dict(Counter(dict_one_list[0]) + Counter(dict_two_list[0])),
                                     dict_one_list[1] & dict_two_list[1]])
                else:
                    if word in search_dict:
                        create_results_set_helper(dictionary_stack, word, remove_flag)
                    else:
                        plural_str = inflect_engine.plural(word)
                        singular_str = inflect_engine.singular_noun(word)
                        if plural_str != word and plural_str in search_dict:
                            create_results_set_helper(dictionary_stack, plural_str,
                                                      remove_flag)
                        elif singular_str != word and singular_str in search_dict:
                            create_results_set_helper(dictionary_stack, singular_str,
                                                      remove_flag)
                        else:  # this is for the cases there are no results - should work
                            dictionary_stack.append([{}, set()])
    return {k: v for k, v in dictionary_stack[0][0].items() if k not in dictionary_stack[0][1]} if len(
        dictionary_stack) >= 1 and len(
        dictionary_stack[0]) > 1 else dictionary_stack[0][0] if len(dictionary_stack) >= 1 and len(
        dictionary_stack[0]) == 1 else {}
    # return difference between results_set and exclude_from_results_set based on keys and not key-value pairs


def create_results_set_helper(dictionary_stack, key, remove_flag=False):
    """
    Populates the dictionary with the number of hits.
    :param dictionary_stack: Stack of dictionaries
    :param key: Key to check against class-level search_dictionary
    :param remove_flag: remove_flag which determines whether to add extra data to results_set
    :return: None
    """
    if remove_flag:
        for tag in search_dict[key]:
            dictionary_stack[-1][1].add(tag)
    else:
        dictionary_stack.append([{}, set()])
        for site in search_dict[key]:
            if site in site_dict and key in site_dict[site][1]:
                if site in dictionary_stack[-1][0]:
                    dictionary_stack[-1][0][site] += search_ranking_algorithm(site_dict[site][1][key])
                    # 1 in site_dict[site] is for relevancy dictionary, since 0 is the title - needed for speeding up and eliminating NoSQLdb calls
                else:
                    dictionary_stack[-1][0][site] = search_ranking_algorithm(site_dict[site][1][key])
