import requests

import hashlib

import os

URL = "https://www.fstg-marrakech.ac.ma/"

NTFY_TOPIC = "fstg-alertes-2026"

def get_page_content():

    try:

        response = requests.get(URL, timeout=20)

        response.raise_for_status()

        return response.text

    except Exception as e:

        print("Erreur de récupération du site :", e)

        return None

def get_hash(content):

    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def send_notification(message):

    try:

        requests.post(

            f"https://ntfy.sh/{NTFY_TOPIC}",

            data=message.encode("utf-8"),

            timeout=20

        )

    except Exception as e:

        print("Erreur notification :", e)

def main():

    content = get_page_content()

    if content is None:

        return

    new_hash = get_hash(content)

    old_hash = None

    if os.path.exists("last_hash.txt"):

        with open("last_hash.txt", "r") as file:

            old_hash = file.read().strip()

    if old_hash and old_hash != new_hash:

        send_notification("🚨 Le site FSTG Marrakech a changé ! Vérifiez les nouvelles informations.")

    with open("last_hash.txt", "w") as file:

        file.write(new_hash)

if __name__ == "__main__":

    main()
