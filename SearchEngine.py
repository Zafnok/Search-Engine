import os.path


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
        if userInput[len(userInput) - 1] == '*':
            for key in self.searchDictionary.keys():
                if key.startswith(userInput[0:len(userInput) - 1], 0, len(key)):
                    results = self.createResultsSet(key, results)
        else:
            for key in userInput.split():
                if key in self.searchDictionary:
                    results = self.createResultsSet(key, results)
        if len(results) == 0:
            tempStr = input("Search returned zero results\nWhat were you searching for?\n")
            self.addToDictionary(userInput.split(), tempStr)
        else:
            returnStr = ""
            for key, value in results.items():
                returnStr += (key + " - hits: " + str(value) + "\n")
            return returnStr

    def createResultsSet(self, key, set):
        for tag in self.searchDictionary[key]:
            if tag in set:
                set[tag] = set[tag] + 1
            else:
                set[tag] = 1
        return set

    def writeToFile(self, fileName):
        try:
            with open(fileName, 'x+') as dataFile:
                for key, value in self.searchDictionary.items():
                    dataFile.write(key + " ")
                    for data in value:
                        dataFile.write(data + " ")
                    dataFile.write("\n")
        except FileExistsError:
            with open(fileName, 'r+') as dataFile:
                for key, value in self.searchDictionary.items():
                    dataFile.write(key + " ")
                    for data in value:
                        dataFile.write(data + " ")
                    dataFile.write("\n")

    def populateFromFile(self, fileName):
        try:
            with open(fileName, 'r') as dataFile:
                for line in dataFile:
                    line = line.strip("\n")
                    self.addToDictionary(line[0:line.index(" ")], line[line.index(" ") + 1:])
        except FileNotFoundError:
            return False


def main():
    searchengine = SearchEngine()
    searchengine.addToDictionary({'gaming', 'news', 'media', 'ign', 'games', 'ps4'}, 'ign gaming news')
    searchengine.addToDictionary({'cars', 'ford', 'toyota', 'honda'}, 'carmax')
    searchengine.addToDictionary({'jobs', 'careers', 'internships'}, 'indeed')
    exitFlag = False
    while not exitFlag:
        str = input("What would you like to search for?\nType exit to exit\n")
        if str.lower() == "exit":
            exitFlag = True
        else:
            print(searchengine.searchKeys(str))
    searchengine.writeToFile("dataFile.txt")


main()
