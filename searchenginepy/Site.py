class Site:
    """
    This class is a data element for SearchEngine. It holds a site name and a site category, both being strings.
    """

    def __init__(self, site_name=None, relevancy_dictionary=None, time_since_scrape=0):
        """
        Constructor for Site.
        :param site_name: Name of site.
        :param relevancy_dictionary: Dictionary holding tags and their assigned relevancy values
        """
        self.site_name = site_name
        self.relevancy_dictionary = relevancy_dictionary if relevancy_dictionary is not None else dict()
        self.time_since_scrape = time_since_scrape

    def get_time_since_scrape(self):
        return self.time_since_scrape

    def get_site_name(self):
        """
        :return: site_name or "None" if it does not exist
        """
        if self.site_name is None:
            return "None"
        else:
            return self.site_name

    def __str__(self):
        """
        :return: get_site_name
        """
        return self.get_site_name()

    # TODO fix this or remove
    def __repr__(self):
        """
        :return: get_site_name: get_category
        """
        return self.get_site_name() + ": " + self.get_category()
