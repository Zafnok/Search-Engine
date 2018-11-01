import operator
import inflect


class SearchEngine:
    searchDictionary = {}
    inflect_engine = inflect.engine()

    def add_to_dictionary(self, tags, data):
        for tag in tags:
            plural_str = self.inflect_engine.plural(tag)
            singular_str = self.inflect_engine.singular_noun(tag)
            if tag in self.searchDictionary:
                self.searchDictionary[tag].add(data)
                if plural_str != tag:
                    self.searchDictionary[plural_str].add(data)
                if singular_str != tag:
                    self.searchDictionary[singular_str].add(data)
            else:
                self.searchDictionary[tag] = {data}
                if plural_str != tag:
                    self.searchDictionary[plural_str] = {data}
                if singular_str != tag:
                    self.searchDictionary[singular_str] = {data}

    def search_keys(self, user_input):
        results = {}
        if user_input[len(user_input) - 1] == '*':
            results = self.create_results_set(results, True, user_input)
        else:
            results = self.create_results_set(results, False, user_input)
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

    @staticmethod
    def order_dictionary(dictionary):
        return sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)

    def create_results_set_helper(self, results_set, key):
        for tag in self.searchDictionary[key]:
            if tag in results_set:
                results_set[tag] = results_set[tag] + 1
            else:
                results_set[tag] = 1

    def create_results_set(self, results_set, star_present, user_input):
        if star_present:
            for key in self.searchDictionary.keys():
                if key.startswith(user_input[0:len(user_input) - 1], 0, -1):
                    self.create_results_set_helper(results_set, key)
        else:
            for key in user_input.split(" "):
                if key in self.searchDictionary.keys():
                    self.create_results_set_helper(results_set, key)
        return results_set

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
