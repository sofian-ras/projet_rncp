"""
BC04 - Acquisition d'images : telecharge des photos des 4 especes du projet
depuis GBIF (mediaType=StillImage : iNaturalist / Flickr, URLs JPEG directes).

Code plat : une fonction = une etape. Sert au notebook_bc04_images.ipynb.
Les images sont mises en cache dans donnees/images_oiseaux/<espece>/ ;
un second appel ne re-telecharge rien.
"""

import io
import time
from pathlib import Path

import requests
from loguru import logger

from commun.config import ESPECES, REPERTOIRE_DONNEES

REPERTOIRE_IMAGES = REPERTOIRE_DONNEES / "images_oiseaux"
URL_GBIF = "https://api.gbif.org/v1/occurrence/search"


def _urls_images_espece(code_gbif: int, nb_voulu: int) -> list:
    """Recupere jusqu'a nb_voulu URLs d'images pour une espece (pagination GBIF)."""
    urls, decalage = [], 0
    while len(urls) < nb_voulu:
        reponse = requests.get(URL_GBIF, params={
            "taxonKey": code_gbif,
            "mediaType": "StillImage",
            "limit": 300,
            "offset": decalage,
        }, timeout=30)
        reponse.raise_for_status()
        resultats = reponse.json().get("results", [])
        if not resultats:
            break
        for occ in resultats:
            for media in occ.get("media", []):
                lien = media.get("identifier")
                if media.get("type") == "StillImage" and lien and lien.lower().endswith((".jpg", ".jpeg")):
                    urls.append(lien)
        decalage += len(resultats)
        time.sleep(0.5)  # on menage l'API publique
    return urls[:nb_voulu]


def _telecharger_image(url: str, chemin: Path) -> bool:
    """Telecharge une image ; renvoie False (sans lever) si l'URL est cassee ou l'image trop petite."""
    try:
        reponse = requests.get(url, timeout=20)
        reponse.raise_for_status()
        contenu = reponse.content
        if len(contenu) < 3000:  # < 3 Ko : probablement une page d'erreur, pas une photo
            return False
        chemin.write_bytes(contenu)
        return True
    except requests.RequestException:
        return False


def telecharger_images(nb_par_espece: int = 120) -> Path:
    """Telecharge nb_par_espece photos pour chacune des 4 especes (skip si deja present)."""
    logger.info(f"Acquisition d'images : {nb_par_espece} photos par espece -> {REPERTOIRE_IMAGES}")
    for cle, infos in ESPECES.items():
        dossier = REPERTOIRE_IMAGES / cle
        dossier.mkdir(parents=True, exist_ok=True)
        deja = len(list(dossier.glob("*.jpg")))
        if deja >= nb_par_espece:
            logger.info(f"  {infos['nom_francais']:<26} : {deja} images deja en cache, on saute")
            continue

        logger.info(f"  {infos['nom_francais']:<26} : recuperation des URLs...")
        urls = _urls_images_espece(infos["code_gbif"], nb_par_espece * 2)  # marge pour les liens casses

        obtenues = deja
        for url in urls:
            if obtenues >= nb_par_espece:
                break
            chemin = dossier / f"img_{obtenues:03d}.jpg"
            if chemin.exists():
                obtenues += 1
                continue
            if _telecharger_image(url, chemin):
                obtenues += 1
            time.sleep(0.1)
        logger.info(f"  {infos['nom_francais']:<26} : {obtenues} images sur disque")

    total = sum(len(list((REPERTOIRE_IMAGES / c).glob('*.jpg'))) for c in ESPECES)
    logger.info(f"Total : {total} images dans {REPERTOIRE_IMAGES}")
    return REPERTOIRE_IMAGES


if __name__ == "__main__":
    telecharger_images()
