"""
BC01 - Nettoyage (ETL) : validation, deduplication et agregation des
observations et de la meteo brutes en donnees exploitables par le ML.

Separe de run.py (qui orchestre acquisition + nettoyage) et de
acquisition.py pour ne pas melanger les deux metiers dans le meme fichier.
"""

import itertools
from pathlib import Path

import pandas as pd
from loguru import logger
from pandas.errors import EmptyDataError

from commun.config import (
    REPERTOIRE_DONNEES_BRUTES,
    REPERTOIRE_DONNEES_TRAITEES,
    ZONE_GEOGRAPHIQUE,
    ParametresNettoyage,
)


class NettoyeurObservations:
    """Valide et nettoie observations GBIF"""

    def __init__(self):
        self.parametres = ParametresNettoyage()

    def charger_et_nettoyer(self, chemin_fichier: Path) -> pd.DataFrame:
        """Charge CSV brut et applique nettoyage complet"""
        logger.info(f"Chargement observations : {chemin_fichier.name}")
        try:
            df = pd.read_csv(chemin_fichier)
        except EmptyDataError:
            logger.warning("  Fichier observations vide : aucune donnee a nettoyer")
            return pd.DataFrame(columns=[
                "espece", "nom_scientifique", "date_observation", "latitude", "longitude",
                "precision_coordinate", "pays", "source", "id_gbif",
            ])

        nb_initial = len(df)
        logger.info(f"  Observations initiales : {nb_initial}")
        if df.empty:
            logger.warning("  Aucune observation disponible apres chargement")
            return df

        df = self._supprimer_valeurs_nulles(df)
        logger.info(f"  Apres suppression nulls : {len(df)} (-{nb_initial - len(df)})")

        df = self._valider_coordonnees(df)
        logger.info(f"  Apres validation coords : {len(df)} (-{nb_initial - len(df)})")

        df = self._filtrer_region(df)
        logger.info(f"  Apres filtrage region : {len(df)}")

        df["date_observation"] = pd.to_datetime(
            df["date_observation"], errors="coerce", format="mixed", utc=True,
        ).dt.tz_localize(None)
        df = df.dropna(subset=["date_observation"])

        nb_avant_doublon = len(df)
        if "id_gbif" in df.columns and df["id_gbif"].notna().any():
            df = df.drop_duplicates(subset=["id_gbif"], keep="first")
        else:
            df = df.drop_duplicates(subset=["espece", "date_observation", "latitude", "longitude"], keep="first")
        logger.info(f"  Apres suppression doublons : {len(df)} (-{nb_avant_doublon - len(df)})")

        return df

    @staticmethod
    def _supprimer_valeurs_nulles(df: pd.DataFrame) -> pd.DataFrame:
        return df.dropna(subset=["latitude", "longitude", "date_observation"])

    def _valider_coordonnees(self, df: pd.DataFrame) -> pd.DataFrame:
        masque_valide = (
            (df["latitude"] >= self.parametres.LATITUDE_MIN) & (df["latitude"] <= self.parametres.LATITUDE_MAX) &
            (df["longitude"] >= self.parametres.LONGITUDE_MIN) & (df["longitude"] <= self.parametres.LONGITUDE_MAX)
        )
        return df[masque_valide]

    def _filtrer_region(self, df: pd.DataFrame) -> pd.DataFrame:
        zone = ZONE_GEOGRAPHIQUE
        masque_region = (
            (df["latitude"] >= zone.latitude_min - 0.5) & (df["latitude"] <= zone.latitude_max + 0.5) &
            (df["longitude"] >= zone.longitude_min - 0.5) & (df["longitude"] <= zone.longitude_max + 0.5)
        )
        return df[masque_region]


class AggregeurTemporel:
    """Agrege observations par semaine + localite en grille presence/absence"""

    @staticmethod
    def creer_grille_hebdomadaire(df_observations: pd.DataFrame, annee_debut: int = 2019, annee_fin: int = 2024) -> pd.DataFrame:
        """Cree grille complete (semaine x espece x localite) et assigne presence/absence"""
        logger.info("Creation grille hebdomadaire...")

        df_observations["annee"] = df_observations["date_observation"].dt.isocalendar().year
        df_observations["semaine"] = df_observations["date_observation"].dt.isocalendar().week
        df_observations["lat_discrete"] = df_observations["latitude"].round(1)
        df_observations["lon_discrete"] = df_observations["longitude"].round(1)

        annees = list(range(annee_debut, annee_fin + 1))
        semaines = list(range(1, 53))
        especes = df_observations["espece"].unique()
        lats = df_observations["lat_discrete"].unique()
        lons = df_observations["lon_discrete"].unique()

        grille = pd.DataFrame(
            itertools.product(annees, semaines, especes, lats, lons),
            columns=["annee", "semaine", "espece", "lat_discrete", "lon_discrete"],
        )

        observations_marquees = df_observations.groupby(
            ["annee", "semaine", "espece", "lat_discrete", "lon_discrete"]
        ).size().reset_index(name="nombre_observations")

        grille = grille.merge(
            observations_marquees,
            on=["annee", "semaine", "espece", "lat_discrete", "lon_discrete"],
            how="left",
        )
        grille["nombre_observations"] = grille["nombre_observations"].fillna(0)
        grille["presence"] = (grille["nombre_observations"] > 0).astype(int)

        logger.info(f"  Grille creee : {len(grille)} lignes")
        logger.info(f"  Equilibre classes : {grille['presence'].value_counts().to_dict()}")
        return grille


def traiter_meteo(chemin_fichier_meteo: Path) -> pd.DataFrame:
    """Charge et nettoie les donnees meteo brutes"""
    if not chemin_fichier_meteo.exists():
        logger.warning(f"Fichier meteo non trouve : {chemin_fichier_meteo}")
        return pd.DataFrame()
    try:
        df_meteo = pd.read_csv(chemin_fichier_meteo)
    except EmptyDataError:
        logger.warning("Fichier meteo vide")
        return pd.DataFrame()
    if df_meteo.empty:
        return df_meteo

    colonnes_attendues = [
        "date", "temperature_max", "temperature_min", "temperature_moyenne",
        "precipitation_sum", "vent_max", "humidite_moyenne", "pression_moyenne",
    ]
    colonnes_presentes = [c for c in colonnes_attendues if c in df_meteo.columns]
    df_meteo = df_meteo[colonnes_presentes].copy()

    if "date" in df_meteo.columns:
        df_meteo["date"] = pd.to_datetime(df_meteo["date"], errors="coerce")
        df_meteo = df_meteo.dropna(subset=["date"])

    for colonne in [c for c in colonnes_presentes if c != "date"]:
        df_meteo[colonne] = pd.to_numeric(df_meteo[colonne], errors="coerce")

    df_meteo = df_meteo.sort_values("date").drop_duplicates(subset=["date"], keep="first")
    logger.info(f"Donnees meteo nettoyees : {len(df_meteo)} lignes")
    return df_meteo


def executer_nettoyage() -> None:
    """Pipeline complet de nettoyage : observations_gbif.csv -> parquets traites"""
    logger.info("=" * 60)
    logger.info("NETTOYAGE (ETL)")
    logger.info("=" * 60)

    nettoyeur = NettoyeurObservations()
    fichier_brut = REPERTOIRE_DONNEES_BRUTES / "observations_gbif.csv"

    if not fichier_brut.exists():
        logger.error(f"Fichier non trouve : {fichier_brut}")
        logger.error("L'etape d'acquisition n'a pas produit de donnees. Relancez le script complet.")
        return

    df_observations = nettoyeur.charger_et_nettoyer(fichier_brut)
    fichier_observations_nettoyees = REPERTOIRE_DONNEES_TRAITEES / "observations_nettoyees.parquet"

    if df_observations.empty:
        logger.warning("Aucune observation exploitable. Sauvegarde d'un parquet vide.")
        df_observations.to_parquet(fichier_observations_nettoyees)
        return

    df_observations.to_parquet(fichier_observations_nettoyees)
    logger.info("Observations nettoyees sauvegardees")

    aggregeur = AggregeurTemporel()
    df_grille = aggregeur.creer_grille_hebdomadaire(df_observations)
    fichier_grille = REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet"
    df_grille.to_parquet(fichier_grille)
    logger.info("Grille hebdomadaire sauvegardee")

    fichier_meteo_brut = REPERTOIRE_DONNEES_BRUTES / "meteo_npdc.csv"
    df_meteo = traiter_meteo(fichier_meteo_brut)
    if not df_meteo.empty:
        fichier_meteo_traite = REPERTOIRE_DONNEES_TRAITEES / "meteo_processed.parquet"
        df_meteo.to_parquet(fichier_meteo_traite)
        logger.info("Donnees meteo traitees sauvegardees")

    logger.info("=" * 60)
    logger.info("BILAN BC01")
    logger.info("=" * 60)
    logger.info(f"Observations nettoyees : {len(df_observations)}")
    logger.info(f"Especes : {df_observations['espece'].nunique()}")
    logger.info(
        f"Plage temporelle : {df_observations['date_observation'].min()} a "
        f"{df_observations['date_observation'].max()}"
    )
    logger.info(f"Lignes de la grille presence/absence : {len(df_grille)}")
