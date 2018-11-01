import operator
import inflect


# TODO check variable names, some are bad
# TODO add NOT/AND/OR
# TODO add functionality to write on close
class SearchEngine:
    search_dictionary = {}
    inflect_engine = inflect.engine()

    @staticmethod
    def order_dictionary(dictionary):
        return sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)

    def add_to_dictionary(self, tags, data):
        for tag in tags:
            if tag in self.search_dictionary:
                self.search_dictionary[tag].add(data)
            else:
                self.search_dictionary[tag] = {data}

    def search_keys(self, user_input):
        results = {}
        if len(user_input.strip()) > 0:
            results = self.create_results_set(results, user_input)
            results = self.order_dictionary(results)
            if len(results) == 0:
                new_tag_str = input("Search returned zero results\nWhat were you searching for?\nType "
                                    "None if you don't want to add to the engine.\n")
                if not new_tag_str.lower().strip() == "none":
                    self.add_to_dictionary(user_input.strip().split(" "), new_tag_str)
            else:
                return_str = ""
                for pair in results:
                    return_str += (pair[0] + " - hits: " + str(pair[1]) + "\n")
                return return_str
        else:
            return "Invalid input, please try again."

    # TODO create function to make this more concise

    def create_results_set(self, results_set, user_input):
        exclude_from_results_set = {}
        if user_input[len(user_input) - 1] == '*':
            remove_flag = False
            try:
                last_word = user_input[user_input.rindex(" ") + 1:len(user_input) - 1]
                if last_word[0] == '-':
                    last_word = last_word[1:]
                    remove_flag = True
            except ValueError:
                last_word = user_input[0:len(user_input) - 1]
                if last_word[0] == '-':
                    remove_flag = True
                    last_word = last_word[1:]
            for key in self.search_dictionary.keys():
                if key.startswith(last_word):
                    self.send_to_helper(results_set, exclude_from_results_set, key, remove_flag)
            last_index_of_space = user_input.rfind(" ")
            if last_index_of_space != -1:
                user_input = user_input[0:last_index_of_space]
        for key in user_input.split(" "):
            remove_flag = False
            word = key
            if word[0] == '-':
                remove_flag = True
                word = word[1:]
            if word in self.search_dictionary.keys():
                self.send_to_helper(results_set, exclude_from_results_set, key, remove_flag)
            else:
                plural_str = self.inflect_engine.plural(word)
                singular_str = self.inflect_engine.singular_noun(word)
                if plural_str != word and plural_str in self.search_dictionary.keys():
                    self.send_to_helper(results_set, exclude_from_results_set, plural_str, remove_flag)
                elif singular_str != word and singular_str in self.search_dictionary.keys():
                    self.send_to_helper(results_set, exclude_from_results_set, singular_str, remove_flag)
        return dict(results_set.items() - exclude_from_results_set.items())

    def send_to_helper(self, results_set, exclude_from_results_set, key, remove_flag):
        if remove_flag:
            self.create_results_set_helper(exclude_from_results_set, key)
        else:
            self.create_results_set_helper(results_set, key)

    def create_results_set_helper(self, results_set, key):
        for tag in self.search_dictionary[key]:
            if tag in results_set:
                results_set[tag] = results_set[tag] + 1
            else:
                results_set[tag] = 1

    def write_to_file(self, file_name):
        try:
            with open(file_name, 'x+') as data_file:
                self.write_helper(data_file)
        except FileExistsError:
            with open(file_name, 'w') as data_file:
                self.write_helper(data_file)

    def write_helper(self, data_file):
        for key, value in self.search_dictionary.items():
            data_file.write(key + " ")
            data_file.write(", ".join(value))
            data_file.write("\n")

    def populate_from_file(self, file_name):
        try:
            with open(file_name, 'r') as data_file:
                for line in data_file:
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
