class SearchEngine:

    searchDictionary = {}

    def addToDictionary(self, tags, data):

        for tag in tags:
            if tag in self.searchDictionary:
                self.searchDictionary[tag].append(data)
            else:
                self.searchDictionary[tag] = {data}


    def searchKeys(self, userInput):

        results = {}
        for key in userInput.split():
            if key in self.searchDictionary:
                for tag in self.searchDictionary[key]:
                    if tag in results:
                        results[tag] = results[tag]+1
                    else:
                        results[tag] = 1
        if len(results)==0:
            tempStr = input("Search returned zero results\nWhat were you searching for?\n")
            self.addToDictionary(userInput.split(), tempStr)

        else:
            returnStr = ""
            for key, value in results.items():
                returnStr += (key+" - hits: "+str(value)+"\n")
            return returnStr


def main():
    dataFile = open('dataFile', 'r+')
    if(dataFile.)
    searchengine = SearchEngine()
    searchengine.addToDictionary({'gaming', 'news', 'media', 'ign', 'games', 'ps4'}, 'ign gaming news')
    searchengine.addToDictionary({'cars', 'ford', 'toyota', 'honda'}, 'carmax')
    searchengine.addToDictionary({'jobs', 'careers', 'internships'}, 'indeed')
    exitFlag = False
    while not exitFlag:
        str = input("What would you like to search for?\nType exit to exit\n")
        if str.lower()=="exit":
            exitFlag=True
        else:
            print(searchengine.searchKeys(str))


main()



