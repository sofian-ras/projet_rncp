"""
BC01 - Acquisition de données GBIF et Open-Meteo
Télécharge les observations d'oiseaux et données météorologiques
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import logging

import pandas as pd
import requests
from tqdm import tqdm
from loguru import logger

from config import (
    ESPECES,
    ZONE_GEOGRAPHIQUE,
    REPERTOIRE_DONNEES_BRUTES,
    ParametresAcquisition,
    FORMAT_LOG,
    FICHIER_LOG,
)

# Configuration logging
logger.remove()
logger.add(lambda msg: print(msg, end=""), format=FORMAT_LOG)
logger.add(FICHIER_LOG, format=FORMAT_LOG)


class AcquisiteurGBIF:
    """Télécharge observations d'oiseaux depuis GBIF"""

    COLONNES_OBSERVATIONS = [
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
    
    def __init__(self):
        self.url_base_gbif = "https://api.gbif.org/v1/occurrence/search"
        self.params_acquisition = ParametresAcquisition()
        
    def telecharger_observations_espece(
        self,
        nom_espece: str,
        infos_espece: Dict
    ) -> pd.DataFrame:
        """
        Télécharge toutes les observations GBIF pour une espèce
        dans la région Nord-Pas-de-Calais
        """
        logger.info(f"🐦 Téléchargement {infos_espece['nom_francais']}...")
        
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
                reponse = requests.get(
                    self.url_base_gbif,
                    params=parametres,
                    timeout=30
                )
                reponse.raise_for_status()
                donnees = reponse.json()
                
                resultats = donnees.get("results", [])
                if not resultats:
                    break
                
                observations_liste.extend(resultats)
                decalage += len(resultats)
                
                logger.debug(
                    f"  ✓ Récupéré {len(observations_liste)} observations"
                )
                time.sleep(self.params_acquisition.DELAI_ENTRE_REQUETES)
                
            except Exception as erreur:
                logger.error(f"  ✗ Erreur requête GBIF : {erreur}")
                break
        
        # Transformer en DataFrame
        donnees_extraites = self._extraire_colonnes(observations_liste, nom_espece)
        df = pd.DataFrame(donnees_extraites, columns=self.COLONNES_OBSERVATIONS)
        
        logger.info(
            f"  ✓ {len(df)} observations téléchargées pour {infos_espece['nom_francais']}"
        )
        return df
    
    def _creer_bbox_geometrie(self) -> str:
        """Crée géométrie WKT pour filtrer par région"""
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
        """Extrait colonnes pertinentes"""
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
    """Télécharge données météorologiques depuis Open-Meteo"""
    
    def __init__(self):
        self.url_api = ParametresAcquisition.API_METEO_URL
        
    def telecharger_meteo(
        self,
        latitude: float,
        longitude: float,
        date_debut: str,
        date_fin: str
    ) -> pd.DataFrame:
        """
        Télécharge historique météo pour une localité et période
        Format date : "YYYY-MM-DD"
        """
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
            
            df = pd.DataFrame({
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
            
            return df
            
        except Exception as erreur:
            logger.error(f"Erreur téléchargement météo : {erreur}")
            return pd.DataFrame()


def executer_acquisition():
    """Exécute complet d'acquisition"""
    logger.info("=" * 60)
    logger.info("🌍 DEBUT ACQUISITION DONNEES")
    logger.info("=" * 60)
    
    acquisiteur_gbif = AcquisiteurGBIF()
    
    # Télécharger observations par espèce
    donnees_gbif_liste = []
    for nom_espece, infos in ESPECES.items():
        df = acquisiteur_gbif.telecharger_observations_espece(nom_espece, infos)
        donnees_gbif_liste.append(df)
    
    # Fusionner tous données
    donnees_non_vides = [df for df in donnees_gbif_liste if not df.empty]
    if donnees_non_vides:
        donnees_gbif_globales = pd.concat(donnees_non_vides, ignore_index=True)
    else:
        donnees_gbif_globales = pd.DataFrame(columns=AcquisiteurGBIF.COLONNES_OBSERVATIONS)
    donnees_gbif_globales = donnees_gbif_globales.reindex(
        columns=AcquisiteurGBIF.COLONNES_OBSERVATIONS
    )
    
    # Sauvegarder brute
    fichier_sortie = REPERTOIRE_DONNEES_BRUTES / "observations_gbif.csv"
    donnees_gbif_globales.to_csv(fichier_sortie, index=False)
    logger.info(f"✓ Données GBIF sauvegardées : {fichier_sortie}")

    # Télécharger météo régionale (centre NPDC)
    logger.info("🌦️ Téléchargement météo Open-Meteo...")
    acquisiteur_meteo = AcquisiteurMeteo()
    date_debut = f"{ParametresAcquisition.ANNEE_DEBUT}-01-01"
    date_fin = f"{ParametresAcquisition.ANNEE_FIN}-12-31"

    df_meteo = acquisiteur_meteo.telecharger_meteo(
        latitude=ZONE_GEOGRAPHIQUE.centre_latitude,
        longitude=ZONE_GEOGRAPHIQUE.centre_longitude,
        date_debut=date_debut,
        date_fin=date_fin,
    )

    if not df_meteo.empty:
        fichier_meteo = REPERTOIRE_DONNEES_BRUTES / "meteo_npdc.csv"
        df_meteo.to_csv(fichier_meteo, index=False)
        logger.info(f"✓ Données météo sauvegardées : {fichier_meteo}")
    else:
        logger.warning("⚠️ Données météo non récupérées (pipeline poursuit avec GBIF)")
    
    logger.info("=" * 60)
    logger.info("✓ ACQUISITION TERMINEE")
    logger.info("=" * 60)


if __name__ == "__main__":
    executer_acquisition()
