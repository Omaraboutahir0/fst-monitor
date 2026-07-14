import urllib.request
import urllib.parse
import json
import re
import os

# ================= CONFIGURATION GREEN-API =================
ID_INSTANCE = "710722683092"
API_TOKEN_INSTANCE = "171338a45065416492ee51f0e922a737bf8de6df0f3c45f9a5"
ID_GROUPE_WHATSAPP = "120363402810483357@g.us"  # <--- CORRIGÉ ICI AVEC @g.us

URL_FST = "https://fstg-marrakech.ac.ma/"
FILE_TEXTE = "fst_archive_officielle.txt"
# ===========================================================

def envoyer_whatsapp_groupe(message):
    """ Envoie un message dans le groupe WhatsApp via Green-API """
    try:
        url_api = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN_INSTANCE}"
        
        payload = {
            "chatId": ID_GROUPE_WHATSAPP,
            "message": message
        }
        data_json = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(
            url_api, 
            data=data_json, 
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            res = response.read().decode('utf-8')
            print("Message envoyé au groupe WhatsApp avec succès !")
    except Exception as e:
        print(f"Erreur lors de l'envoi WhatsApp : {e}")

def extraire_annonces(html):
    """ Extrait les textes et les liens des actualités du site de la FST """
    liens_trouves = re.findall(r'href="([^"]+)"[^>]*>([^<]+)</a>', html)
    annonces = []
    for href, texte in liens_trouves:
        texte_propre = texte.strip()
        if len(texte_propre) > 15 and any(mot in href.lower() or mot in texte_propre.lower() for mot in ["actualite", "annonce", "communique", "note", "etudiant", "inscription"]):
            lien_complet = urllib.parse.urljoin(URL_FST, href)
            annonces.append((texte_propre, lien_complet))
    return annonces

try:
    print(f"Connexion au site de la FST : {URL_FST}...")
    headers_nav = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9"
    }
    
    req_fst = urllib.request.Request(URL_FST, headers=headers_nav)
    with urllib.request.urlopen(req_fst, timeout=30) as response:
        html_content = response.read().decode('utf-8', errors='ignore')

    annonces_actuelles = extraire_annonces(html_content)
    print(f"Annonces trouvées : {len(annonces_actuelles)}")
    contenu_texte_actuel = "\n".join([f"{t} ({l})" for t, l in annonces_actuelles])

    # --- LOGIQUE DE COMPARAISON ---
    if not os.path.exists(FILE_TEXTE):
        print("Première exécution : Enregistrement de l'état initial...")
        with open(FILE_TEXTE, "w", encoding="utf-8") as f:
            f.write(contenu_texte_actuel)
        
        # Message de présentation officiel et stylisé
        msg_init = (
            "🎓 *Bot FSTG Marrakech*\n\n"
            "Bonjour à tous ! 👋\n\n"
            "Je suis le *Robot d'Annonces Officiel* de la FSTG Marrakech. 🤖🏫\n\n"
            "👉 *Mon rôle :* Je surveille le site de la faculté 24h/24. Dès qu'un professeur ou l'administration publie une nouvelle annonce, un emploi du temps ou un communiqué important, je vous l'envoie instantanément ici avec son lien direct !\n\n"
            "Restez connectés, vous ne raterez plus aucune information importante ! 🚀"
        )
        envoyer_whatsapp_groupe(msg_init)

    else:
        print("Comparaison avec l'état précédent...")
        with open(FILE_TEXTE, "r", encoding="utf-8") as f:
            ancien_contenu = f.read()

        if contenu_texte_actuel != ancien_contenu:
            print("Changement détecté !")
            anciens_liens = re.findall(r'\((https?://[^\)]+)\)', ancien_contenu)
            nouveautes = []
            
            for texte, lien in annonces_actuelles:
                if lien not in anciens_liens:
                    nouveautes.append(f"📢 *{texte}*\n🔗 {lien}")

            if nouveautes:
                message_alerte = "🆕 *Nouvelle annonce FST détectée !*\n\n" + "\n\n".join(nouveautes)
            else:
                message_alerte = "📝 Une modification a été effectuée sur la page d'accueil de la FST !"

            # Envoi dans le groupe WhatsApp !
            envoyer_whatsapp_groupe(message_alerte)

            with open(FILE_TEXTE, "w", encoding="utf-8") as f:
                f.write(contenu_texte_actuel)
        else:
            print("Aucun changement détecté sur le site.")

except Exception as e:
    print(f"Erreur globale : {e}")
