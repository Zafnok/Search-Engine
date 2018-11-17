from unqlite import UnQLite
import ast
import atexit
from SearchEngine import clean_string, inflect_engine
from nltk.corpus import stopwords

"""
Author: Nicholas Wentz
This is a module which allows the UnQlite NoSQL database to work
"""

# TODO raise error if error?

search_dictionary_db = UnQLite("searchdb.db")
site_dictionary_db = UnQLite("sitedb.db")


# queue_dictionary_db = UnQLite("queuedb")


def store_kv_search_db(key, value):
    """
    Stores a tag: url pairing in the searchdb file
    :param key: Tag
    :param value: Site url string
    :return: None
    """
    if not exists_in_search_db(key):
        search_dictionary_db[key] = {value}
    else:
        set(search_dictionary_db[key]).add(value)


def store_multiple_kv_search_db(keys, value):
    """
    Runs the store_kv_search_db function multiple times, one for each key in keys. Preferred way of adding to db.
    :param keys: Tags
    :param value: Site url string
    :return: None
    """

    keys = set([clean_string(word) for word in keys if
                clean_string(word) not in stopwords.words('english')])
    for key in keys:
        if key not in set(stopwords.words('english')):  # common words from nltk
            if exists_in_search_db(key):
                store_kv_search_db(key, value)
            else:
                plural_str = inflect_engine.plural(key)
                singular_str = inflect_engine.singular_noun(key)
                if exists_in_search_db(plural_str):
                    store_kv_search_db(plural_str, value)
                elif exists_in_search_db(singular_str):
                    store_kv_search_db(singular_str, value)
                else:
                    store_kv_search_db(key, value)


# def store_kv_queue_db(value):
#     queue_dictionary_db[max(iter(queue_dictionary_db), default=0)] = value


def store_kv_site_db(key, value):
    """
    Stores a url string : relevancy dictionary pairing in sitedb file.
    :param key: Site url string
    :param value: Site rlevancy dictionary
    :return: None
    """
    if exists_in_site_db(key):
        # print(NoSQLdb.retrieve_kv_site_db(key).decode())
        # print(ast.literal_eval(NoSQLdb.retrieve_kv_site_db(key).decode()))
        delete_list = [i for i in ast.literal_eval(retrieve_kv_site_db_dictionary(key).decode()).keys() if
                       i not in value[1]]
        for item in delete_list:
            del search_dictionary_db[item][key]
    site_dictionary_db[key] = value


def retrieve_kv_search_db(key):
    """
    This function takes a key and returns the matching list of sites from searchdb
    :param key: key to return value from searchdb for
    :return: list of site strings for key in searchdb
    """
    return search_dictionary_db[key]  # if key in NoSQLdb.search_dictionary_db.keys() else False


def retrieve_kv_site_db_dictionary(key):
    """
    This function takes a key and returns the matching relevancy dictionary from sitedb
    :param key: key to return value from sitedb for
    :return: relevancy dictionary for site
    """
    return site_dictionary_db[key][1]  # if key in NoSQLdb.site_dictionary_db.keys() else False


def retrieve_kv_site_db_time(key):
    return site_dictionary_db[key][0]


# def retrieve_kv_queue_db(key):
#     return queue_dictionary_db[key]


# def pop_item_queue_db():
#
#     return queue_dictionary_db.pop(next(iter(queue_dictionary_db), default=None))
#

def get_all_search_db_data():
    """
    This function returns the full dictionary for keys and their values from searchdb
    :return: the full data for searchdb
    """
    return {key: value for (key, value) in search_dictionary_db.items()}


def get_all_site_db_data():
    """
    This function returns the full dictionary for keys and their values from sitedb
    :return: the full data for sitedb
    """
    return {key: value for (key, value) in site_dictionary_db.items()}


def get_search_db_keys():
    """
    This function returns all the keys from searchdb
    :return: Keys for searchdb
    """
    return search_dictionary_db.keys()


def get_site_db_keys():
    """
    This function returns all the keys for sitedb
    :return: Keys for sitedb
    """
    return site_dictionary_db.keys()


def exists_in_search_db(key):
    """
    This function checks whether the key exists in searchdb
    :param key: Key to check if exists in searchdb
    :return: True if exists in searchdb, False if not
    """
    return search_dictionary_db.exists(key)


def exists_in_site_db(key):
    """
    This function checks whether the key exists in sitedb
    :param key: Key to check if exists in sitedb
    :return: True if exists in sitedb, False if not
    """
    return site_dictionary_db.exists(key)


# def exists_in_queue_db(key):
#     return queue_dictionary_db.exists(key)


def close_and_save():
    search_dictionary_db.close()
    site_dictionary_db.close()
    # queue_dictionary_db.close()
    #


atexit.register(close_and_save)
