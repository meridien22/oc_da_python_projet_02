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
    # transforme (parse) le HTML en objet BeautifulSoup
    return BeautifulSoup(page, "html.parser")

def get_href_book(soup, url_base):
    tab_url = []
    elements = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")
    for element in elements:
        href = element.find("a").get("href")
        tab_url.append(urljoin(url_base, href))
    return tab_url

def get_detail(soup):
    resultat = []
    elements = soup.find_all("tr")
    for element in elements:
        titre = element.find("th")
        description = element.find("td")
        if titre.text in good_field:
            resultat.append(description.text)
    return resultat

def get_title(soup):
    element = soup.find("h1")
    return element.text

def get_product_description(soup):
    element = soup.find("p", attrs={'class': False})
    if element:
        return element.text
    else:
        return ""

def get_image_url(soup, url):
    element = soup.find("div", class_="item active")
    img = element.find("img")
    return urljoin(url, img["src"])

def test_next(soup):
    element = soup.find("li", class_="next")
    if element:
        return True
    else:
        return False

def get_next(soup, url):
    element = soup.find("li", class_="next")
    href = element.find("a").get("href")
    return urljoin(url, href)

def get_category(soup, url_base):
    tab = []
    element = soup.find("ul", attrs={'class': False})
    elements = element.find_all("li", attrs={'class': False})
    for element in elements:
        link = element.find("a")
        href = link["href"]
        category = link.text.strip()
        tab.append((category, urljoin(url_base, href)))
    return tab

def create_directory():
    directory = {}
    now = datetime.now()
    date_time = now.strftime("%Y%m%d_%Hh%Mm%Ss")
    directory["root"] = os.path.join(".", "data", f"Books_to_Scrape_{date_time}_{uuid.uuid4()}")
    directory["csv"] = os.path.join(directory["root"], "csv")
    directory["img"] = os.path.join(directory["root"], "img")
    for cle in directory:
        os.makedirs(directory[cle])
    return directory

def download_img(url, dir, upc):
    reponse = requests.get(url)
    with open(os.path.join(dir, f"{upc}.jpg"), 'wb') as fichier:
        fichier.write(reponse.content)

def write_csv(resultats, dir, name_category):
    en_tete = [
        "universal_product_code",
        "price_excluding_tax",
        "price_including_tax",
        "number_available",
        "review_rating",
        "title",
        "image_url",
        "product_description",
        "product_page_url",
        "category"
    ]
    file_name = f"{name_category}.csv"
    with open(os.path.join(dir, file_name), "w", newline="", encoding='utf-8') as fichier_csv:
        writer = csv.writer(fichier_csv, delimiter=",")
        writer.writerow(en_tete)
        for resultat in resultats:
            writer.writerow(resultat)

if __name__ == "__main__":
    # initialisation des variables
    # url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    # url_base = "https://books.toscrape.com/catalogue/category/books/fiction_10/index.html"
    # url_base = "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html"
    # url_base = "https://books.toscrape.com/catalogue/category/books/travel_2/index.html"
    url_base = "https://books.toscrape.com/index.html"
    good_field = ["UPC","Price (excl. tax)","Price (incl. tax)","Availability","Number of reviews"]

    directory = create_directory()

    soup_base = get_soup(url_base)
    categorys = get_category(soup_base,url_base)
    for category in categorys:
        print(category)
        category_name = (category[0])
        category_url = (category[1])
        resultats = []
        next_present = True
        directory["category_img"] = os.path.join(directory["img"], category_name)
        os.makedirs(directory["category_img"])
        while next_present :
            category_soup = get_soup(category_url)
            for url in get_href_book(category_soup,category_url):
                print(url)
                resultat = []
                soup = get_soup(url)
                resultat.extend(get_detail(soup))
                resultat.append(get_title(soup))
                img_url = get_image_url(soup, url)
                resultat.append(img_url)
                resultat.append(get_product_description(soup))
                resultat.append(url)
                resultat.append(category_name)
                resultat[3] = re.findall(r'\d+', resultat[3])[0]
                download_img(img_url, directory["category_img"], resultat[0])
                resultats.append(resultat)
            next_present = test_next(category_soup)
            if next_present:
                category_url = get_next(category_soup,category_url)
        print(category_name)
        write_csv(resultats, directory["csv"], category_name)