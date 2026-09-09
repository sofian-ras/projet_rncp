"""
Chargement des donnees traitees, partage par les blocs qui consomment
les fichiers produits par BC01 (bc02, bc03, bc05/dashboard) : evite que
chacun recopie independamment les memes chemins et le meme
pd.read_parquet(...).

Deux sources possibles, selon STORAGE_BACKEND (cf. commun/config.py) :
  - "local" (defaut) : les parquets de donnees/traitees/, versionnes dans
    le depot -> le projet tourne apres un simple clone, sans Docker.
  - "objet" : les collections MongoDB alimentees par BC01 (docker-compose).
Les signatures sont identiques dans les deux cas : les blocs appelants
n'ont pas a savoir d'ou viennent les donnees.
"""

import pandas as pd

from commun.config import REPERTOIRE_DONNEES_TRAITEES, ParametresStockage


def _lire(nom_parquet: str, nom_collection: str, colonnes_dates=()) -> pd.DataFrame:
    """MongoDB si STORAGE_BACKEND=objet, sinon le parquet local correspondant.

    En mode objet, repli automatique sur le parquet local si MongoDB est
    injoignable ou si la collection est vide (ETL BC01 pas encore joue) : la
    demo reste presentable meme sans le service bc01 du docker-compose.
    """
    chemin_parquet = REPERTOIRE_DONNEES_TRAITEES / nom_parquet
    if ParametresStockage.backend_objet():
        try:
            from commun.stockage import ClientMongo

            client = ClientMongo()
            try:
                cadre = client.lire_dataframe(nom_collection, colonnes_dates=colonnes_dates)
            finally:
                client.fermer()
            if not cadre.empty:
                return cadre
        except Exception:
            pass  # repli sur le parquet local ci-dessous
    return pd.read_parquet(chemin_parquet)


def charger_observations_nettoyees() -> pd.DataFrame:
    """Observations GBIF nettoyees (produites par BC01)."""
    return _lire("observations_nettoyees.parquet", "observations_nettoyees", ["date_observation"])


def charger_grille_hebdomadaire() -> pd.DataFrame:
    """Grille presence/absence hebdomadaire (produite par BC01)."""
    return _lire("grille_presence_hebdo.parquet", "grille_presence_hebdo")


def charger_meteo_traitee() -> pd.DataFrame:
    """Donnees meteo nettoyees (produites par BC01)."""
    return _lire("meteo_processed.parquet", "meteo_processed", ["date"])
