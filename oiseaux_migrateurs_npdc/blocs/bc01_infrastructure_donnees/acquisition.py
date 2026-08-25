"""
BC01 - Acquisition : telechargement GBIF (observations) + Open-Meteo (meteo).

Separe de run.py (qui orchestre acquisition + nettoyage) pour ne pas
melanger les deux metiers dans le meme fichier.
"""

import time
from typing import Dict, List

import pandas as pd
import requests
from loguru import logger

from commun.config import (
    ESPECES,
    ZONE_GEOGRAPHIQUE,
    REPERTOIRE_DONNEES_BRUTES,
    ParametresAcquisition,
)


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
        logger.info("  (utiliser --forcer-telechargement pour re-telecharger depuis GBIF/Open-Meteo)")
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
