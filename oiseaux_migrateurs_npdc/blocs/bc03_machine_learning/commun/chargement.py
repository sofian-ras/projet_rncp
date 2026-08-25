"""
Chargement des donnees traitees necessaires a BC03 (grille + meteo,
observations non necessaires ici).
"""

import pandas as pd

from commun.config import REPERTOIRE_DONNEES_TRAITEES


def charger_grille_hebdomadaire() -> pd.DataFrame:
    """Grille presence/absence hebdomadaire (produite par BC01)."""
    return pd.read_parquet(REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet")


def charger_meteo_traitee() -> pd.DataFrame:
    """Donnees meteo nettoyees (produites par BC01)."""
    return pd.read_parquet(REPERTOIRE_DONNEES_TRAITEES / "meteo_processed.parquet")
