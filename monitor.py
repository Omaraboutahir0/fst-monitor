import hashlib

import requests

from bs4 import BeautifulSoup

URL = "https://www.fstg-marrakech.ac.ma/"

print("Téléchargement du site...")

response = requests.get(URL, timeout=30)

response.raise_for_status()

print("Analyse de la page...")

soup = BeautifulSoup(response.text, "html.parser")

page_text = soup.get_text(separator=" ", strip=True)

current_hash = hashlib.sha256(

    page_text.encode("utf-8")

).hexdigest()

print("Hash actuel :")

print(current_hash)
