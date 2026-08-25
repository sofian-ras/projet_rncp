"""
Chargement des donnees traitees, partage par les blocs qui consomment
les fichiers produits par BC01 (bc02, bc03, bc05/dashboard) : evite que
chacun recopie independamment les memes chemins et le meme
pd.read_parquet(...).
"""

import pandas as pd

from commun.config import REPERTOIRE_DONNEES_TRAITEES


def charger_observations_nettoyees() -> pd.DataFrame:
    """Observations GBIF nettoyees (produites par BC01)."""
    return pd.read_parquet(REPERTOIRE_DONNEES_TRAITEES / "observations_nettoyees.parquet")


def charger_grille_hebdomadaire() -> pd.DataFrame:
    """Grille presence/absence hebdomadaire (produite par BC01)."""
    return pd.read_parquet(REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet")


def charger_meteo_traitee() -> pd.DataFrame:
    """Donnees meteo nettoyees (produites par BC01)."""
    return pd.read_parquet(REPERTOIRE_DONNEES_TRAITEES / "meteo_processed.parquet")
