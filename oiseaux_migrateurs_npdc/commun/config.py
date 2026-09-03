"""
Configuration partagee par les 6 blocs.

Rassemble ce qui etait auparavant duplique dans chaque `blocs/bc0X_.../commun/` :
chemins du projet, zone geographique, especes etudiees, format de log et
parametres de chaque etape (acquisition, nettoyage, ML, segmentation, DL, API).
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# ========== CHEMINS (racine du projet = dossier oiseaux_migrateurs_npdc/) ==========
REPERTOIRE_RACINE = Path(__file__).resolve().parent.parent
REPERTOIRE_DONNEES = REPERTOIRE_RACINE / "donnees"
REPERTOIRE_DONNEES_BRUTES = REPERTOIRE_DONNEES / "brutes"
REPERTOIRE_DONNEES_TRAITEES = REPERTOIRE_DONNEES / "traitees"
REPERTOIRE_MODELES = REPERTOIRE_RACINE / "modeles"
REPERTOIRE_OUTPUTS = REPERTOIRE_RACINE / "outputs"

for _repertoire in (REPERTOIRE_DONNEES_BRUTES, REPERTOIRE_DONNEES_TRAITEES, REPERTOIRE_MODELES):
    _repertoire.mkdir(parents=True, exist_ok=True)


# ========== ZONE GEOGRAPHIQUE ==========
@dataclass
class BoundingBoxNPdC:
    """Bounding box Nord-Pas-de-Calais en coordonnees GPS."""

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


# ========== PARAMETRES ACQUISITION (BC01) ==========
class ParametresAcquisition:
    """Telechargement GBIF + Open-Meteo."""

    # GBIF ne recense quasiment aucune observation de ces 4 especes dans la zone
    # avant 2019 (trop peu de contributeurs actifs a l'epoque). Demarrer en 2015
    # ajoutait 4 annees entierement vides a la grille presence/absence : 40 % de
    # lignes toutes a "absence" qui n'etaient pas de vraies absences ecologiques
    # mais des trous de collecte, faussant l'equilibre des classes et donnant a
    # BC03 un separateur artificiel (annee <= 2018 -> absence). On borne donc a
    # la premiere annee reellement couverte par la source.
    ANNEE_DEBUT = 2019
    ANNEE_FIN = 2024
    LIMITE_RESULTATS_PAR_ESPECE = 10000
    DELAI_ENTRE_REQUETES = 1  # secondes

    # Reessais sur erreur passagere des API (5xx, 429, timeout, coupure reseau).
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


# ========== PARAMETRES NETTOYAGE (BC01) ==========
class ParametresNettoyage:
    """Validation et agregation des donnees brutes."""

    PRECISION_MIN_KM = 1
    DISTANCE_MAX_REGION_KM = 10

    LATITUDE_MIN = ZONE_GEOGRAPHIQUE.latitude_min - 1
    LATITUDE_MAX = ZONE_GEOGRAPHIQUE.latitude_max + 1
    LONGITUDE_MIN = ZONE_GEOGRAPHIQUE.longitude_min - 1
    LONGITUDE_MAX = ZONE_GEOGRAPHIQUE.longitude_max + 1

    AGREGATION_SEMAINES = True


# ========== PARAMETRES MACHINE LEARNING (BC03) ==========
class ParametresML:
    """Entrainement et evaluation des modeles supervises."""

    TEST_SIZE = 0.2
    VALIDATION_SIZE = 0.1
    RANDOM_STATE = 42
    N_SPLITS_CV = 5  # plis pour la validation croisee du modele retenu

    XGBOOST_PARAMS = {
        "max_depth": 6,
        "learning_rate": 0.05,
        "n_estimators": 100,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
    }

    RANDOM_FOREST_PARAMS = {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 5,
        "random_state": RANDOM_STATE,
    }

    SEUIL_PRECISION_ACCEPTABLE = 0.70


# ========== PARAMETRES SEGMENTATION (BC03, non supervise) ==========
class ParametresSegmentation:
    """K-Means : on teste K de K_MIN a K_MAX et on retient le meilleur score de silhouette."""

    K_MIN = 2
    K_MAX = 8


# ========== PARAMETRES DEEP LEARNING (BC04) ==========
class ParametresDL:
    """Entrainement du modele Embedding + LSTM (analyse de sentiment)."""

    NB_MOTS_VOCABULAIRE = 10000
    LONGUEUR_SEQUENCE = 200
    TAILLE_EMBEDDING = 32
    UNITES_LSTM = 32
    DROPOUT_RATE = 0.3
    BATCH_SIZE = 128
    EPOCHS = 5
    TAILLE_ECHANTILLON_DEMO = 6000
    RANDOM_STATE = 42


# ========== PARAMETRES API (BC05) ==========
class ParametresAPI:
    """Serveur FastAPI."""

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
