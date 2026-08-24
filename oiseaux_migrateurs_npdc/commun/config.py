"""
Configuration centralisee du projet.

Ce module est utilise par les 6 blocs (blocs/bc01_... a blocs/bc06_...) :
c'est la seule source de verite pour les chemins, la zone geographique,
les especes suivies et les hyperparametres. Aucun bloc ne redefinit ces
informations en local.
"""

from pathlib import Path
from typing import Dict, Tuple
from dataclasses import dataclass
from datetime import datetime

# ========== CHEMINS ==========
REPERTOIRE_RACINE = Path(__file__).parent.parent
REPERTOIRE_DONNEES = REPERTOIRE_RACINE / "donnees"
REPERTOIRE_DONNEES_BRUTES = REPERTOIRE_DONNEES / "brutes"
REPERTOIRE_DONNEES_TRAITEES = REPERTOIRE_DONNEES / "traitees"
REPERTOIRE_CARACTERISTIQUES = REPERTOIRE_DONNEES / "caracteristiques"
REPERTOIRE_MODELES = REPERTOIRE_RACINE / "modeles"
REPERTOIRE_BLOCS = REPERTOIRE_RACINE / "blocs"

# Creer repertoires s'ils n'existent pas
for repertoire in [REPERTOIRE_DONNEES_BRUTES, REPERTOIRE_DONNEES_TRAITEES,
                   REPERTOIRE_CARACTERISTIQUES, REPERTOIRE_MODELES]:
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
        "mois_arrivee": [4, 5],  # Avril, Mai
        "mois_depart": [9, 10],   # Septembre, Octobre
    },
    "cigogne_blanche": {
        "nom_scientifique": "Ciconia ciconia",
        "nom_francais": "Cigogne blanche",
        "code_gbif": 2481912,
        "mois_arrivee": [3, 4],   # Mars, Avril
        "mois_depart": [8, 9],    # Aout, Septembre
    },
    "martinet_noir": {
        "nom_scientifique": "Apus apus",
        "nom_francais": "Martinet noir",
        "code_gbif": 5228676,
        "mois_arrivee": [5, 6],   # Mai, Juin
        "mois_depart": [8, 9],    # Aout, Septembre
    },
    "bergeronnette_printaniere": {
        "nom_scientifique": "Motacilla alba",
        "nom_francais": "Bergeronnette printaniere",
        "code_gbif": 9687165,
        "mois_arrivee": [3, 4],   # Mars, Avril
        "mois_depart": [10, 11],  # Octobre, Novembre
    },
}


# ========== PARAMETRES ACQUISITION (BC01) ==========
class ParametresAcquisition:
    """Parametres pour telechargement donnees"""

    # GBIF
    ANNEE_DEBUT = 2015
    ANNEE_FIN = 2024
    LIMITE_RESULTATS_PAR_ESPECE = 10000
    DELAI_ENTRE_REQUETES = 1  # secondes

    # Open-Meteo
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


# ========== PARAMETRES NETTOYAGE (BC01) ==========
class ParametresNettoyage:
    """Parametres pour traitement et validation donnees"""

    # Filtrage observations
    PRECISION_MIN_KM = 1  # Exclure observations imprecises
    DISTANCE_MAX_REGION_KM = 10  # Garder observations max D km de la region

    # Validation coordonnees
    LATITUDE_MIN = ZONE_GEOGRAPHIQUE.latitude_min - 1
    LATITUDE_MAX = ZONE_GEOGRAPHIQUE.latitude_max + 1
    LONGITUDE_MIN = ZONE_GEOGRAPHIQUE.longitude_min - 1
    LONGITUDE_MAX = ZONE_GEOGRAPHIQUE.longitude_max + 1

    # Agregation temporelle
    AGREGATION_SEMAINES = True  # Grouper par semaine


# ========== PARAMETRES ML (BC03) ==========
class ParametresML:
    """Parametres entrainement modeles Machine Learning"""

    TEST_SIZE = 0.2
    VALIDATION_SIZE = 0.1
    RANDOM_STATE = 42

    # Hyperparametres XGBoost
    XGBOOST_PARAMS = {
        "max_depth": 6,
        "learning_rate": 0.05,
        "n_estimators": 100,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
    }

    # Hyperparametres Random Forest
    RANDOM_FOREST_PARAMS = {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 5,
        "random_state": RANDOM_STATE,
    }

    # Metriques seuil
    SEUIL_PRECISION_ACCEPTABLE = 0.70


# ========== PARAMETRES DEEP LEARNING (BC04) ==========
class ParametresDL:
    """Parametres entrainement du modele de Deep Learning (BC04).

    BC04 demontre la competence "prediction sur donnees non structurees"
    (texte), une competence distincte de BC03 (donnees tabulaires
    structurees). Le modele utilise est un reseau Embedding + LSTM
    pour de la classification de texte (analyse de sentiment).
    """

    NB_MOTS_VOCABULAIRE = 10000     # taille du vocabulaire conserve
    LONGUEUR_SEQUENCE = 200         # nombre de mots par avis, apres troncature/padding
    TAILLE_EMBEDDING = 32
    UNITES_LSTM = 32
    DROPOUT_RATE = 0.3
    BATCH_SIZE = 128
    EPOCHS = 5
    TAILLE_ECHANTILLON_DEMO = 6000  # sous-echantillon pour un entrainement rapide en demo
    RANDOM_STATE = 42


# ========== PARAMETRES API (BC05) ==========
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


if __name__ == "__main__":
    print("Configuration chargee")
    print("Repertoires crees")
    print(
        f"ZONE: {ZONE_GEOGRAPHIQUE.nom_region} "
        f"({ZONE_GEOGRAPHIQUE.latitude_min}-{ZONE_GEOGRAPHIQUE.latitude_max}deg N, "
        f"{ZONE_GEOGRAPHIQUE.longitude_min}-{ZONE_GEOGRAPHIQUE.longitude_max}deg E)"
    )
    noms_especes = ", ".join(nom.split("_")[0] for nom in ESPECES)
    print(f"ESPECES: {len(ESPECES)} ({noms_especes})")
