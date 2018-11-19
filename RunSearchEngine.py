import SearchEngine
import time

# TODO takes long time, perhaps load into memory since WebScraper only needs to be in file for RPi
# TODO need to add robots.txt and sitemaps.xml
# TODO need to make it so webpage.com/blah#bleh is the same as webpage.com/blah
# TODO since they show up in list multiple times
if __name__ == "__main__":
    # print(NoSQLdb.retrieve_kv_site_db_dictionary('https://en.wikipedia.org/wiki/Category:Philosophers'))
    exit_flag = False
    print("mercado" in SearchEngine.search_dict)
    while not exit_flag:
        input_str = input("What would you like to search for?\nType exit to exit\n")
        if input_str.lower() == "exit":
            exit_flag = True
        else:
            # print(SearchEngine.interpret_input(input_str))
            start = time.time()
            output_str = SearchEngine.search_keys(input_str)
            # end = time.time()
            print(time.time() - start)
            if output_str is not None:
                print(output_str)
