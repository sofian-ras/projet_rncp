"""
Configuration locale a BC05 -- ce bloc est autonome (envoyable/executable
seul, sans le reste du projet), donc cette config est une copie reduite
aux seuls besoins de BC05, et non un import d'un commun/ partage.

modeles/ et donnees/traitees/ et outputs/eda/ contiennent des copies
figees des livrables de BC02/BC03, pour que ce bloc n'ait pas besoin que
les autres blocs aient ete executes a cote de lui.
"""

from pathlib import Path
from datetime import datetime

# ========== CHEMINS (locaux a ce bloc) ==========
REPERTOIRE_RACINE = Path(__file__).resolve().parent.parent
REPERTOIRE_DONNEES_TRAITEES = REPERTOIRE_RACINE / "donnees" / "traitees"
REPERTOIRE_MODELES = REPERTOIRE_RACINE / "modeles"


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


# ========== PARAMETRES API ==========
class ParametresAPI:
    """Parametres serveur API"""

    TITRE = "API Prediction Oiseaux Migrateurs"
    VERSION = "1.0.0"
    DESCRIPTION = "Prediction arrivee oiseaux migrateurs - Nord-Pas-de-Calais"
    HOST = "127.0.0.1"
    PORT = 8000
    LOG_LEVEL = "info"


# ========== LOGGING ==========
FORMAT_LOG = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

FICHIER_LOG = REPERTOIRE_RACINE / "logs" / f"projet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
FICHIER_LOG.parent.mkdir(exist_ok=True)
