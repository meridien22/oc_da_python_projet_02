import requests
from bs4 import BeautifulSoup
import csv
import re

# ● product_page_url
# ● category

def get_soup():
    reponse = requests.get(url)
    page = reponse.content
    # transforme (parse) le HTML en objet BeautifulSoup
    return BeautifulSoup(page, "html.parser")

def get_detail(soup):
    resultat = []
    elements = soup.find_all("tr")
    for element in elements:
        titre = element.find("th")
        description = element.find("td")
        if titre.text in good_header:
            resultat.append(description.text)
    return resultat

def get_title(soup):
    element = soup.find("h1")
    return element.text

def get_product_description(soup):
    element = soup.find("p", attrs={'class': False})
    return element.text

def get_product_description(soup):
    element = soup.find("p", attrs={'class': False})
    return element.text

def get_image_url(soup):
    element = soup.find("div", class_="item active")
    image = element.find("img")
    return image["src"]

def write_csv(resultats):
    en_tete = [
        "universal_product_code",
        "price_excluding_tax",
        "price_including_tax",
        "number_available",
        "review_rating",
        "title",
        "image_url",
        "product_description"
    ]
    with open(".\\data\\produits.csv", "w", newline="", encoding='utf-8') as fichier_csv:
        writer = csv.writer(fichier_csv, delimiter=",")
        writer.writerow(en_tete)
        for resultat in resultats:
            writer.writerow(resultat)

if __name__ == "__main__":
    # initialisation des variables
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    headers = []
    resultat = []
    resultats = []
    good_header = {
        "UPC": "universal_product_code",
        "Price (excl. tax)":  "price_excluding_tax",
        "Price (incl. tax)":  "price_including_tax",
        "Availability": "number_available",
        "Number of reviews": "review_rating"
    }

    soup = get_soup()
    resultat.extend(get_detail(soup))
    resultat.append(get_title(soup))
    resultat.append(get_image_url(soup))
    resultat.append(get_product_description(soup))
    resultat[3] = re.findall(r'\d+', resultat[3])[0]
    resultats.append(resultat)
    write_csv(resultats)