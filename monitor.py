import urllib.request
import urllib.parse
import re
import os

# CONFIGURATION
URL_FST = "https://fstg-marrakech.ac.ma/"  # L'adresse de la FSTG Marrakech
URL_NTFY = "https://ntfy.sh/FSTG-Marrakech"

FILE_TEXTE = "derniere_page_fst.txt"
FILE_LIENS = "derniers_liens_fst.txt"

def extraire_annonces(html):
    """
    Extrait les textes et les liens des actualités/annonces du code HTML.
    Adapte les sélecteurs selon la structure du site.
    """
    # Recherche des liens (href) et des textes associés dans le HTML
    # Cette regex cherche des liens contenant souvent 'actualite', 'annonce' ou des éléments de liste
    liens_trouves = re.findall(r'href="([^"]+)"[^>]*>([^<]+)</a>', html)
    
    annonces = []
    for href, texte in liens_trouves:
        texte_propre = texte.strip()
        # On filtre pour ne garder que les vrais textes d'actualités (pas les menus 'Accueil', etc.)
        if len(texte_propre) > 15 and any(mot in href.lower() or mot in texte_propre.lower() for mot in ["actualite", "annonce", "communique", "note", "etudiant", "inscription"]):
            # Reconstruire le lien complet si c'est un lien relatif
            lien_complet = urllib.parse.urljoin(URL_FST, href)
            annonces.append((texte_propre, lien_complet))
            
    return annonces

try:
    print(f"Connexion au site de la FST : {URL_FST}...")
    headers_nav = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req_fst = urllib.request.Request(URL_FST, headers=headers_nav)
    
    with urllib.request.urlopen(req_fst, timeout=15) as response:
        html_content = response.read().decode('utf-8', errors='ignore')

    # Extraction des annonces actuelles
    annonces_actuelles = extraire_annonces(html_content)
    print(f"Annonces trouvées sur la page : {len(annonces_actuelles)}")

    # Création d'une empreinte texte simple pour détecter s'il y a un changement global
    contenu_texte_actuel = "\n".join([f"{t} ({l})" for t, l in annonces_actuelles])

    # --- LOGIQUE DE COMPARAISON ---
    
    # 1. Premier lancement (Initialisation)
    if not os.path.exists(FILE_TEXTE):
        print("Première exécution : Enregistrement de l'état initial...")
        with open(FILE_TEXTE, "w", encoding="utf-8") as f:
            f.write(contenu_texte_actuel)
        
        # Notification d'initialisation
        msg_init = "🚀 Initialisation réussie ! Le robot surveille désormais le site de la FSTG Marrakech."
        req_ntfy = urllib.request.Request(
            URL_NTFY, 
            data=msg_init.encode("utf-8"), 
            headers={"Title": "FSTG Monitor Activated", "Priority": "high", "Tags": "school,white_check_mark"},
            method="POST"
        )
        urllib.request.urlopen(req_ntfy)
        print("Notification d'initialisation envoyée.")

    # 2. Lancements suivants (Comparaison)
    else:
        print("Comparaison avec l'état précédent...")
        with open(FILE_TEXTE, "r", encoding="utf-8") as f:
            ancien_contenu = f.read()

        if contenu_texte_actuel != ancien_content:
            print("Changement détecté !")
            
            # Trouver ce qui a changé (par exemple un nouveau lien)
            anciens_liens = re.findall(r'\((https?://[^\)]+)\)', ancien_content)
            nouveautes = []
            
            for texte, lien in annonces_actuelles:
                if lien not in anciens_liens:
                    nouveautes.append(f"📢 {texte}\n🔗 {lien}")

            if nouveautes:
                message_alerte = "🆕 Nouvelle annonce FST détectée !\n\n" + "\n\n".join(nouveautes)
            else:
                message_alerte = "📝 Une mise à jour ou modification a été faite sur la page d'accueil de la FST !"

            # Envoi de la notification
            req_ntfy = urllib.request.Request(
                URL_NTFY, 
                data=message_alerte.encode("utf-8"), 
                headers={"Title": "Alerte FST Marrakech !", "Priority": "urgent", "Tags": "warning,bell"},
                method="POST"
            )
            urllib.request.urlopen(req_ntfy)
            print("Notification d'alerte envoyée sur votre téléphone !")

            # Sauvegarde du nouvel état
            with open(FILE_TEXTE, "w", encoding="utf-8") as f:
                f.write(contenu_texte_actuel)
        else:
            print("Aucun changement détecté sur le site de la FST.")

except Exception as e:
    print(f"Erreur rencontrée : {e}")
    raise e
