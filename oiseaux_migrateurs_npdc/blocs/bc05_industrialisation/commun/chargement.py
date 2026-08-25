"""
Chargement des donnees traitees necessaires au dashboard de BC05
(observations + grille, utilisees pour les onglets Statistiques/Donnees).
"""

import pandas as pd

from commun.config import REPERTOIRE_DONNEES_TRAITEES


def charger_observations_nettoyees() -> pd.DataFrame:
    """Observations GBIF nettoyees (produites par BC01)."""
    return pd.read_parquet(REPERTOIRE_DONNEES_TRAITEES / "observations_nettoyees.parquet")


def charger_grille_hebdomadaire() -> pd.DataFrame:
    """Grille presence/absence hebdomadaire (produite par BC01)."""
    return pd.read_parquet(REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet")
