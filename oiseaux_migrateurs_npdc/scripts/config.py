"""
Configuration centralisée du projet
Variables en français, clean et maintenable
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
REPERTOIRE_SCRIPTS = REPERTOIRE_RACINE / "scripts"

# Créer répertoires s'ils n'existent pas
for repertoire in [REPERTOIRE_DONNEES_BRUTES, REPERTOIRE_DONNEES_TRAITEES, 
                   REPERTOIRE_CARACTERISTIQUES, REPERTOIRE_MODELES]:
    repertoire.mkdir(parents=True, exist_ok=True)


# ========== REGION GEOGRAPHIQUE ==========
@dataclass
class BoundingBoxNPdC:
    """Bounding box Nord-Pas-de-Calais en coordonnées GPS"""
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
        "mois_depart": [8, 9],    # Août, Septembre
    },
    "martinet_noir": {
        "nom_scientifique": "Apus apus",
        "nom_francais": "Martinet noir",
        "code_gbif": 5228676,
        "mois_arrivee": [5, 6],   # Mai, Juin
        "mois_depart": [8, 9],    # Août, Septembre
    },
    "bergeronnette_printaniere": {
        "nom_scientifique": "Motacilla alba",
        "nom_francais": "Bergeronnette printanière",
        "code_gbif": 9687165,
        "mois_arrivee": [3, 4],   # Mars, Avril
        "mois_depart": [10, 11],  # Octobre, Novembre
    },
}


# ========== PARAMETRES ACQUISITION ==========
class ParametresAcquisition:
    """Paramètres pour téléchargement données"""
    
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


# ========== PARAMETRES NETTOYAGE ==========
class ParametresNettoyage:
    """Paramètres pour traitement et validation données"""
    
    # Filtrage observations
    PRECISION_MIN_KM = 1  # Exclure observations imprécises
    DISTANCE_MAX_REGION_KM = 10  # Garder observations maxD km de la région
    
    # Validation coordonnées
    LATITUDE_MIN = ZONE_GEOGRAPHIQUE.latitude_min - 1
    LATITUDE_MAX = ZONE_GEOGRAPHIQUE.latitude_max + 1
    LONGITUDE_MIN = ZONE_GEOGRAPHIQUE.longitude_min - 1
    LONGITUDE_MAX = ZONE_GEOGRAPHIQUE.longitude_max + 1
    
    # Agrégation temporelle
    AGREGATION_SEMAINES = True  # Grouper par semaine


# ========== PARAMETRES FEATURES ==========
class ParametresFeatures:
    """Paramètres engineering des features"""
    
    # Windows temporels (en jours)
    FENETRE_HISTORIQUE_METEO = 7  # 1 semaine de météo avant observation
    FENETRE_AGREGATION = 7  # Agréger par semaine
    
    # Variables to include
    VARIABLES_METEO_FINALES = [
        "temperature_max",
        "temperature_min",
        "precipitation_cumule",
        "vent_max",
        "humidite_moyenne",
        "pression_moyenne",
    ]
    
    # Features temporelles
    AJOUTER_JOUR_ANNEE = True
    AJOUTER_SEMAINE_ANNEE = True
    AJOUTER_MOIS = True
    
    # Classes imbalancées
    EQUILIBRAGE_SMOTE = True


# ========== PARAMETRES ML ==========
class ParametresML:
    """Paramètres entraînement modèles Machine Learning"""
    
    TEST_SIZE = 0.2
    VALIDATION_SIZE = 0.1
    RANDOM_STATE = 42
    
    # Hyperparamètres XGBoost
    XGBOOST_PARAMS = {
        "max_depth": 6,
        "learning_rate": 0.05,
        "n_estimators": 100,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
    }
    
    # Hyperparamètres Random Forest
    RANDOM_FOREST_PARAMS = {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 5,
        "random_state": RANDOM_STATE,
    }
    
    # Métriques seuil
    SEUIL_PRECISION_ACCEPTABLE = 0.70


# ========== PARAMETRES DEEP LEARNING ==========
class ParametresDL:
    """Paramètres entrainement LSTM"""
    
    # Architecture LSTM
    LSTM_UNITES = [64, 32]
    DROPOUT_RATE = 0.2
    BATCH_SIZE = 32
    EPOCHS = 50
    LEARNING_RATE = 0.001
    
    # Séquences temporelles
    LONGUEUR_SEQUENCE = 8  # 8 semaines en entrée
    PREDICTION_SEMAINES = 1  # Prédire semaine suivante
    
    # Early stopping
    PATIENCE = 10


# ========== PARAMETRES API ==========
class ParametresAPI:
    """Paramètres serveur API"""
    
    TITRE = "API Prédiction Oiseaux Migrateurs"
    VERSION = "1.0.0"
    DESCRIPTION = "Prédiction arrivée oiseaux migrateurs - Nord-Pas-de-Calais"
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
