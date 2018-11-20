import NoSQLdb
import os  # for making dir if doesn't exist and getting paths

"""
Author: Nicholas Wentz
This module contains a function to generate HTML from the results of a search
"""


def generate_html(user_input, results_dict):
    """
    This function takes the user input string and results dictionary, and uses them to generate an HTML file with the
    results
    :param user_input: user input string for the file to be named after
    :param results_dict: dictionary of results for the HTML page to be ordered and displayed
    :return: None
    """
    # print(results_dict)
    html_file_name = os.path.join(os.path.dirname(__file__),
                                  r"webpages\results_for_{}.html".format(user_input.replace(" ", "_")))
    print(os.path.dirname(__file__))
    print(html_file_name)
    os.makedirs(os.path.dirname(html_file_name), exist_ok=True)
    with open(html_file_name, 'w+', encoding="utf8") as html_file:
        html_file.write("<!DOCTYPE html>\n")
        html_file.write("<meta charset=\"UTF-8\"/>")
        html_file.write("<html lang=\"en\">\n")
        html_file.write("<title>Search Results</title>\n")
        html_file.write("<body>\n")
        html_file.write("<ul style=\"list-style: none;\">\n")  # makes a list without bullets
        for item in results_dict:
            html_file.write(
                u"<li><a href=\"{0}\">{1}</a></li>\n".format(item[0], NoSQLdb.retrieve_kv_site_db_title(
                    item[0])))  # displays the items with their names as their HTML title tags
        html_file.write("</ul>\n")
        html_file.write("</body>\n")
        html_file.write("</html>\n")
