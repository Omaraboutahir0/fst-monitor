import urllib.request

# Configuration de l'adresse avec le protocole sécurisé https:// obligatoire pour Python
# Nous utilisons ici l'adresse officielle de ntfy avec votre canal (topic) "FSTG-Marrakech"
url = "https://ntfy.sh/FSTG-Marrakech"

# Message de test
message = "Le script de surveillance fonctionne à merveille ! 🚀".encode("utf-8")

headers = {
    "Title": "Test de Notification FST",
    "Priority": "high",
    "Tags": "white_check_mark,mortar_board"
}

req = urllib.request.Request(url, data=message, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req) as response:
        print("Notification envoyée avec succès !", response.read().decode())
except Exception as e:
    print(f"Erreur lors de l'envoi de la notification : {e}")
    raise e
