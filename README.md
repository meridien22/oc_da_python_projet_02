# # Extraction des données du site "Books to Scrape"
# oc_da_python_projet_p02

Script Python qui permet d'extraire des informations du site "Books to Scrape" (https://books.toscrape.com/index.html).
Les informations extraites sont :
- universal_product_code
- title
- category
- price_excluding_tax
- price_including_tax
- number_available
- review_rating
- product_page_url
- product_description
- image_url
L'image du livre est également extraite et sotocké dans un répertoire local.

Il est préférable de créer un environnement virtuel pour exécuter le script.

Placer vous dans votre répertoire de travail et exécuter ces commandes :

**python -m venv env**

Activer ensuite votre environnement virtuel :

**env\Scripts\activate.bat** (sous Windows)

Pour finir installer les paquets nécessaires pour l'exécution du script :

**pip install -r requirements.txt**

Vous pouvez ensuite lancer le script :

**python script_p02.py**

Vous pourrez alors choisir de lancer le scipt en mode démo ou complétement.