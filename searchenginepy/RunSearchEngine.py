import SearchEngine
import time
import sys

# TODO need to add robots.txt and sitemaps.xml - robots.txt should be done, still need sitemaps.xml
if __name__ == "__main__":
    # print(NoSQLdb.retrieve_kv_site_db_dictionary('https://en.wikipedia.org/wiki/Category:Philosophers'))
    exit_flag = False
    SearchEngine.initialize_dicts()
    while not exit_flag:
        try:
            input_str = input("What would you like to search for?\nType exit to exit\n")
            if input_str.lower() == "exit":
                exit_flag = True
            else:
                # print(SearchEngine.interpret_input(input_str))
                start = time.time()
                SearchEngine.search_keys(input_str)
                # output_str = SearchEngine.search_keys(input_str)
                # end = time.time()
                print(time.time() - start)
                # if output_str is not None:
                #     print(output_str)
        except KeyboardInterrupt:
            sys.exit()
