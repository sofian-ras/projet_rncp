"""
Configuration locale a BC03 -- ce bloc est autonome (envoyable/executable
seul, sans le reste du projet), donc cette config est une copie reduite
aux seuls besoins de BC03, et non un import d'un commun/ partage.

donnees/traitees/ contient une copie figee de la grille et de la meteo
traitees, produites par BC01, pour que ce bloc n'ait pas besoin que BC01
ait ete execute a cote de lui.
"""

from pathlib import Path
from datetime import datetime

# ========== CHEMINS (locaux a ce bloc) ==========
REPERTOIRE_RACINE = Path(__file__).resolve().parent.parent
REPERTOIRE_DONNEES_TRAITEES = REPERTOIRE_RACINE / "donnees" / "traitees"
REPERTOIRE_MODELES = REPERTOIRE_RACINE / "modeles"
REPERTOIRE_MODELES.mkdir(parents=True, exist_ok=True)


# ========== PARAMETRES ML ==========
class ParametresML:
    """Parametres entrainement modeles Machine Learning"""

    TEST_SIZE = 0.2
    VALIDATION_SIZE = 0.1
    RANDOM_STATE = 42

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


# ========== LOGGING ==========
FORMAT_LOG = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

FICHIER_LOG = REPERTOIRE_RACINE / "logs" / f"projet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
FICHIER_LOG.parent.mkdir(exist_ok=True)
