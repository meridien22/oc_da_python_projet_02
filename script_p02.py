import requests
from bs4 import BeautifulSoup
import csv
import re

# ● product_page_url
# ● product_description
# ● category
# ● image_url

def extraire():
    reponse = requests.get(url)
    page = reponse.content
    # transforme (parse) le HTML en objet BeautifulSoup
    return BeautifulSoup(page, "html.parser")

def transformer1(soup):
    elements = soup.find_all("tr")
    for element in elements:
        titre = element.find("th")
        description = element.find("td")
        if titre.text in good_header:
            resultats.append(description.text)

def transformer2(soup):
    element = soup.find("h1")
    resultats.append(element.text)

def transformer3(soup):
    element = soup.find("p", attrs={'class': False})
    resultats.append(element.text)

if __name__ == "__main__":
    # initialisation des variables
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    delimiter = ","
    headers = []
    resultats = []
    good_header = {
    "UPC": "universal_product_code",
    "Price (excl. tax)":  "price_excluding_tax",
    "Price (incl. tax)":  "price_including_tax",
    "Availability": "number_available",
    "Number of reviews": "review_rating"
    }

    soup = extraire()
    transformer1(soup)
    transformer2(soup)
    transformer3(soup)
    resultats[3] = re.findall(r'\d+', resultats[3])[0]
    print(resultats)