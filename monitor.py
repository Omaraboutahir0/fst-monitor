import urllib.request
import os
import re
from urllib.parse import urljoin

# 🎯 CONFIGURATION DE TEST MULTI-PAGES (Hacker News)
PAGES_A_SURVEILLER = {
    "HackerNews_Accueil": "https://news.ycombinator.com/",
    "HackerNews_Nouveautes": "https://news.ycombinator.com/newest", 
    "HackerNews_Questions": "https://news.ycombinator.com/ask"
}

URL_NOTIFICATION = "https://ntfy.sh/FSTG-Marrakech"

FICHIER_TEXTE_SAUVEGARDE = "derniere_page.txt"
FICHIER_LIENS_SAUVEGARDE = "derniers_liens.txt"

def extraire_contenu_et_liens(html_content, base_url):
    """Extrait le texte de la page ainsi que tous les liens"""
    liens_bruts = re.findall(r'href=["\']([^"\']+)["\']', html_content)
    liens_utiles = set()
    
    for lien in liens_bruts:
        lien_complet = urljoin(base_url, lien)
        if lien_complet.startswith("http") and "#" not in lien:
            liens_utiles.add(lien_complet)
            
    html_clean = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html_content)
    html_clean = re.sub(r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>', '', html_clean)
    texte = re.sub(r'<[^>]+>', ' ', html_clean)
    texte_clean = " ".join(texte.split())
    
    return texte_clean, sorted(list(liens_utiles))

try:
    texte_global_actuel = []
    liens_globaux_actuels = set()

    # 1. Parcours de chaque sous-page du site de test
    for nom_page, url in PAGES_A_SURVEILLER.items():
        print(f"Analyse de la sous-page : {nom_page} ({url})...")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8', errors='ignore')
            
            texte_page, liens_page = extraire_contenu_et_liens(html, url)
            
            # On regroupe tout le contenu de toutes les pages visitées
            texte_global_actuel.append(f"--- PAGE: {nom_page} --- \n {texte_page}")
            liens_globaux_actuels.update(liens_page)
        except Exception as err_page:
            print(f"Impossible d'accéder à la sous-page {nom_page}: {err_page}")

    texte_final_actuel = "\n".join(texte_global_actuel)
    liens_finals_actuels = sorted(list(liens_globaux_actuels))

    changement_detecte = False
    message_notification = ""
    lien_a_ouvrir = "https://news.ycombinator.com/"

    # 2 & 3. Vérification s'il y a des fichiers de sauvegarde
    if not os.path.exists(FICHIER_LIENS_SAUVEGARDE) or not os.path.exists(FICHIER_TEXTE_SAUVEGARDE):
        # 🚀 CAS 1 : C'est le tout premier lancement (Pas d'historique)
        changement_detecte = True
        message_notification = "🚀 Initialisation réussie ! Le moniteur commence la surveillance active de vos pages."
        print("Première exécution : envoi de la notification d'initialisation et création des sauvegardes.")
    else:
        # 🔄 CAS 2 : Les fichiers existent déjà, on compare
        with open(FICHIER_LIENS_SAUVEGARDE, "r", encoding="utf-8") as f:
            anciens_liens = f.read().splitlines()
        
        nouveaux_liens = [l for l in liens_finals_actuels if l not in anciens_liens]
        
        if nouveaux_liens:
            changement_detecte = True
            message_notification = "🧪 Test : Nouveau lien détecté sur l'une des sous-pages !"
            lien_a_ouvrir = nouveaux_liens[0]
            print(f"Nouveau sous-lien trouvé : {lien_a_ouvrir}")
            
        if not changement_detecte:
            with open(FICHIER_TEXTE_SAUVEGARDE, "r", encoding="utf-8") as f:
                ancien_texte = f.read()
                
            if texte_final_actuel != ancien_texte:
                changement_detecte = True
                message_notification = "🧪 Test : Modification de texte détectée sur l'une des sous-pages !"
                lien_a_ouvrir = "https://news.ycombinator.com/"

    # 4. Envoi de l'alerte
    if changement_detecte:
        print(f"Notification envoyée : {message_notification}")
        headers = {
            "Title": "Test Multi-Pages",
            "Priority": "high",
            "Tags": "test_tube,arrows_counterclockwise",
            "Click": lien_a_ouvrir
        }
        req_notif = urllib.request.Request(URL_NOTIFICATION, data=message_notification.encode("utf-8"), headers=headers, method="POST")
        urllib.request.urlopen(req_notif)
    else:
        print("Aucun changement sur aucune des sous-pages.")

    # 5. Sauvegarde de l'état global
    with open(FICHIER_TEXTE_SAUVEGARDE, "w", encoding="utf-8") as f:
        f.write(texte_final_actuel)
        
    with open(FICHIER_LIENS_SAUVEGARDE, "w", encoding="utf-8") as f:
        f.write("\n".join(liens_finals_actuels))

except Exception as e:
    print(f"Erreur globale : {e}")
    raise e
