from SearchEngineCopyCopy import SearchEngine
from Site import Site
# import time

if __name__ == "__main__":
    search_engine = SearchEngine()
    if not search_engine.loaded:
        search_engine.add_to_dictionary({'gaming', 'news', 'media', 'ign', 'games', 'ps4'},
                                        Site('ign gaming news', 'gaming'))
        search_engine.add_to_dictionary({'cars', 'ford', 'toyota', 'honda'}, Site('carmax', 'cars'))
        search_engine.add_to_dictionary({'jobs', 'careers', 'internships'}, Site('indeed', 'jobs'))
    exit_flag = False
    while not exit_flag:
        input_str = input("What would you like to search for?\nType exit to exit\n")
        if input_str.lower() == "exit":
            exit_flag = True
        else:
            print(search_engine.interpret_input(input_str))
            # start = time.time()
            # output_str = search_engine.search_keys(input_str)
            # end = time.time()
            # print(end - start)
            # if output_str is not None:
            #     print(output_str)
