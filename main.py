import pandas as pd
from bs4 import BeautifulSoup
import requests
from owlready2 import *
import rdfpandas

def scrapeWiki():
    pageWiki = requests.get("https://en.wikipedia.org/wiki/List_of_planet_types")
    soupWiki = BeautifulSoup(pageWiki.content, "html.parser")

    # getting classes
    headingWiki = soupWiki.findAll('span', {'class': "mw-headline"})
    headingListWiki = []

    for i in headingWiki:
        headingListWiki.append(i.get_text().replace("By", "").lower())
    del headingListWiki[4:]

    # getting subclasses
    planetTableWiki = soupWiki.findAll('table', {'class': "wikitable"})
    dfPlanetWiki = pd.read_html(str(planetTableWiki))

    # creating dictionary
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
    # print(planetDfWiki)
    planetDfWiki.to_csv("planet.csv", index=False)
    return planetDfWiki


def scrapeLenAcademy():
    page = requests.get(
        "https://www.len.com.ng/csblogdetail/421/Classification-and-types-of-planets-with-their-characteristics")
    soup = BeautifulSoup(page.content, "html.parser")

    # get main classes
    planetHeading = soup.findAll('h4' and 'strong')
    classList = []
    for i in planetHeading:
        textLine = i.get_text()
        if textLine.startswith("B"):
            classList.append(textLine.replace("By", "").replace("their", "").lower())

    # print(classList)

    # get subclasses
    planetType = soup.findAll('span' and 'u')
    subClassList = []
    # print(planetType)
    for i in planetType:
        textLine = i.get_text()
        if "Planet" in textLine:
            subClassList.append(textLine.replace(":", "").split(' or ')[-1])
    del subClassList[0]
    # print(subClassList)

    # dict for class and subclass
    planetList = {}
    startIndex = 0
    for i in classList:
        planetList.update({i: subClassList[startIndex: startIndex + 2]})
        startIndex = startIndex + 2

    # making dataframe and csv
    planetDf = pd.DataFrame(planetList.items(), columns=["class", "subclasses"])
    # print(planetDf)
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

    # appending all the dataframes
    concatdf = newdf.append(planetWiki.drop([0, 2]))
    finaldf = concatdf.append(planetLenAcademy.drop([0, 5]))
    print(finaldf)
    finaldf.to_csv("FinalPlanetClassification.csv", index=False)
    return finaldf


dataAggregation()

