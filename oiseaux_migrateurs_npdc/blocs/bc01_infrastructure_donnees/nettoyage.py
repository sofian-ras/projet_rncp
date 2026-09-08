"""
BC01 - Nettoyage (ETL) : validation, deduplication et agregation des
observations et de la meteo brutes en donnees exploitables par le ML.

Code plat (pas de classe) : une fonction = une etape, lisible de haut en bas.
Separe de run.py (qui orchestre) et de acquisition.py (le telechargement).
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

COLONNES_OBSERVATIONS = [
    "espece", "nom_scientifique", "date_observation", "latitude", "longitude",
    "precision_coordinate", "pays", "source", "id_gbif",
]


# ---------------------------------------------------------------------------
# Nettoyage des observations : 5 etapes appliquees dans l'ordre
# ---------------------------------------------------------------------------

def supprimer_valeurs_nulles(df: pd.DataFrame) -> pd.DataFrame:
    """Etape 1 : retire les lignes sans coordonnees ou sans date (inexploitables)."""
    return df.dropna(subset=["latitude", "longitude", "date_observation"])


def valider_coordonnees(df: pd.DataFrame) -> pd.DataFrame:
    """Etape 2 : rejette les latitudes/longitudes hors de toute plage plausible."""
    p = ParametresNettoyage
    masque = (
        (df["latitude"] >= p.LATITUDE_MIN) & (df["latitude"] <= p.LATITUDE_MAX) &
        (df["longitude"] >= p.LONGITUDE_MIN) & (df["longitude"] <= p.LONGITUDE_MAX)
    )
    return df[masque]


def filtrer_region(df: pd.DataFrame) -> pd.DataFrame:
    """Etape 3 : ne garde que les points dans le Nord-Pas-de-Calais (+ 0,5 deg de marge)."""
    zone = ZONE_GEOGRAPHIQUE
    masque = (
        (df["latitude"] >= zone.latitude_min - 0.5) & (df["latitude"] <= zone.latitude_max + 0.5) &
        (df["longitude"] >= zone.longitude_min - 0.5) & (df["longitude"] <= zone.longitude_max + 0.5)
    )
    return df[masque]


def charger_et_nettoyer(chemin_fichier: Path) -> pd.DataFrame:
    """Charge le CSV brut et enchaine les 5 etapes de nettoyage."""
    logger.info(f"Chargement observations : {chemin_fichier.name}")
    try:
        df = pd.read_csv(chemin_fichier)
    except EmptyDataError:
        logger.warning("  Fichier observations vide : aucune donnee a nettoyer")
        return pd.DataFrame(columns=COLONNES_OBSERVATIONS)

    nb_initial = len(df)
    logger.info(f"  Observations initiales : {nb_initial}")
    if df.empty:
        logger.warning("  Aucune observation disponible apres chargement")
        return df

    df = supprimer_valeurs_nulles(df)
    logger.info(f"  Apres suppression nulls : {len(df)} (-{nb_initial - len(df)})")

    df = valider_coordonnees(df)
    logger.info(f"  Apres validation coords : {len(df)} (-{nb_initial - len(df)})")

    df = filtrer_region(df)
    logger.info(f"  Apres filtrage region : {len(df)}")

    # Etape 4 : uniformiser les dates (GBIF renvoie des formats varies)
    df["date_observation"] = pd.to_datetime(
        df["date_observation"], errors="coerce", format="mixed", utc=True,
    ).dt.tz_localize(None)
    df = df.dropna(subset=["date_observation"])

    # Etape 5 : retirer les doublons (meme id_gbif = meme signalement republie)
    nb_avant_doublon = len(df)
    if "id_gbif" in df.columns and df["id_gbif"].notna().any():
        df = df.drop_duplicates(subset=["id_gbif"], keep="first")
    else:
        df = df.drop_duplicates(subset=["espece", "date_observation", "latitude", "longitude"], keep="first")
    logger.info(f"  Apres suppression doublons : {len(df)} (-{nb_avant_doublon - len(df)})")

    return df


# ---------------------------------------------------------------------------
# Transformation cle : grille hebdomadaire presence/absence
# ---------------------------------------------------------------------------

def creer_grille_hebdomadaire(
    df_observations: pd.DataFrame, annee_debut: int = 2019, annee_fin: int = 2024
) -> pd.DataFrame:
    """Construit la grille complete (annee x semaine x espece x maille) et marque presence/absence.

    Chaque case vaut 1 si au moins une observation y tombe, 0 sinon : c'est la
    facon de fabriquer des exemples negatifs (absences) que GBIF ne fournit pas.
    """
    logger.info("Creation grille hebdomadaire...")

    # Discretisation : semaine ISO + maille geographique de 0,1 deg
    df_observations["annee"] = df_observations["date_observation"].dt.isocalendar().year
    df_observations["semaine"] = df_observations["date_observation"].dt.isocalendar().week
    df_observations["lat_discrete"] = df_observations["latitude"].round(1)
    df_observations["lon_discrete"] = df_observations["longitude"].round(1)

    # Toutes les combinaisons possibles (produit cartesien)
    annees = list(range(annee_debut, annee_fin + 1))
    semaines = list(range(1, 53))
    especes = df_observations["espece"].unique()
    lats = df_observations["lat_discrete"].unique()
    lons = df_observations["lon_discrete"].unique()
    grille = pd.DataFrame(
        itertools.product(annees, semaines, especes, lats, lons),
        columns=["annee", "semaine", "espece", "lat_discrete", "lon_discrete"],
    )

    # Nombre d'observations par case, puis presence = (au moins une observation)
    observations_par_case = df_observations.groupby(
        ["annee", "semaine", "espece", "lat_discrete", "lon_discrete"]
    ).size().reset_index(name="nombre_observations")

    grille = grille.merge(
        observations_par_case,
        on=["annee", "semaine", "espece", "lat_discrete", "lon_discrete"],
        how="left",
    )
    grille["nombre_observations"] = grille["nombre_observations"].fillna(0)
    grille["presence"] = (grille["nombre_observations"] > 0).astype(int)

    logger.info(f"  Grille creee : {len(grille)} lignes")
    logger.info(f"  Equilibre classes : {grille['presence'].value_counts().to_dict()}")
    return grille


# ---------------------------------------------------------------------------
# Nettoyage de la meteo
# ---------------------------------------------------------------------------

def traiter_meteo(chemin_fichier_meteo: Path) -> pd.DataFrame:
    """Charge et nettoie la meteo brute : typage des colonnes, tri par date, deduplication."""
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


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def executer_nettoyage() -> None:
    """Pipeline complet : observations_gbif.csv + meteo_npdc.csv -> parquets traites."""
    logger.info("=" * 60)
    logger.info("NETTOYAGE (ETL)")
    logger.info("=" * 60)

    fichier_brut = REPERTOIRE_DONNEES_BRUTES / "observations_gbif.csv"
    if not fichier_brut.exists():
        logger.error(f"Fichier non trouve : {fichier_brut}")
        logger.error("L'etape d'acquisition n'a pas produit de donnees. Relancez le script complet.")
        return

    df_observations = charger_et_nettoyer(fichier_brut)
    fichier_observations_nettoyees = REPERTOIRE_DONNEES_TRAITEES / "observations_nettoyees.parquet"

    if df_observations.empty:
        logger.warning("Aucune observation exploitable. Sauvegarde d'un parquet vide.")
        df_observations.to_parquet(fichier_observations_nettoyees)
        return

    df_observations.to_parquet(fichier_observations_nettoyees)
    logger.info("Observations nettoyees sauvegardees")

    df_grille = creer_grille_hebdomadaire(df_observations)
    df_grille.to_parquet(REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet")
    logger.info("Grille hebdomadaire sauvegardee")

    df_meteo = traiter_meteo(REPERTOIRE_DONNEES_BRUTES / "meteo_npdc.csv")
    if not df_meteo.empty:
        df_meteo.to_parquet(REPERTOIRE_DONNEES_TRAITEES / "meteo_processed.parquet")
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
