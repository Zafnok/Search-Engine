import operator
import inflect  # natural language processing
import yaml  # YAML file functionality
import atexit  # for exit functions
from collections import Counter  # dictionary-like object
import itertools
import re  # regex
from nltk.corpus import stopwords  # stopwords are common english words


# TODO need to add a ranking system for if sites have many words in common - such as if one description has 3 australia,
# TODO rank higher than 1 (initial algorithm - (-abs(x-3)+3) for description, then make content ranked lower
# TODO need to make a memory management function so that it can be used on Pi

# TODO webcrawl - in progress
# TODO need to rework docstrings, they are outdated!!! important
# TODO some functions reliant on certain type - add_to_search_dictionary, create_results_set_helper
class SearchEngine:
    """
    This class describes a search engine that uses a dictionary of tag : Site pairs
    The dictionary's values are sets of Sites and the keys are string tags
    """

    __inflect_engine = inflect.engine()

    # inflect is used for natural language processing, turns plurals into singulars and vice versa

    def __init__(self, search_dictionary_file_name="search_dictionary_data_file.yaml",
                 site_dictionary_file_name="site_dictionary_data_file.yaml"):
        """
        This is the constructor for SearchEngine
        :param search_dictionary_file_name: file path string for the search dictionary YAML file
        :param site_dictionary_file_name: file path string for the site dictionary YAML file
        """
        self.site_dictionary = dict()  # TODO this is needed for easy updating of references for search dictionary -
        # TODO site dictionary will have key be site url and value be the site object, the search dictionary will have
        # TODO the tag key and the site string value - corresponds to the site object in the site dictionary example
        # TODO call: site_dictionary[search_dictionary[tag]].relevancy_dictionary[tag] should return the relevance for
        # TODO that tag
        self.search_dictionary = dict()
        self.search_dictionary_file_name = search_dictionary_file_name
        self.site_dictionary_file_name = site_dictionary_file_name
        self.loaded = self.populate_from_file(self.search_dictionary_file_name,
                                              self.site_dictionary_file_name)  # not sure if needed anymore,
        # if not then make it so populate doesn't return
        atexit.register(self.write_to_file, self.search_dictionary_file_name, self.site_dictionary_file_name)

    @staticmethod
    def search_ranking_algorithm(num):
        """
        Takes a number and returns the number altered using the algorithm
        :param num: number to convert using algorithm
        :return: the converted number
        """
        return -abs(num - 3) + 3

    @staticmethod
    def clean_string(user_string):
        """
        This function cleans a string by removing whitespace and punctuation and converting it to lowercase
        :param user_string: string to clean
        :return: string.strip().lower() - also removes punctuation
        """
        return re.sub("[,:!?]", "", user_string.strip().lower().strip('.'))
        # return user_string.strip().lower().translate()(maketrans(string.punctuation)

    @staticmethod
    def order_dictionary(dictionary):
        """
        This function orders the dictionary's relevancy results by using the operator's sorted function.
        The reverse=True is due to the dictionary's relevancy results being ordered 1,2,3 rather than 3,2,1
        :param dictionary: search result's dictionary to sort by relevancy
        :return: the sorted dictionary
        """
        return sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)

    def add_to_search_dictionary(self, tags, site):
        """
        This function adds the tag : data pairing to the dictionary via a for-each loop that checks whether the
        tag (key) or its variants (plural/singular) is already in the dictionary. The function also adds the
        site url: Site pairing to the site dictionary
        :param tags: set of tags that are associated with the data
        :param site: Site to add to the value for each of the tags
        :return: None
        """
        tags = set([word for word in tags if word not in stopwords.words('english')])
        for tag in tags:
            word = self.clean_string(tag)
            if word not in set(stopwords.words('english')):  # common words from nltk
                if word in self.search_dictionary:
                    self.search_dictionary[word].add(str(site))
                else:
                    plural_str = self.__inflect_engine.plural(word)
                    singular_str = self.__inflect_engine.singular_noun(word)
                    if plural_str in self.search_dictionary:
                        self.search_dictionary[plural_str].add(str(site))
                    elif singular_str in self.search_dictionary:
                        self.search_dictionary[singular_str].add(str(site))
                    else:
                        self.search_dictionary[word] = {str(site)}
        self.site_dictionary[str(site)] = site

    # TODO don't know if the Sites will work with search function anymore, will have to test after
    # TODO running the scraper for a while
    def search_keys(self, user_input):
        """
        This function checks the user input delimited by spaces against the class-level dictionary and returns the
        results of the search. This function calls create_results_set and order_dictionary as well as conditionally
        calls add_to_dictionary.
        :param user_input: the string inputted by the user to check against the class-level search_dictionary
        :return: a formatted string that shows the sites and number of hits - sorted by number of hits
        """
        if len(user_input.strip()) > 0:
            results = self.order_dictionary(
                self.create_results_set(self.interpret_input(self.clean_string(user_input))))
            if len(results) == 0:
                new_tag_str = input("Search returned zero results\nWhat were you searching for?\nType "
                                    "None if you don't want to add to the engine.\n")
                if not new_tag_str.lower().strip() == "none":
                    self.add_to_search_dictionary(user_input.strip().split(" "), new_tag_str)
            else:
                return_str = ""
                for pair in results:
                    return_str += (pair[0] + " - hits: " + str(
                        pair[1]) + "\n")  # TODO eventually convert back to Site object
                    # return_str += (pair[0].get_site_name() + " - hits: " + str(pair[1]) + "\n")
                return return_str
        else:
            return "Invalid input, please try again."

    # this function is labyrinthine and should not be altered unless rebuilding wholly
    @staticmethod
    def interpret_input(user_input):
        """
        This function takes the user input string, converts it to post-fix, and returns it.
        :param user_input: user input string passed by search_keys
        :return: post-fix string
        """
        postfix_string = ""
        operator_stack = []
        # inner-most list comprehension splits based on quotes
        # TODO maybe better way to check if string empty
        # next-level out list comprehension conditionally splits - if the index is even, it will split on spaces,
        # other-wise (quoted strings) it will return a list of the one element, enclosed by quotes - FILTER MOVED HERE:
        # filters to check if the strip returns an empty string
        # final-level could have been done with comprehension but would be slower -
        # basically flattens the list of lists to make one single list
        ls = list(itertools.chain.from_iterable(
            [outer_string.split() if outer_index % 2 == 0 else ["\"" + outer_string + "\""] for
             outer_index, outer_string in enumerate(
                [inner_string.strip() for inner_string in SearchEngine.clean_string(user_input).split("\"")
                 ]) if len(outer_string.strip()) > 0 and not outer_string.strip().isspace()]))
        i = 0
        while i < len(ls):
            # val = ls[i] - for debugging
            if i < len(ls):
                if re.match("^[(]+$", ls[i]):
                    # this regex matches only open parentheses, and only if the whole word is
                    # made up of them. The below regex is the same but with closed parentheses.
                    ls[i:i + 2] = [''.join(ls[i:i + 2])]
                    i -= 1
                elif re.match("^[)]+$", ls[i]):
                    ls[i - 1:i + 1] = [''.join(ls[i - 1:i + 1])]
                    i -= 1
                elif (ls[i] != 'or' and ls[i] != 'and') and i % 2 == 1:
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

        # TODO create function to make this more concise
        # TODO does this need to be so wordy? Look into libraries/use Site more - can be condensed
        # TODO NOT operator - should be done, but maybe add NOT instead of just -

    # this function is labyrinthine and should not be altered unless rebuilt wholly
    def create_results_set(self, user_input):
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
        dictionary_stack = []  # TODO better name
        for word in self.clean_string(user_input).split(" "):
            if word == "or" or word == "and":
                dict_one_list = dictionary_stack.pop()  # TODO convert tuple to set probably - done
                dict_two_list = dictionary_stack.pop()
                if word == "and":
                    dictionary_stack.append([{key: dict_one_list[0][key] for key in dict_one_list[0] if
                                              key in dict_two_list[0]},
                                             {key: dict_one_list[1][key] for key in dict_one_list[1] if
                                              key in dict_two_list[1]}])
                else:
                    dictionary_stack.append([dict(Counter(dict_one_list[0]) + Counter(dict_two_list[0])),
                                             dict(Counter(dict_one_list[1]) + Counter(dict_two_list[1]))])
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
                    if word[-1] == '*':  # TODO change len to -1
                        # TODO this creates several lists of dicts in stack
                        word = word[0:-1]
                        counter = 0
                        for key in self.search_dictionary.keys():
                            if key.startswith(word):
                                self.create_results_set_helper(dictionary_stack, key, remove_flag)
                                counter += 1
                                if counter >= 2:
                                    dict_one_list = dictionary_stack.pop()
                                    dict_two_list = dictionary_stack.pop()
                                    dictionary_stack.append(
                                        [dict(Counter(dict_one_list[0]) + Counter(dict_two_list[0])),
                                         dict(Counter(dict_one_list[1]) + Counter(dict_two_list[1]))])

                    else:
                        if word in self.search_dictionary.keys():
                            self.create_results_set_helper(dictionary_stack, word, remove_flag)
                        else:
                            plural_str = self.__inflect_engine.plural(word)
                            singular_str = self.__inflect_engine.singular_noun(word)
                            if plural_str != word and plural_str in self.search_dictionary.keys():
                                self.create_results_set_helper(dictionary_stack, plural_str,
                                                               remove_flag)
                            elif singular_str != word and singular_str in self.search_dictionary.keys():
                                self.create_results_set_helper(dictionary_stack, singular_str,
                                                               remove_flag)
                            else:  # this is for the cases there are no results - should work
                                dictionary_stack.append([{}, {}])
        print(dictionary_stack)
        return {k: v for k, v in dictionary_stack[0][0].items() if k not in dictionary_stack[0][1]} if len(
            dictionary_stack) >= 1 and len(
            dictionary_stack[0]) > 1 else dictionary_stack[0][0] if len(dictionary_stack) >= 1 and len(
            dictionary_stack[0]) == 1 else {}  # TODO condense return
        # return difference between results_set and exclude_from_results_set based on keys and not key-value pairs

    def create_results_set_helper(self, dictionary_stack, key, remove_flag=False):
        """
        Populates the dictionary with the number of hits.
        :param dictionary_stack: Stack of dictionaries
        :param key: Key to check against class-level search_dictionary
        :param remove_flag: remove_flag which determines whether to add extra data to results_set
        :return: None
        """
        dictionary_stack.append([{}, {}])
        if remove_flag:
            for tag in self.search_dictionary[key]:
                if tag not in dictionary_stack[-1][1]:
                    dictionary_stack[-1][1][tag] = 1
        else:
            for site in self.search_dictionary[key]:
                if site in dictionary_stack[-1][0]:
                    dictionary_stack[-1][0][site] = \
                        dictionary_stack[-1][0][site] + self.site_dictionary[site].relevancy_dictionary[key]
                else:
                    dictionary_stack[-1][0][site] = self.site_dictionary[site].relevancy_dictionary[key]

    # TODO make this compatible with any stream so it can be used for server
    def write_to_file(self, search_dictionary_file_name, site_dictionary_file_name):
        """
        Writes the search_dictionary and site dictionary to their respective YAML files.
        :param search_dictionary_file_name: file string path for the search dictionary's YAML file.
        :param site_dictionary_file_name: file string path for the site dictionary's YAML file
        :return: None
        """
        try:
            with open(search_dictionary_file_name, 'x+') as data_file:
                yaml.dump(self.search_dictionary, data_file)
        except FileExistsError:
            with open(search_dictionary_file_name, 'w') as data_file:
                yaml.dump(self.search_dictionary, data_file)
        try:
            with open(site_dictionary_file_name, 'x+') as data_file:
                yaml.dump(self.site_dictionary, data_file)
        except FileExistsError:
            with open(site_dictionary_file_name, 'w') as data_file:
                yaml.dump(self.site_dictionary, data_file)

    # TODO make this compatible with any stream so it can be used for server - python open makes stream?
    # TODO might not need to return anything, since loaded isn't used right now
    def populate_from_file(self, search_dictionary_file_name, site_dictionary_file_name):
        """
        Populates the class-level search_dictionary and site dictionary from a YAML file.
        :param search_dictionary_file_name: file string path for the search dictionary's YAML file.
        :param site_dictionary_file_name: file string path for the site dictionary's YAML file.
        :return: Whether the files exist and loaded or not - True or False. - TODO this might change
        """
        try:
            with open(search_dictionary_file_name, 'r') as data_file:
                self.search_dictionary = yaml.load(data_file)
        except FileNotFoundError:
            return False
        try:
            with open(site_dictionary_file_name, 'r') as data_file:
                self.site_dictionary = yaml.load(data_file)
        except FileNotFoundError:
            return False
