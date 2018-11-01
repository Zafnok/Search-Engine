import operator
import inflect


# TODO check variable names, some are bad
# TODO add NOT/AND/OR
class SearchEngine:
    searchDictionary = {}
    inflect_engine = inflect.engine()

    @staticmethod
    def order_dictionary(dictionary):
        return sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)

    def add_to_dictionary(self, tags, data):
        for tag in tags:
            if tag in self.searchDictionary:
                self.searchDictionary[tag].add(data)
            else:
                self.searchDictionary[tag] = {data}

    def search_keys(self, user_input):
        results = {}
        results = self.create_results_set(results, user_input)
        results = self.order_dictionary(results)
        if len(results) == 0:
            temp_str = input("Search returned zero results\nWhat were you searching for?\nType "
                             "None if you don't want to add to the engine.\n")
            if not temp_str.lower().strip() == "none":
                self.add_to_dictionary(user_input.strip().split(" "), temp_str)
        else:
            return_str = ""
            for pair in results:
                return_str += (pair[0] + " - hits: " + str(pair[1]) + "\n")
            return return_str

    # TODO create function to make this more concise

    def create_results_set(self, results_set, user_input):
        exclude_from_results_set = {}
        if user_input[len(user_input) - 1] == '*':
            for key in self.searchDictionary.keys():
                remove_flag = False
                try:
                    last_word = user_input[user_input.rindex(" ") + 1:len(user_input) - 1]
                    if last_word[0] == '-':
                        last_word = last_word[1:]
                        remove_flag = True
                    if key.startswith(last_word):
                        if remove_flag:
                            self.create_results_set_helper(exclude_from_results_set, key)
                        else:
                            self.create_results_set_helper(results_set, key)
                except ValueError:
                    last_word = user_input
                    if last_word[0] == '-':
                        remove_flag = True
                        last_word = last_word[1:]
                    if key.startswith(last_word):
                        if remove_flag:
                            self.create_results_set_helper(exclude_from_results_set, key)
                        else:
                            self.create_results_set_helper(results_set, key)
            last_index_of_space = user_input.rfind(" ")
            if last_index_of_space != -1:
                user_input = user_input[0:last_index_of_space]
        for key in user_input.split(" "):
            remove_flag = False
            word = key
            if word[0] == '-':
                remove_flag = True
                word = word[1:]
            if word in self.searchDictionary.keys():
                if remove_flag:
                    self.create_results_set_helper(exclude_from_results_set, word)
                else:
                    self.create_results_set_helper(results_set, word)
            else:
                plural_str = self.inflect_engine.plural(word)
                singular_str = self.inflect_engine.singular_noun(word)
                if plural_str != word and plural_str in self.searchDictionary.keys():
                    if remove_flag:
                        self.create_results_set_helper(exclude_from_results_set, plural_str)
                    else:
                        self.create_results_set_helper(results_set, plural_str)
                elif singular_str != word and singular_str in self.searchDictionary.keys():
                    if remove_flag:
                        self.create_results_set_helper(exclude_from_results_set, singular_str)
                    else:
                        self.create_results_set_helper(results_set, singular_str)
        print(str(dict(results_set.items() - exclude_from_results_set.items())) + " " + str(
            exclude_from_results_set) + " " + str(results_set))
        return dict(results_set.items() - exclude_from_results_set.items())

    def create_results_set_helper(self, results_set, key):
        for tag in self.searchDictionary[key]:
            if tag in results_set:
                results_set[tag] = results_set[tag] + 1
            else:
                results_set[tag] = 1

    def write_to_file(self, file_name):
        try:
            with open(file_name, 'x+') as dataFile:
                for key, value in self.searchDictionary.items():
                    dataFile.write(key + " ")
                    dataFile.write(", ".join(value))
                    dataFile.write("\n")
        except FileExistsError:
            with open(file_name, 'w') as dataFile:
                for key, value in self.searchDictionary.items():
                    dataFile.write(key + " ")
                    dataFile.write(", ".join(value))
                    dataFile.write("\n")

    def populate_from_file(self, file_name):
        try:
            with open(file_name, 'r') as dataFile:
                for line in dataFile:
                    line = line.strip("\n")
                    self.add_to_dictionary({line[0:line.index(" ")]}, line[line.index(" ") + 1:])
        except FileNotFoundError:
            return False


def main():
    search_engine = SearchEngine()
    if not search_engine.populate_from_file('dataFile.txt'):
        search_engine.add_to_dictionary({'gaming', 'news', 'media', 'ign', 'games', 'ps4'}, 'ign gaming news')
        search_engine.add_to_dictionary({'cars', 'ford', 'toyota', 'honda'}, 'carmax')
        search_engine.add_to_dictionary({'jobs', 'careers', 'internships'}, 'indeed')
    exit_flag = False
    while not exit_flag:
        input_str = input("What would you like to search for?\nType exit to exit\n")
        if input_str.lower() == "exit":
            exit_flag = True
        else:
            output_str = search_engine.search_keys(input_str)
            if output_str is not None:
                print(output_str)
    search_engine.write_to_file("dataFile.txt")


main()
