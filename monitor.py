import urllib.request

# Configuration exacte selon vos indications :
# Application/Serveur : FST.sh
# Topic : FST Marrakech-Marrakech (encodé pour les espaces dans l'URL)
url = "fstg-marrakech.ac.ma"
message = "Le script de surveillance fonctionne à merveille ! 🚀".encode("utf-8")

headers = {
    "Title": "Test de Notification",
    "Priority": "high",
    "Tags": "white_check_mark,computer"
}

req = urllib.request.Request(url, data=message, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req) as response:
        print("Notification envoyée avec succès !", response.read().decode())
except Exception as e:
    print(f"Erreur lors de l'envoi de la notification : {e}")
    raise e
