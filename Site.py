class Site:
    def __init__(self, site_name=None, site_category=None):
        self.site_name = site_name
        self.site_category = site_category

    def get_category(self):
        if self.site_category is None:
            return "None"
        else:
            return self.site_category

    def get_site_name(self):
        if self.site_name is None:
            return "None"
        else:
            return self.site_name

    def __str__(self):
        return self.get_site_name()

    def __repr__(self):
        return self.get_site_name() + ": " + self.get_category()
