"""
Configuration locale a BC01 -- ce bloc est autonome (envoyable/executable
seul, sans le reste du projet), donc cette config est une copie reduite
aux seuls besoins de BC01, et non un import d'un commun/ partage.
"""

from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# ========== CHEMINS (locaux a ce bloc) ==========
REPERTOIRE_RACINE = Path(__file__).resolve().parent.parent
REPERTOIRE_DONNEES = REPERTOIRE_RACINE / "donnees"
REPERTOIRE_DONNEES_BRUTES = REPERTOIRE_DONNEES / "brutes"
REPERTOIRE_DONNEES_TRAITEES = REPERTOIRE_DONNEES / "traitees"

for repertoire in [REPERTOIRE_DONNEES_BRUTES, REPERTOIRE_DONNEES_TRAITEES]:
    repertoire.mkdir(parents=True, exist_ok=True)


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


# ========== PARAMETRES ACQUISITION ==========
class ParametresAcquisition:
    """Parametres pour telechargement donnees"""

    ANNEE_DEBUT = 2015
    ANNEE_FIN = 2024
    LIMITE_RESULTATS_PAR_ESPECE = 10000
    DELAI_ENTRE_REQUETES = 1  # secondes

    # Reessais en cas d'erreur passagere des API (5xx, 429, timeout, coupure reseau).
    # GBIF renvoie regulierement des 503 transitoires : sans reessai, l'acquisition
    # repartait avec 0 observation.
    NB_TENTATIVES_MAX = 4
    DELAI_RETRY_INITIAL = 2  # secondes, double a chaque tentative (2, 4, 8...)

    API_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"
    VARIABLES_METEO = [
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "precipitation_sum",
        "windspeed_10m_max",
        "relative_humidity_2m_mean",
        "pressure_msl_mean",
    ]


# ========== PARAMETRES NETTOYAGE ==========
class ParametresNettoyage:
    """Parametres pour traitement et validation donnees"""

    PRECISION_MIN_KM = 1
    DISTANCE_MAX_REGION_KM = 10

    LATITUDE_MIN = ZONE_GEOGRAPHIQUE.latitude_min - 1
    LATITUDE_MAX = ZONE_GEOGRAPHIQUE.latitude_max + 1
    LONGITUDE_MIN = ZONE_GEOGRAPHIQUE.longitude_min - 1
    LONGITUDE_MAX = ZONE_GEOGRAPHIQUE.longitude_max + 1

    AGREGATION_SEMAINES = True


# ========== LOGGING ==========
FORMAT_LOG = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

FICHIER_LOG = REPERTOIRE_RACINE / "logs" / f"projet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
FICHIER_LOG.parent.mkdir(exist_ok=True)
