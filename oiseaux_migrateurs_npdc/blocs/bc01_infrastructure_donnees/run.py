"""
BC01 - Infrastructure de donnees
=================================

Ce script est AUTONOME : il peut etre lance seul, sans avoir besoin
qu'un autre bloc ait ete execute avant lui.

Il fait deux choses, dans l'ordre :
  1. ACQUISITION : telecharge les observations d'oiseaux (GBIF) et la
     meteo historique (Open-Meteo) -> donnees/brutes/*.csv
  2. NETTOYAGE (ETL) : valide, deduplique, et transforme ces donnees
     brutes en une grille hebdomadaire presence/absence exploitable
     par le Machine Learning -> donnees/traitees/*.parquet

Utilisation :
    python blocs/bc01_infrastructure_donnees/run.py
    python blocs/bc01_infrastructure_donnees/run.py --forcer-telechargement

Par defaut, si les fichiers bruts existent deja sur disque, l'etape de
telechargement est sautee (pour une demonstration rapide et qui ne
depend pas d'internet) ; utiliser --forcer-telechargement pour tout
re-telecharger depuis les API.
"""

import argparse
import itertools
import sys
import time
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests
from loguru import logger
from pandas.errors import EmptyDataError

# --- Rendre le script executable seul : on ajoute la racine du projet ---
RACINE_PROJET = Path(__file__).resolve().parents[2]
if str(RACINE_PROJET) not in sys.path:
    sys.path.insert(0, str(RACINE_PROJET))

from commun.config import (  # noqa: E402
    ESPECES,
    ZONE_GEOGRAPHIQUE,
    REPERTOIRE_DONNEES_BRUTES,
    REPERTOIRE_DONNEES_TRAITEES,
    ParametresAcquisition,
    ParametresNettoyage,
    FORMAT_LOG,
    FICHIER_LOG,
)

logger.remove()
logger.add(lambda msg: print(msg, end=""), format=FORMAT_LOG)
logger.add(FICHIER_LOG, format=FORMAT_LOG)


# ======================================================================
# PARTIE 1 : ACQUISITION (telechargement GBIF + Open-Meteo)
# ======================================================================

class AcquisiteurGBIF:
    """Telecharge observations d'oiseaux depuis GBIF"""

    COLONNES_OBSERVATIONS = [
        "espece", "nom_scientifique", "date_observation", "latitude", "longitude",
        "precision_coordinate", "pays", "source", "id_gbif",
    ]

    def __init__(self):
        self.url_base_gbif = "https://api.gbif.org/v1/occurrence/search"
        self.params_acquisition = ParametresAcquisition()

    def telecharger_observations_espece(self, nom_espece: str, infos_espece: Dict) -> pd.DataFrame:
        """Telecharge toutes les observations GBIF pour une espece dans la region NPDC"""
        logger.info(f"Telechargement {infos_espece['nom_francais']}...")

        observations_liste = []
        decalage = 0
        limite = self.params_acquisition.LIMITE_RESULTATS_PAR_ESPECE
        taille_page = 300

        while decalage < limite:
            parametres = {
                "taxonKey": infos_espece["code_gbif"],
                "geometry": self._creer_bbox_geometrie(),
                "year": f"{self.params_acquisition.ANNEE_DEBUT},{self.params_acquisition.ANNEE_FIN}",
                "hasCoordinate": "true",
                "hasGeospatialIssue": "false",
                "occurrenceStatus": "PRESENT",
                "fields": "gbifID,scientificName,eventDate,decimalLatitude,decimalLongitude,coordinateUncertaintyInMeters,country",
                "limit": min(taille_page, limite - decalage),
                "offset": decalage,
            }
            try:
                reponse = requests.get(self.url_base_gbif, params=parametres, timeout=30)
                reponse.raise_for_status()
                resultats = reponse.json().get("results", [])
                if not resultats:
                    break
                observations_liste.extend(resultats)
                decalage += len(resultats)
                logger.debug(f"  Recupere {len(observations_liste)} observations")
                time.sleep(self.params_acquisition.DELAI_ENTRE_REQUETES)
            except Exception as erreur:
                logger.error(f"  Erreur requete GBIF : {erreur}")
                break

        donnees_extraites = self._extraire_colonnes(observations_liste, nom_espece)
        df = pd.DataFrame(donnees_extraites, columns=self.COLONNES_OBSERVATIONS)
        logger.info(f"  {len(df)} observations telechargees pour {infos_espece['nom_francais']}")
        return df

    def _creer_bbox_geometrie(self) -> str:
        """Cree geometrie WKT pour filtrer par region"""
        zone = ZONE_GEOGRAPHIQUE
        return (
            f"POLYGON(("
            f"{zone.longitude_min} {zone.latitude_min},"
            f"{zone.longitude_max} {zone.latitude_min},"
            f"{zone.longitude_max} {zone.latitude_max},"
            f"{zone.longitude_min} {zone.latitude_max},"
            f"{zone.longitude_min} {zone.latitude_min}"
            f"))"
        )

    @staticmethod
    def _extraire_colonnes(observations: List[Dict], nom_espece: str) -> List[Dict]:
        donnees = []
        for obs in observations:
            donnees.append({
                "espece": nom_espece,
                "nom_scientifique": obs.get("scientificName", ""),
                "date_observation": obs.get("eventDate", ""),
                "latitude": obs.get("decimalLatitude"),
                "longitude": obs.get("decimalLongitude"),
                "precision_coordinate": obs.get("coordinateUncertaintyInMeters"),
                "pays": obs.get("country", ""),
                "source": "GBIF",
                "id_gbif": obs.get("gbifID"),
            })
        return donnees


class AcquisiteurMeteo:
    """Telecharge donnees meteorologiques depuis Open-Meteo"""

    def __init__(self):
        self.url_api = ParametresAcquisition.API_METEO_URL

    def telecharger_meteo(self, latitude: float, longitude: float, date_debut: str, date_fin: str) -> pd.DataFrame:
        """Telecharge historique meteo pour une localite et periode (format date : YYYY-MM-DD)"""
        parametres = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": date_debut,
            "end_date": date_fin,
            "daily": ",".join(ParametresAcquisition.VARIABLES_METEO),
            "timezone": "Europe/Paris",
        }
        try:
            reponse = requests.get(self.url_api, params=parametres, timeout=30)
            reponse.raise_for_status()
            donnees = reponse.json()
            return pd.DataFrame({
                "date": pd.to_datetime(donnees["daily"]["time"]),
                "temperature_max": donnees["daily"]["temperature_2m_max"],
                "temperature_min": donnees["daily"]["temperature_2m_min"],
                "temperature_moyenne": donnees["daily"]["temperature_2m_mean"],
                "precipitation_sum": donnees["daily"]["precipitation_sum"],
                "vent_max": donnees["daily"]["windspeed_10m_max"],
                "humidite_moyenne": donnees["daily"]["relative_humidity_2m_mean"],
                "pression_moyenne": donnees["daily"]["pressure_msl_mean"],
                "latitude": latitude,
                "longitude": longitude,
            })
        except Exception as erreur:
            logger.error(f"Erreur telechargement meteo : {erreur}")
            return pd.DataFrame()


def executer_acquisition(forcer: bool = False) -> None:
    """Telecharge les donnees brutes GBIF + Open-Meteo, sauf si deja presentes sur disque"""
    fichier_obs = REPERTOIRE_DONNEES_BRUTES / "observations_gbif.csv"
    fichier_meteo = REPERTOIRE_DONNEES_BRUTES / "meteo_npdc.csv"

    if fichier_obs.exists() and fichier_meteo.exists() and not forcer:
        logger.info("Donnees brutes deja presentes sur disque -> telechargement saute.")
        logger.info(f"  (utiliser --forcer-telechargement pour re-telecharger depuis GBIF/Open-Meteo)")
        return

    logger.info("=" * 60)
    logger.info("ACQUISITION - Telechargement GBIF + Open-Meteo")
    logger.info("=" * 60)

    acquisiteur_gbif = AcquisiteurGBIF()
    donnees_gbif_liste = [
        acquisiteur_gbif.telecharger_observations_espece(nom_espece, infos)
        for nom_espece, infos in ESPECES.items()
    ]

    donnees_non_vides = [df for df in donnees_gbif_liste if not df.empty]
    donnees_gbif_globales = (
        pd.concat(donnees_non_vides, ignore_index=True) if donnees_non_vides
        else pd.DataFrame(columns=AcquisiteurGBIF.COLONNES_OBSERVATIONS)
    )
    donnees_gbif_globales = donnees_gbif_globales.reindex(columns=AcquisiteurGBIF.COLONNES_OBSERVATIONS)
    donnees_gbif_globales.to_csv(fichier_obs, index=False)
    logger.info(f"Donnees GBIF sauvegardees : {fichier_obs}")

    logger.info("Telechargement meteo Open-Meteo...")
    acquisiteur_meteo = AcquisiteurMeteo()
    df_meteo = acquisiteur_meteo.telecharger_meteo(
        latitude=ZONE_GEOGRAPHIQUE.centre_latitude,
        longitude=ZONE_GEOGRAPHIQUE.centre_longitude,
        date_debut=f"{ParametresAcquisition.ANNEE_DEBUT}-01-01",
        date_fin=f"{ParametresAcquisition.ANNEE_FIN}-12-31",
    )
    if not df_meteo.empty:
        df_meteo.to_csv(fichier_meteo, index=False)
        logger.info(f"Donnees meteo sauvegardees : {fichier_meteo}")
    else:
        logger.warning("Donnees meteo non recuperees (le pipeline continue avec GBIF seul)")


# ======================================================================
# PARTIE 2 : NETTOYAGE (ETL)
# ======================================================================

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
    def creer_grille_hebdomadaire(df_observations: pd.DataFrame, annee_debut: int = 2015, annee_fin: int = 2024) -> pd.DataFrame:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="BC01 - Infrastructure de donnees (acquisition + nettoyage)")
    parser.add_argument(
        "--forcer-telechargement", action="store_true",
        help="Re-telecharge les donnees depuis GBIF/Open-Meteo meme si des fichiers bruts existent deja.",
    )
    args = parser.parse_args()

    print("\n" + "#" * 70)
    print("# BC01 - INFRASTRUCTURE DE DONNEES")
    print("#" * 70 + "\n")

    executer_acquisition(forcer=args.forcer_telechargement)
    executer_nettoyage()

    print("\nPreuves produites (fichiers verifiables sur disque) :")
    for chemin in [
        REPERTOIRE_DONNEES_BRUTES / "observations_gbif.csv",
        REPERTOIRE_DONNEES_BRUTES / "meteo_npdc.csv",
        REPERTOIRE_DONNEES_TRAITEES / "observations_nettoyees.parquet",
        REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet",
        REPERTOIRE_DONNEES_TRAITEES / "meteo_processed.parquet",
    ]:
        marque = "OK" if chemin.exists() else "MANQUANT"
        print(f"  [{marque}] {chemin.relative_to(RACINE_PROJET)}")

    print("\nBC01 termine. Bloc suivant : blocs/bc02_analyse_exploratoire/run.py\n")


if __name__ == "__main__":
    main()
