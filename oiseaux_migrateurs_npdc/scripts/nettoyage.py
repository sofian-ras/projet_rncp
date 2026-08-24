"""
BC01 - Nettoyage et validation des donnees
ETL pipeline : observations + meteo
"""

import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple, Optional

import pandas as pd
import numpy as np
from pandas.errors import EmptyDataError
from loguru import logger

from config import (
    ZONE_GEOGRAPHIQUE,
    REPERTOIRE_DONNEES_BRUTES,
    REPERTOIRE_DONNEES_TRAITEES,
    ParametresNettoyage,
    FORMAT_LOG,
    FICHIER_LOG,
)

logger.remove()
logger.add(lambda msg: print(msg, end=""), format=FORMAT_LOG)
logger.add(FICHIER_LOG, format=FORMAT_LOG)


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
            return pd.DataFrame(
                columns=[
                    "espece",
                    "nom_scientifique",
                    "date_observation",
                    "latitude",
                    "longitude",
                    "precision_coordinate",
                    "pays",
                    "source",
                    "id_gbif",
                ]
            )

        nb_initial = len(df)
        logger.info(f"  Observations initiales : {nb_initial}")

        if df.empty:
            logger.warning("  Aucune observation disponible apres chargement")
            return df
        
        # Etape 1 : Supprimer nulls
        df = self._supprimer_valeurs_nulles(df)
        logger.info(f"  Apres suppression nulls : {len(df)} (-{nb_initial - len(df)})")
        
        # Etape 2 : Valider coordonnees
        df = self._valider_coordonnees(df)
        logger.info(f"  Apres validation coords : {len(df)} (-{nb_initial - len(df)})")
        
        # Etape 3 : Filtrer region NPDC
        df = self._filtrer_region(df)
        logger.info(f"  Apres filtrage region : {len(df)}")
        
        # Etape 4 : Formater dates (GBIF peut mixer date simple et timestamp)
        df["date_observation"] = pd.to_datetime(
            df["date_observation"],
            errors="coerce",
            format="mixed",
            utc=True,
        ).dt.tz_localize(None)
        df = df.dropna(subset=["date_observation"])
        
        # Etape 5 : Supprimer doublons
        nb_avant_doublon = len(df)
        if "id_gbif" in df.columns and df["id_gbif"].notna().any():
            df = df.drop_duplicates(subset=["id_gbif"], keep="first")
        else:
            df = df.drop_duplicates(
                subset=["espece", "date_observation", "latitude", "longitude"],
                keep="first"
            )
        logger.info(f"  Apres suppression doublons : {len(df)} (-{nb_avant_doublon - len(df)})")
        
        return df
    
    @staticmethod
    def _supprimer_valeurs_nulles(df: pd.DataFrame) -> pd.DataFrame:
        """Supprime lignes avec valeurs critiques nulles"""
        colonnes_critiques = ["latitude", "longitude", "date_observation"]
        return df.dropna(subset=colonnes_critiques)
    
    def _valider_coordonnees(self, df: pd.DataFrame) -> pd.DataFrame:
        """Valide plages latitude/longitude"""
        masque_valide = (
            (df["latitude"] >= self.parametres.LATITUDE_MIN) &
            (df["latitude"] <= self.parametres.LATITUDE_MAX) &
            (df["longitude"] >= self.parametres.LONGITUDE_MIN) &
            (df["longitude"] <= self.parametres.LONGITUDE_MAX)
        )
        return df[masque_valide]
    
    def _filtrer_region(self, df: pd.DataFrame) -> pd.DataFrame:
        """Garde seulement observations NPDC + buffer"""
        zone = ZONE_GEOGRAPHIQUE
        
        masque_region = (
            (df["latitude"] >= zone.latitude_min - 0.5) &
            (df["latitude"] <= zone.latitude_max + 0.5) &
            (df["longitude"] >= zone.longitude_min - 0.5) &
            (df["longitude"] <= zone.longitude_max + 0.5)
        )
        
        return df[masque_region]


class AggregeurTemporel:
    """Agrege observations par semaine + periode"""
    
    @staticmethod
    def creer_grille_hebdomadaire(
        df_observations: pd.DataFrame,
        annee_debut: int = 2015,
        annee_fin: int = 2024
    ) -> pd.DataFrame:
        """
        Cree grille complete (semaine x espece x localite)
        Assigne presence/absence
        """
        logger.info("Creation grille hebdomadaire...")
        
        # Extraire annee et semaine
        df_observations["annee"] = df_observations["date_observation"].dt.isocalendar().year
        df_observations["semaine"] = df_observations["date_observation"].dt.isocalendar().week
        
        # Discretiser coordonnees (grille 0.1deg x 0.1deg)
        df_observations["lat_discrete"] = (
            df_observations["latitude"].round(1)
        )
        df_observations["lon_discrete"] = (
            df_observations["longitude"].round(1)
        )
        
        # Creer grille complete
        annees = list(range(annee_debut, annee_fin + 1))
        semaines = list(range(1, 53))
        especes = df_observations["espece"].unique()
        lats = df_observations["lat_discrete"].unique()
        lons = df_observations["lon_discrete"].unique()
        
        import itertools
        grille = pd.DataFrame(
            itertools.product(annees, semaines, especes, lats, lons),
            columns=["annee", "semaine", "espece", "lat_discrete", "lon_discrete"]
        )
        
        # Marquer presence si observation
        observations_marquees = df_observations.groupby(
            ["annee", "semaine", "espece", "lat_discrete", "lon_discrete"]
        ).size().reset_index(name="nombre_observations")
        
        grille = grille.merge(
            observations_marquees,
            on=["annee", "semaine", "espece", "lat_discrete", "lon_discrete"],
            how="left"
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
        logger.warning("Aucune donnee meteo disponible")
        return df_meteo

    colonnes_attendues = [
        "date",
        "temperature_max",
        "temperature_min",
        "temperature_moyenne",
        "precipitation_sum",
        "vent_max",
        "humidite_moyenne",
        "pression_moyenne",
    ]
    colonnes_presentes = [col for col in colonnes_attendues if col in df_meteo.columns]
    df_meteo = df_meteo[colonnes_presentes].copy()

    if "date" in df_meteo.columns:
        df_meteo["date"] = pd.to_datetime(df_meteo["date"], errors="coerce")
        df_meteo = df_meteo.dropna(subset=["date"])

    for colonne in [c for c in colonnes_presentes if c != "date"]:
        df_meteo[colonne] = pd.to_numeric(df_meteo[colonne], errors="coerce")

    df_meteo = df_meteo.sort_values("date").drop_duplicates(subset=["date"], keep="first")
    logger.info(f"Donnees meteo nettoyees : {len(df_meteo)} lignes")
    return df_meteo


def executer_nettoyage():
    """Pipeline complet nettoyage"""
    logger.info("=" * 60)
    logger.info("DEBUT NETTOYAGE ET ETL")
    logger.info("=" * 60)
    
    # Charger et nettoyer observations GBIF
    nettoyeur = NettoyeurObservations()
    fichier_brut = REPERTOIRE_DONNEES_BRUTES / "observations_gbif.csv"
    
    if not fichier_brut.exists():
        logger.error(f"Fichier non trouve : {fichier_brut}")
        logger.error("Executez d'abord scripts/acquisition.py")
        return
    
    df_observations = nettoyeur.charger_et_nettoyer(fichier_brut)

    if df_observations.empty:
        logger.warning("Aucune observation exploitable. Sauvegarde d'un parquet vide et arret du pipeline ETL.")

        fichier_observations_nettoyees = (
            REPERTOIRE_DONNEES_TRAITEES / "observations_nettoyees.parquet"
        )
        df_observations.to_parquet(fichier_observations_nettoyees)
        logger.info("Observations nettoyees (vides) sauvegardees")

        logger.info("NETTOYAGE TERMINE (sans donnees observations)")
        return
    
    # Sauvegarder observations nettoyees
    fichier_observations_nettoyees = (
        REPERTOIRE_DONNEES_TRAITEES / "observations_nettoyees.parquet"
    )
    df_observations.to_parquet(fichier_observations_nettoyees)
    logger.info("Observations nettoyees sauvegardees")
    
    # Creer grille hebdomadaire
    aggregeur = AggregeurTemporel()
    df_grille = aggregeur.creer_grille_hebdomadaire(df_observations)
    
    # Sauvegarder grille
    fichier_grille = REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet"
    df_grille.to_parquet(fichier_grille)
    logger.info("Grille hebdomadaire sauvegardee")

    # Nettoyer et sauvegarder meteo
    fichier_meteo_brut = REPERTOIRE_DONNEES_BRUTES / "meteo_npdc.csv"
    df_meteo = traiter_meteo(fichier_meteo_brut)
    if not df_meteo.empty:
        fichier_meteo_traite = REPERTOIRE_DONNEES_TRAITEES / "meteo_processed.parquet"
        df_meteo.to_parquet(fichier_meteo_traite)
        logger.info("Donnees meteo traitees sauvegardees")

    # Statistiques finales
    logger.info("=" * 60)
    logger.info("STATISTIQUES FINALES")
    logger.info("=" * 60)
    logger.info(f"Total observations nettoyees : {len(df_observations)}")
    logger.info(f"Especes : {df_observations['espece'].nunique()}")
    logger.info(f"Plage temporelle : {df_observations['date_observation'].min()} a {df_observations['date_observation'].max()}")
    logger.info(f"Zone geographique : {df_observations['latitude'].min():.2f} deg N a {df_observations['latitude'].max():.2f} deg N")
    
    logger.info("=" * 60)
    logger.info("NETTOYAGE TERMINE")
    logger.info("=" * 60)


if __name__ == "__main__":
    executer_nettoyage()
