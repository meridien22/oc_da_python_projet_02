import requests
import csv
import re
import os
import uuid
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

def get_soup(url):
    reponse = requests.get(url)
    page = reponse.content
    return BeautifulSoup(page, "html.parser")

def get_categorys(categorys, soup, url, root):
    element = soup.find("ul", attrs = {'class': False})
    elements = element.find_all("li", attrs = {'class': False})
    for element in elements:
        category = {}
        link = element.find("a")
        href = link["href"]
        name = link.text.strip()
        category["name"] = name
        category["url"] = urljoin(url, href)
        category["directory"] = os.path.join(root, name)
        category["url_books"] = get_url_books(category["url"])
        categorys.append(category)
    return categorys

def get_root():
    now = datetime.now()
    date_time = now.strftime("%y%m%d")
    directory = f"BTS_{date_time}_{uuid.uuid4()}"
    return os.path.join(".", "data", directory)

def create_directorys(root, categorys):
    os.makedirs(root)
    for category in categorys:
        os.makedirs(category["directory"])
        os.makedirs(os.path.join(category["directory"], "img"))

def get_next(soup, url):
    element = soup.find("li", class_ = "next")
    href = element.find("a").get("href")
    return urljoin(url, href)

def get_url_books(url):
    next_present = True
    url_books = []
    while next_present:
        soup = get_soup(url)
        books = soup.find_all("li", class_ = "col-xs-6 col-sm-4 col-md-3 col-lg-3")
        for book in books:
            href = book.find("a").get("href")
            url_books.append(urljoin(url, href))
        next_present = soup.find("li", class_ = "next")
        if next_present:
            url = get_next(soup, url)
    return url_books

def get_string_from_hint(soup, hint):
    element = soup.find("th", string = hint)
    return element.find_next_sibling('td').text

def get_float_from_hint(soup, hint):
    value = get_string_from_hint(soup, hint)
    return re.findall(r'\d+\.*\d*', value)[0]

def get_int_from_hint(soup, hint):
    value = get_string_from_hint(soup, hint)
    return re.findall(r'\d+', value)[0]

def get_title(soup):
    element = soup.find("h1")
    return element.text

def get_image_url(soup, url):
    element = soup.find("div", class_="item active")
    img = element.find("img")
    return urljoin(url, img["src"])

def get_product_description(soup):
    element = soup.find("p", attrs={'class': False})
    if element:
        return element.text
    else:
        return ""

def download_img(url, dir, upc):
    reponse = requests.get(url)
    with open(os.path.join(dir, "img", f"{upc}.jpg"), 'wb') as fichier:
        fichier.write(reponse.content)

def write_csv(resultats, dir, name_category, en_tete):
    file_name = f"{name_category}.csv"
    with open(os.path.join(dir, file_name), "w", newline="", encoding='utf-8') as fichier_csv:
        writer = csv.writer(fichier_csv, delimiter=",")
        writer.writerow(en_tete)
        for resultat in resultats:
            writer.writerow(resultat)

if __name__ == "__main__":
    # url de base du site
    url_base = "https://books.toscrape.com/index.html"
    # dossier racine qui va stocker les fichiers téléchargés
    root = get_root()
    # liste qui va stocker les url, les noms et les dossiers des catégories
    categorys = []
    # en-tête du fichier csv
    en_tete = [
        "universal_product_code",
        "title",
        "category",
        "price_excluding_tax",
        "price_including_tax",
        "number_available",
        "review_rating",
        "product_page_url",
        "product_description",
        "image_url"
    ]

    soup_base = get_soup(url_base)
    categorys = get_categorys(categorys,soup_base, url_base, root)
    directorys = create_directorys(root, categorys)
    for category in categorys:
        resultats = []
        for url in category["url_books"]:
            resultat = []
            soup = get_soup(url)
            resultat.append(get_string_from_hint(soup, "UPC"))
            resultat.append(get_title(soup))
            resultat.append(category["name"])
            resultat.append(get_float_from_hint(soup, "Price (excl. tax)"))
            resultat.append(get_float_from_hint(soup, "Price (incl. tax)"))
            resultat.append(get_int_from_hint(soup, "Availability"))
            resultat.append(get_string_from_hint(soup, "Number of reviews"))
            resultat.append(url)
            resultat.append(get_product_description(soup))
            img_url = get_image_url(soup, url)
            resultat.append(img_url)
            download_img(img_url, category["directory"], resultat[0])
            resultats.append(resultat)
        write_csv(resultats, category["directory"], category["name"], en_tete)