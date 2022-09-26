import pandas as pd
from bs4 import BeautifulSoup
import requests
from owlready2 import *
import types


# function to scrape from Wikipedia
def scrapeWiki():
    pageWiki = requests.get("https://en.wikipedia.org/wiki/List_of_planet_types")
    soupWiki = BeautifulSoup(pageWiki.content, "html.parser")

    # getting classes based on span and class
    headingWiki = soupWiki.findAll('span', {'class': "mw-headline"})
    headingListWiki = []

    # iterating over obtained result from above to clean the text and adding it to a list
    for i in headingWiki:
        headingListWiki.append(i.get_text().replace("By", "").lower())
    del headingListWiki[4:]

    # getting subclasses from the table in wiki
    planetTableWiki = soupWiki.findAll('table', {'class': "wikitable"})

    # converting obtained table of subclasses into dataframe
    dfPlanetWiki = pd.read_html(str(planetTableWiki))

    # creating dictionary of class and subclasses
    listSize = len(headingListWiki)
    finalPlanetWiki = {}
    count = 0

    while count < listSize:
        df = pd.DataFrame(dfPlanetWiki[count])
        planetType = headingListWiki[count]
        planetList = df["Planet type"].tolist()
        finalPlanetWiki.update({planetType: planetList})
        count = count + 1

    # creating dataframe from dict and converting to csv
    planetDfWiki = pd.DataFrame(finalPlanetWiki.items(), columns=["class", "subclasses"])
    print("**********Planet Classification From Wikipedia**********")
    print(planetDfWiki)
    planetDfWiki.to_csv("planetFromWiki.csv", index=False)
    return planetDfWiki


# function to scrape from Len Academy
def scrapeLenAcademy():
    page = requests.get(
        "https://www.len.com.ng/csblogdetail/421/Classification-and-types-of-planets-with-their-characteristics")
    soup = BeautifulSoup(page.content, "html.parser")

    # get main classes from different tags
    planetHeading = soup.findAll('h4' and 'strong')
    classList = []

    # cleaning the data obtained and putting them in a list
    for i in planetHeading:
        textLine = i.get_text()
        if textLine.startswith("B"):
            classList.append(textLine.replace("By", "").replace("their", "").lower())

    # get subclasses based on tags span and u
    planetType = soup.findAll('span' and 'u')
    subClassList = []

    # cleaning the obtained data and putting them in a list
    for i in planetType:
        textLine = i.get_text()
        if "Planet" in textLine:
            subClassList.append(textLine.replace(":", "").split(' or ')[-1])
    del subClassList[0]

    # dict for class and subclass
    planetList = {}
    startIndex = 0
    for i in classList:
        planetList.update({i: subClassList[startIndex: startIndex + 2]})
        startIndex = startIndex + 2

    # making dataframe and csv
    planetDf = pd.DataFrame(planetList.items(), columns=["class", "subclasses"])
    print("\n**********Planet Classification from Len Academy**********")
    print(planetDf)
    planetDf.to_csv("planetFromPlainText.csv", index=False)
    return planetDf


# aggregating dataframe from two different links
def dataAggregation():
    planetType = {}
    planetWiki = scrapeWiki()
    planetLenAcademy = scrapeLenAcademy()

    # iterating over the dataframes
    for indexWiki, rowWiki in planetWiki.iterrows():
        for indexLen, rowLen in planetLenAcademy.iterrows():
            wiki = rowWiki['class'].split()
            lenAca = rowLen['class'].split()

            # checking if similar classes exist in two dataframes; if yes then combining the list of subclasses
            if any(x in wiki for x in lenAca):
                planetSubclass = rowWiki['subclasses'] + rowLen['subclasses']
                planetType.update({rowWiki['class']: planetSubclass})

    # newdf with combined subclasses
    newdf = pd.DataFrame(planetType.items(), columns=["class", "subclasses"])
    # print(newdf)

    # appending all the dataframes
    # dropped rows in index 0 and 2 because it overlaps with the updated rows
    # dropped row in index 3 because of unwanted result
    concatdf = newdf.append(planetWiki.drop([0, 2, 3]))

    # dropped rows in index 0 and 5 because it overlaps with the updated rows
    finaldf = concatdf.append(planetLenAcademy.drop([0, 5]))
    print("\n**********Final Planet Classification**********")
    print(finaldf)
    finaldf.to_csv("FinalPlanetClassification.csv", index=False)
    return finaldf


# function to add new classes and subclasses into the existing ontology.
def dfToOwl(df):
    # loading the existing owl file
    onto = get_ontology("astronomyRdf.owl").load()

    # iterating over every class in the existing ontology until we find class "Planet"
    for i in list(onto.classes()):
        if i.name == "Planet":

            # interating over the dataframe we created before and adding them to our ontology
            for index, row in df.iterrows():
                with onto:
                    mainClass = row['class'].strip().replace(" ", "_")
                    subClass = row["subclasses"]  # list of subclasses

                    # "mainClass" will be the subclass of Planet and is stored as "newClass"
                    newClass = types.new_class(mainClass, (i,), {})

                    # iterating over the list of subclasses from the dataframe
                    # and adding them to the existing mainClass as a subclass
                    for j in subClass:

                        # "newSubClass" will be the subclass of "newClass"
                        newSubClass = types.new_class(j.replace(" ", "_"), (newClass,), {})
            break

    # saving as a new ontology file.
    onto.save(file="astronomyRdfUpdated.owl", format="rdfxml")


# Calling the data aggregation function
# and then calling the function to create the ontology file
df = dataAggregation()
dfToOwl(df)
