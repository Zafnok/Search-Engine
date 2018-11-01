import operator
import inflect
import yaml
import atexit
from collections import Counter
import itertools


# TODO use atexit to write on exit - should be done


# TODO check variable names, some are bad
# TODO add NOT/AND/OR - Stack/Queue structure - notes in notebook
# TODO add functionality to write on close - should be done
# TODO add categories to sites - i.e. news/gaming/math etc - metadata of site should explain
# TODO webcrawl

class SearchEngine:
    """
    This class describes a search engine that uses a dictionary of tag : Site pairs
    The dictionary's values are sets of Sites and the keys are string tags
    """

    __inflect_engine = inflect.engine()

    # inflect is used for natural language processing, turns plurals into singulars and vice versa

    def __init__(self, file_name="data_file.yaml"):  # TODO this is new, make sure it works
        """
        This is the constructor for SearchEngine
        :param file_name: file name for input YAML file
        """
        self.search_dictionary = {}
        self.file_name = file_name
        self.loaded = self.populate_from_file(self.file_name)
        atexit.register(self.write_to_file, self.file_name)

    @staticmethod
    def clean_string(string):
        """
        This function cleans a string by removing whitespace and converting it to lowercase
        :param string: string to clean
        :return: string.strip().lower()
        """
        return string.strip().lower()

    @staticmethod
    def order_dictionary(dictionary):
        """
        This function orders the dictionary's hit results by using the operator's sorted function.
        The reverse=True is due to the dictionary's hit results being ordered 1,2,3 rather than 3,2,1
        :param dictionary: search result's dictionary to sort by hits
        :return: the sorted dictionary
        """
        return sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)

    # TODO make tags clean (strip/lower)
    def add_to_dictionary(self, tags, data):
        """
        This functuon adds the tag : data pairing to the dictionary via a for-each loop that checks whether the
        tag (key) is already in the dictionary
        :param tags: set of tags that are associated with the data
        :param data: Site to add to the value for each of the tags
        :return: None
        """
        for tag in tags:
            word = self.clean_string(tag)
            if word in self.search_dictionary:
                self.search_dictionary[word].add(data)
            else:
                self.search_dictionary[word] = {data}

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
                self.create_results_set_helper(self.interpret_input(self.clean_string(user_input))))
            if len(results) == 0:
                new_tag_str = input("Search returned zero results\nWhat were you searching for?\nType "
                                    "None if you don't want to add to the engine.\n")
                if not new_tag_str.lower().strip() == "none":
                    self.add_to_dictionary(user_input.strip().split(" "), new_tag_str)
            else:
                return_str = ""
                for pair in results:
                    return_str += (pair[0].get_site_name() + " - hits: " + str(pair[1]) + "\n")
                return return_str
        else:
            return "Invalid input, please try again."

    # TODO stacks/queues structure, recursion? Old assignment doesn't return anything, just adds string to stack
    @staticmethod
    def interpret_input(user_input):
        postfix_string = ""
        operator_stack = []
        open_parentheses = 0
        # open_quotes = False
        # quote_word = ""
        word_check = 0  # 1 when there is a word, if >=2 then next word w/o operator in between has implied OR
        num_implied_or_to_add = 0  # counts number of ors for parentheses
        # print(list(itertools.chain.from_iterable(
        #     [outer_string.split() if outer_index % 2 == 0 else ["\"" + outer_string + "\""] for
        #      outer_index, outer_string in enumerate(
        #         [inner_string.strip() for inner_string in SearchEngine.clean_string(user_input).split("\"")
        #          ]) if
        #      len(outer_string.strip()) > 0 and not outer_string.strip().isspace()])))
        # inner-most list comprehension splits based on quotes
        # TODO maybe better way to check if string empty
        # next-level out list comprehension conditionally splits - if the index is even, it will split on spaces,
        # other-wise (quoted strings) it will return a list of the one element, enclosed by quotes - FILTER MOVED HERE:
        # filters to check if the strip returns an empty string
        # final-level could have been done with comprehension but would be slower -
        # basically flattens the list of lists to make one single list

        # old for loop used SearchEngine.clean_string(user_input).split(" ")
        for word in list(itertools.chain.from_iterable(
                [outer_string.split() if outer_index % 2 == 0 else ["\"" + outer_string + "\""] for
                 outer_index, outer_string in enumerate(
                    [inner_string.strip() for inner_string in SearchEngine.clean_string(user_input).split("\"")
                     ]) if len(outer_string.strip()) > 0 and not outer_string.strip().isspace()])):
            if word[0] != "\"":
                if word[0] == '(':
                    if len(operator_stack) == 0 and len(postfix_string) != 0:
                        num_implied_or_to_add += 1
                    operator_stack.append(word[0])
                    open_parentheses += 1
                    word = word[1:]
                # if word[0] == '\"' and word[len(word) - 1] == '\"':
                #     word = word.replace("\"", "")
                # if word[0] == '\"' or word[len(word) - 1] == '\"':
                #     print(word)
                #     if len(operator_stack) == 0 and len(postfix_string) != 0:
                #         num_implied_or_to_add += 1
                #     open_quotes = not open_quotes
                #     if not open_quotes:
                #         postfix_string += (quote_word.replace("\"", "") + word.replace("\"", "") + " ")
                #         quote_word = ""
                #     else:
                #         quote_word += (word.replace("\"", "") + " ")
                if len(word) > 0:
                    if word[len(word) - 1] == ')':
                        word = word[:word.index(')')]
                        if len(word) > 0:
                            postfix_string += word + " "
                        open_parentheses -= 1
                        while operator_stack[-1] != '(':
                            postfix_string += operator_stack.pop() + " "
                        operator_stack.pop()
                    elif word == "and" or word == "or":
                        if open_parentheses == 0 and len(operator_stack) > 0:
                            postfix_string += operator_stack.pop() + " "
                        operator_stack.append(word)
                        word_check = 0  # TODO don't know where else needed
                    else:
                        postfix_string += word + " "
                        word_check += 1
                        if word_check >= 2:
                            postfix_string += "or "
            else:
                postfix_string += word + " "
                word_check += 1
                if word_check >= 2:
                    postfix_string += "or "
        while num_implied_or_to_add != 0:
            operator_stack.append("or")
            num_implied_or_to_add -= 1
        while len(operator_stack) > 0:
            if operator_stack[-1] == '(':
                operator_stack.pop()
            else:
                postfix_string += operator_stack.pop() + " "
        return postfix_string

    # TODO create function to make this more concise
    # TODO make * operator per-word
    # TODO does this need to be so wordy? Look into libraries/use Site more
    # TODO return some Sites based on categories, ask user for category of new Site
    # TODO quotes make many words one term
    # TODO NOT operator
    def create_results_set(self, results_set, user_input):
        """
        This function is called by search_keys and creates the actual results set used by search_keys to make the
        formatted return string. By using the - operator, the word will be added to a dictionary that is subtracted
        from the normal result set. This function calls send_to_helper.
        :param results_set: results_set is the dictionary sent by search_keys
        :param user_input: user_input is  also sent by search_keys and is used to check each word against the
        class-level's search_dictionary keys.
        :return: the results_set - excluded_from_results_set which is another dictionary populated by the user_input
        words which start with the - operator.
        """

        exclude_from_results_set = {}
        remove_flag_single_char = False
        if "or" in user_input or "and" in user_input:  # TODO undecided on if use different function
            stack = []  # TODO better name
            for word in self.clean_string(user_input).split(" "):
                if word == "or" or word == "and":  # TODO do we need 2 dicts for exclude/normal for each pop? - set?
                    dict_one = stack.pop()
                    dict_two = stack.pop()
                    if word == "and":
                        stack.append({key: dict_one[key] for key in dict_one if key in dict_two})
                    else:
                        stack.append(Counter(dict_one) + Counter(dict_two))
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
                        if word[len(word) - 1] == '*':
                            word = word[0:len(word) - 1]
                            for key in self.search_dictionary.keys():
                                if key.startswith(word):
                                    self.send_to_helper(results_set, exclude_from_results_set, key, remove_flag)
                        else:
                            if word in self.search_dictionary.keys():
                                self.send_to_helper(results_set, exclude_from_results_set, word, remove_flag)
                            else:
                                plural_str = self.__inflect_engine.plural(word)
                                singular_str = self.__inflect_engine.singular_noun(word)
                                if plural_str != word and plural_str in self.search_dictionary.keys():
                                    self.send_to_helper(results_set, exclude_from_results_set, plural_str, remove_flag)
                                elif singular_str != word and singular_str in self.search_dictionary.keys():
                                    self.send_to_helper(results_set, exclude_from_results_set, singular_str,
                                                        remove_flag)
        return {k: v for k, v in results_set.items() if k not in exclude_from_results_set}
        # return difference between results_set and exclude_from_results_set based on keys and not key-value pairs

    # TODO keep in mind, this might use more memory than a series of if-else statements in previous function.
    # TODO Speed tests showed similar results, but memory test is TBD
    def send_to_helper(self, results_set, exclude_from_results_set, key, remove_flag):
        """
        This function calls create_results_set_helper based on if the key starts with - or not.
        This is determined by remove_flag.
        :param results_set: The results_set dictionary sent by create_results_set (and before that, search_keys)
        :param exclude_from_results_set: The dictionary which is used to remove results from the results_set at the end
        in the create_results_set function. Items are added if remove_flag is true.
        :param key: Word to check against the class-level search_dictionary
        :param remove_flag: Whether the key initially had the - operator before it. Determines which dictionary the
        results are added to.
        :return: None
        """
        if remove_flag:
            self.create_results_set_helper(exclude_from_results_set, key, True)
        else:
            self.create_results_set_helper(results_set, key)

    # TODO doesn't need to do hits for exclude_results_set - maybe add parameter remove_flag
    def create_results_set_helper(self, results_set, key, remove_flag=False):
        """
        Populates the dictionary with the number of hits.
        :param results_set: results_set sent by send_to_helper, which came from create_results_set and initially from
        search_keys.
        :param key: Key to check against class-level search_dictionary
        :param remove_flag: remove_flag which determines whether to add extra data to results_set
        :return: None
        """
        if remove_flag:
            for tag in self.search_dictionary[key]:
                if tag not in results_set:
                    results_set[tag] = 1
        else:
            for tag in self.search_dictionary[key]:
                if tag in results_set:
                    results_set[tag] = results_set[tag] + 1
                else:
                    results_set[tag] = 1

    # TODO make this compatible with any stream so it can be used for server
    def write_to_file(self, file_name):
        """
        Writes the search_dictionary to a YAML file.
        :param file_name: file name for the YAML file.
        :return: None
        """
        try:
            with open(file_name, 'x+') as data_file:
                yaml.dump(self.search_dictionary, data_file)
        except FileExistsError:
            with open(file_name, 'w') as data_file:
                yaml.dump(self.search_dictionary, data_file)

    # TODO make this compatible with any stream so it can be used for server - python open makes stream?
    def populate_from_file(self, file_name):
        """
        Populates the class-level search_dictionary from a YAML file.
        :param file_name: file name for the YAML file.
        :return: Whether the file exists and loaded or not - True or False.
        """
        try:
            with open(file_name, 'r') as data_file:
                self.search_dictionary = yaml.load(data_file)
            return True
        except FileNotFoundError:
            return False
