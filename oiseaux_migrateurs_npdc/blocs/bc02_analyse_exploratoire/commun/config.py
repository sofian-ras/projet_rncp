"""
Configuration locale a BC02 -- ce bloc est autonome (envoyable/executable
seul, sans le reste du projet), donc cette config est une copie reduite
aux seuls besoins de BC02, et non un import d'un commun/ partage.

donnees/traitees/ contient une copie figee des parquets produits par BC01
(observations_nettoyees, grille_presence_hebdo, meteo_processed), pour
que ce bloc n'ait pas besoin que BC01 ait ete execute a cote de lui.
"""

from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# ========== CHEMINS (locaux a ce bloc) ==========
REPERTOIRE_RACINE = Path(__file__).resolve().parent.parent
REPERTOIRE_DONNEES_TRAITEES = REPERTOIRE_RACINE / "donnees" / "traitees"


# ========== REGION GEOGRAPHIQUE ==========
@dataclass
class BoundingBoxNPdC:
    """Bounding box Nord-Pas-de-Calais en coordonnees GPS"""
    latitude_min: float = 49.5
    latitude_max: float = 51.5
    longitude_min: float = 1.5
    longitude_max: float = 4.0

    centre_latitude: float = 50.5
    centre_longitude: float = 2.75
    nom_region: str = "Nord-Pas-de-Calais"


ZONE_GEOGRAPHIQUE = BoundingBoxNPdC()


# ========== ESPECES ETUDIEES ==========
ESPECES = {
    "hirondelle_rustique": {
        "nom_scientifique": "Hirundo rustica",
        "nom_francais": "Hirondelle rustique",
        "code_gbif": 9515886,
        "mois_arrivee": [4, 5],
        "mois_depart": [9, 10],
    },
    "cigogne_blanche": {
        "nom_scientifique": "Ciconia ciconia",
        "nom_francais": "Cigogne blanche",
        "code_gbif": 2481912,
        "mois_arrivee": [3, 4],
        "mois_depart": [8, 9],
    },
    "martinet_noir": {
        "nom_scientifique": "Apus apus",
        "nom_francais": "Martinet noir",
        "code_gbif": 5228676,
        "mois_arrivee": [5, 6],
        "mois_depart": [8, 9],
    },
    "bergeronnette_printaniere": {
        "nom_scientifique": "Motacilla alba",
        "nom_francais": "Bergeronnette printaniere",
        "code_gbif": 9687165,
        "mois_arrivee": [3, 4],
        "mois_depart": [10, 11],
    },
}


# ========== LOGGING ==========
FORMAT_LOG = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

FICHIER_LOG = REPERTOIRE_RACINE / "logs" / f"projet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
FICHIER_LOG.parent.mkdir(exist_ok=True)
