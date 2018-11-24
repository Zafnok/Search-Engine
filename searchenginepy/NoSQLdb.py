from unqlite import UnQLite
from unqlite import UnQLiteError
import ast
import SearchEngine
from nltk.corpus import stopwords
import time
import os

"""
Author: Nicholas Wentz
This is a module which allows the UnQlite NoSQL database to work
"""

# TODO raise error if error?

search_dictionary_db = UnQLite(os.path.join(os.path.dirname(__file__), "searchdb.db"))
site_dictionary_db = UnQLite(os.path.join(os.path.dirname(__file__), "sitedb.db"))
robots_txt_info_db = UnQLite(os.path.join(os.path.dirname(__file__), "robotsdb.db"))
stopword_set = set(stopwords.words('english'))


def store_kv_search_db(key, value):
    """
    Stores a tag: url pairing in the searchdb file
    :param key: Tag
    :param value: Site url string
    :return: None
    """
    if key not in stopword_set:  # common words from nltk
        try:
            if exists_in_search_db(key):
                store_kv_search_db_helper(key, value)
            else:
                plural_str = SearchEngine.inflect_engine.plural(key)
                singular_str = SearchEngine.inflect_engine.singular_noun(key)
                if exists_in_search_db(plural_str):
                    store_kv_search_db_helper(plural_str, value)
                elif exists_in_search_db(singular_str):
                    store_kv_search_db_helper(singular_str, value)
                else:
                    search_dictionary_db[key] = {value}
        except UnQLiteError:
            pass


def store_kv_search_db_helper(key, value):
    temp_set = retrieve_kv_search_db(key)
    temp_set.add(value)
    search_dictionary_db[key] = temp_set


def store_multiple_kv_search_db(keys, value):
    """
    Runs the store_kv_search_db function multiple times, one for each key in keys. Preferred way of adding to db.
    :param keys: Tags
    :param value: Site url string
    :return: None
    """

    keys = set([SearchEngine.clean_string(word) for word in keys if
                SearchEngine.clean_string(word) not in stopword_set])
    for key in keys:
        try:
            store_kv_search_db(key, value)
        except UnQLiteError:
            continue
    keys.clear()


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
                       i not in value[2]]
        for item in delete_list:
            del search_dictionary_db[item][key]
    site_dictionary_db[key] = value


def store_kv_robots_db(key, value):
    """
    This function stores the value at the specified key in the robotsdb
    :param key: key to store value at in robotsdb
    :param value: value to store at key in robotsdb
    :return: None
    """
    # value will be list [(requests, seconds), [num_request, time_since_first], crawl_delay]
    robots_txt_info_db[key] = value


def retrieve_kv_search_db(key):
    """
    This function takes a key and returns the matching list of sites from searchdb
    :param key: key to return value from searchdb for
    :return: list of site strings for key in searchdb
    """
    return ast.literal_eval(search_dictionary_db[key].decode())
    # if key in NoSQLdb.search_dictionary_db.keys() else False


def retrieve_kv_site_db_dictionary(key):
    """
    This function takes a key and returns the matching relevancy dictionary from sitedb
    :param key: key to return value from sitedb for
    :return: relevancy dictionary for site
    """
    return ast.literal_eval(site_dictionary_db[key].decode())[2] if exists_in_site_db(key) else None


def retrieve_kv_site_db_time(key):
    """
    This function returns the time of last visit
    :param key: site url
    :return: last visit time
    """
    return ast.literal_eval(site_dictionary_db[key].decode())[0]


def retrieve_kv_site_db_title(key):
    """
    This function returns the <title> of the site
    :param key: site url
    :return: title tag of site
    """
    return ast.literal_eval(site_dictionary_db[key].decode())[1]


# value will be list [(requests, seconds), [time1, time2, time3], crawl_delay]
def retrieve_kv_robots_db(key):
    """
    This function returns the list that is stored in the robots db at the key specified
    :param key: key for db to search on
    :return: the list at the specified key
    """
    return ast.literal_eval(robots_txt_info_db[key].decode())


def can_make_request(key):
    """
    This function says whether a request can be made to a site or not
    :param key: site url
    :return: True if crawler can proceed, False otherwise
    """
    robots_info = retrieve_kv_robots_db(key)
    need_update = False
    for times in reversed(robots_info[1]):
        if robots_info[0][1] is not None and time.time() - times >= robots_info[0][1]:
            times = -1
            need_update = True
    if need_update:
        store_kv_robots_db(key, robots_info)
    if (robots_info[0][0] is None or robots_info[0][0] > robots_info[1].count(-1)) and (
            robots_info[2] is None or time.time() - robots_info[1].max() > robots_info[2]):
        return True
    return False


def make_request(key):
    """
    This function changes one of the times in the respective site's url
    :param key: key to change one of the times
    :return: None
    """
    robots_info = retrieve_kv_robots_db(key)
    if robots_info[0][1] is not None:
        robots_info[1][robots_info[1].index(-1)] = time.time()


# TODO this takes a long time when retrieving into memory
def get_all_search_db_data():
    """
    This function returns the full dictionary for keys and their values from searchdb
    :return: the full data for searchdb
    """
    # print(os.path.join(os.path.dirname(__file__), "searchdb.db"))
    return {key: ast.literal_eval(value.decode()) for (key, value) in search_dictionary_db.items()}


# TODO this takes a long time when retrieving into memory
def get_all_site_db_data():
    """
    This function returns the full dictionary for keys and their values from sitedb
    :return: the full data for sitedb
    """
    return {key: ast.literal_eval(value.decode()) for (key, value) in site_dictionary_db.items()}


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
    try:
        return search_dictionary_db.exists(key)
    except UnQLiteError:
        pass


def exists_in_site_db(key):
    """
    This function checks whether the key exists in sitedb
    :param key: Key to check if exists in sitedb
    :return: True if exists in sitedb, False if not
    """
    return site_dictionary_db.exists(key)


def exists_in_robots_db(key):
    """
    This function checks whether the key exists in robotsdb
    :param key: key to check if exists in robotsdb
    :return: True if exists in robotsdb, False if not
    """
    return robots_txt_info_db.exists(key)


def close_and_save():
    """
    This function closes the databases so that they can save
    :return: None
    """
    search_dictionary_db.close()
    site_dictionary_db.close()
    robots_txt_info_db.close()
