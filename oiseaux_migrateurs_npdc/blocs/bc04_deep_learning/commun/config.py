"""
Configuration locale a BC04 -- ce bloc est autonome (envoyable/executable
seul, sans le reste du projet). Aucune donnee d'entree d'un autre bloc
n'est necessaire ici (le jeu de donnees IMDB est telecharge par Keras).
"""

from pathlib import Path
from datetime import datetime

# ========== CHEMINS (locaux a ce bloc) ==========
REPERTOIRE_RACINE = Path(__file__).resolve().parent.parent
REPERTOIRE_MODELES = REPERTOIRE_RACINE / "modeles"
REPERTOIRE_MODELES.mkdir(parents=True, exist_ok=True)


# ========== LOGGING ==========
FORMAT_LOG = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

FICHIER_LOG = REPERTOIRE_RACINE / "logs" / f"projet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
FICHIER_LOG.parent.mkdir(exist_ok=True)


# ========== PARAMETRES DEEP LEARNING ==========
class ParametresDL:
    """Parametres entrainement du modele de Deep Learning (BC04)."""

    NB_MOTS_VOCABULAIRE = 10000
    LONGUEUR_SEQUENCE = 200
    TAILLE_EMBEDDING = 32
    UNITES_LSTM = 32
    DROPOUT_RATE = 0.3
    BATCH_SIZE = 128
    EPOCHS = 5
    TAILLE_ECHANTILLON_DEMO = 6000
    RANDOM_STATE = 42
