import requests
import csv
import re
import os
import uuid
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from alive_progress import alive_bar

def get_soup(url):
    """
    Retourne un objet BeautifulSoup à partir d'une URL
    :param url: str, URL du site Boot to Scrape
    :return: Un objet BeautifulSoup
    """
    reponse = requests.get(url)
    page = reponse.content
    return BeautifulSoup(page, "html.parser")

def get_categorys(categorys, soup, url, root, user_choice):
    """
    Récupère la liste de toutes les categories du site
    :param categorys: list, liste qui va contenir les catégories
    :param soup: BeautifulSoup, objet BeautifulSoup à analyser
    :param url: str, URL de la page qui contient les categories, permet de reconstruire
        l'URL absolue de la catgégorie à partir de son URL relative
    :param root: str, chemin vers le dossier des données, permet de construire
        le chemin vers le dossier de chaque catgégorie
    :param user_choice: int, choix de l'utilisateur, permet de lancer le programme
        en mode démo (une seule catégorie extraire) ou en mode complet
    :return: list, liste de toutes les categories du site
        chaque catégorie est un dictionnaire qui reprend le nom, l'URL, le dossier et une
        liste de toutes les URL des livres
    """
    print("Getting category...")
    element = soup.find("ul", attrs = {'class': False})
    if user_choice == 1:
        elements = [element.find("li", attrs = {'class': False})]
    else :
        elements = element.find_all("li", attrs={'class': False})
    with alive_bar(len(elements), force_tty=True) as bar:
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
            bar()
    return categorys

def get_root():
    """
    Contruit le chemin vers le dossier racine qui contiendra les données
    :return: str, chemin vers le dossier racine des données
    """
    now = datetime.now()
    date_time = now.strftime("%y%m%d")
    directory = f"BTS_{date_time}_{uuid.uuid4()}"
    return os.path.join(".", "data", directory)

def create_directorys(root, categorys):
    """
    Crée la structure de dossier dans laquelle seront téléchargées les données
        chaque catégorie correspond à un dossier comprenant un dossier img pour les images
    :param root: str, chemin du dossier racine
    :param categorys: list, liste de toutes les categories du site
    """
    os.makedirs(root)
    for category in categorys:
        os.makedirs(category["directory"])
        os.makedirs(os.path.join(category["directory"], "img"))

def get_next(soup, url):
    """
    Retourne l'URL de la prochaine page de présentation des livres
    :param soup: BeautifulSoup, objet BeautifulSoup à analyser
    :param url: str, URL de la page de présentation des livres
    :return: str, URL de la prochaine page de présentation des livres
    """
    element = soup.find("li", class_ = "next")
    href = element.find("a").get("href")
    return urljoin(url, href)

def get_url_books(url):
    """
    Retourne les URL de tous les livres d'une catégorie. S'il y a plusieurs pages
    de livre, chaque page est analysée
    :param url: str, URL de la page qui présente les livres d'une catégorie
    :return: str, URL de tous les livres d'une catégorie
    """
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
    """
    Recherche la valeur d'un champ dans le tableau qui présente les infromations du livre
    :param soup: BeautifulSoup, objet BeautifulSoup à analyser
    :param hint: str, indice qui permet de préciser l'élément recherché
    :return:str, valeur recherchée
    """
    element = soup.find("th", string = hint)
    return element.find_next_sibling('td').text

def get_float_from_hint(soup, hint):
    """
    Permet d'extraire la partie numérique décimale d'une chaine de caractère
    :param soup: BeautifulSoup, objet BeautifulSoup à analyser
    :param hint: str, indice qui permet de préciser l'élément recherché
    :return: float, valeur recherche
    """
    value = get_string_from_hint(soup, hint)
    return re.findall(r'\d+\.*\d*', value)[0]

def get_int_from_hint(soup, hint):
    """
    Permet d'extraire la partie numérique entière d'une chaine de caractère
    :param soup: BeautifulSoup, objet BeautifulSoup à analyser
    :param hint: str, indice qui permet de préciser l'élément recherché
    :return: int, valeur recherche
    """
    value = get_string_from_hint(soup, hint)
    return re.findall(r'\d+', value)[0]

def get_title(soup):
    """
    Retourne le titre d'un livre
    :param soup:
    :return: str, tutre du livre
    """
    element = soup.find("h1")
    return element.text

def get_image_url(soup, url):
    """
    Retourne l'url d'un livre
    :param soup: BeautifulSoup, objet BeautifulSoup à analyser
    :param url: str, URL de la page qui présente les livres
    :return: str, URL absolue de la page du livre
    """
    element = soup.find("div", class_="item active")
    img = element.find("img")
    return urljoin(url, img["src"])

def get_product_description(soup):
    """
    Retourne le description d'un livre
    :param soup: BeautifulSoup, objet BeautifulSoup à analyser
    :return: str, description du livre
    """
    element = soup.find("p", attrs={'class': False})
    if element:
        return element.text
    else:
        return ""

def get_rating(soup):
    """
    Récupère la note attribuée à chaque livre
    :param soup: BeautifulSoup, objet BeautifulSoup à analyser
    :return: int, note attribué au livre
    """
    element = soup.find("p", class_="star-rating")
    nombre_etoile = element['class'][1]
    dico_correspondance ={
        "One":1,
        "Two":2,
        "Three":3,
        "Four":4,
        "Five":5
    }
    return (dico_correspondance[nombre_etoile])

def download_img(url, dir, upc):
    """
    Téléchrage l'image du livre à partir de son URL
    :param url: str, URL du livre
    :param dir: str, dossier dans lequel sera enregistrée l'image du livre
    :param upc: str, nom du fichier à enregistrer
    """
    reponse = requests.get(url)
    with open(os.path.join(dir, "img", f"{upc}.jpg"), 'wb') as fichier:
        fichier.write(reponse.content)

def write_csv(resultats, dir, name_category, en_tete):
    """
    Ecrit dans un fichier CSV les informations de tous les livres d'une catégorie
    :param resultats: list, liste qui contient toutes les informations des livres
    :param dir: str, chemin vers le dossier iu sera enregistré le fichier CSV
    :param name_category: str, nom de la catégorie, permet de nommer le fichier CSV
    :param en_tete: list, liste qui contient les en-têtes du fichier CSV
    """
    file_name = f"{name_category}.csv"
    with open(os.path.join(dir, file_name), "w", newline="", encoding='utf-8') as fichier_csv:
        writer = csv.writer(fichier_csv, delimiter=",")
        writer.writerow(en_tete)
        for resultat in resultats:
            writer.writerow(resultat)

def ask_user_choice():
    """
    Demande à l'utilisateur s'il veut lancer le programme en mode démo, complet ou s'il
    veut quitter le script
    :return: int, choix de l'utilisateur
    """
    actions = [
        "Lancer le script en mode démo",
        "Lancer le script complétement",
        "Quitter le script"
    ]
    print("Veuillez choisir une option :")
    for index, action in enumerate(actions):
        print(f"{index + 1}. {action}")
    while True:
        try:
            selection = int(input("Entrez le numéro de votre choix : "))
            if 1 <= selection <= len(actions):
                break
            else:
                print("Choix invalide. Veuillez entrer un numéro de la liste.")
        except ValueError:
            print("Saisie invalide. Veuillez entrer un nombre.")
    return selection

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
    # compteur qui stocke le nombre total de livre téléchargé
    cpt = 0

    user_choice = ask_user_choice()
    if user_choice == 3:
        quit()
    soup_base = get_soup(url_base)
    categorys = get_categorys(categorys,soup_base, url_base, root, user_choice)
    directorys = create_directorys(root, categorys)
    for category in categorys:
        print(f"Download category {category['name']}...")
        resultats = []
        cpt += len(category["url_books"])
        with alive_bar(len(category["url_books"]), force_tty=True) as bar:
            for url in category["url_books"]:
                resultat = []
                soup = get_soup(url)
                resultat.append(get_string_from_hint(soup, "UPC"))
                resultat.append(get_title(soup))
                resultat.append(category["name"])
                resultat.append(get_float_from_hint(soup, "Price (excl. tax)"))
                resultat.append(get_float_from_hint(soup, "Price (incl. tax)"))
                resultat.append(get_int_from_hint(soup, "Availability"))
                resultat.append(get_rating(soup))
                resultat.append(url)
                resultat.append(get_product_description(soup))
                img_url = get_image_url(soup, url)
                resultat.append(img_url)
                download_img(img_url, category["directory"], resultat[0])
                resultats.append(resultat)
                bar()
        write_csv(resultats, category["directory"], category["name"], en_tete)

    print(f"Fin du traitement, {cpt} livres téléchargés.")