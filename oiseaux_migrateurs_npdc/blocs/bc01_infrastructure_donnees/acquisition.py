"""
BC01 - Acquisition : telechargement GBIF (observations) + Open-Meteo (meteo).

Code plat (pas de classe) : une fonction = une etape, lisible de haut en bas.
Separe de run.py (qui orchestre) et de nettoyage.py (l'ETL).
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

# URL des deux API publiques utilisees (aucune cle necessaire)
URL_GBIF = "https://api.gbif.org/v1/occurrence/search"
URL_OPEN_METEO = ParametresAcquisition.API_METEO_URL

# Colonnes du CSV d'observations produit par l'acquisition
COLONNES_OBSERVATIONS = [
    "espece", "nom_scientifique", "date_observation", "latitude", "longitude",
    "precision_coordinate", "pays", "source", "id_gbif",
]


def get_avec_retry(url: str, parametres: Dict) -> requests.Response:
    """GET HTTP avec reessais et backoff exponentiel.

    Reessaie sur les erreurs passageres (5xx, 429, timeout, coupure reseau).
    Ne reessaie pas sur une vraie erreur de requete (4xx hors 429), inutile.
    Leve la derniere exception rencontree si toutes les tentatives echouent.
    """
    nb_tentatives = ParametresAcquisition.NB_TENTATIVES_MAX
    delai = ParametresAcquisition.DELAI_RETRY_INITIAL
    derniere_erreur = None

    for tentative in range(1, nb_tentatives + 1):
        try:
            reponse = requests.get(url, params=parametres, timeout=30)
            reponse.raise_for_status()
            return reponse
        except requests.HTTPError as erreur:
            code = erreur.response.status_code if erreur.response is not None else None
            if code is not None and code < 500 and code != 429:
                raise  # 4xx : requete invalide, un reessai ne changera rien
            derniere_erreur = erreur
        except requests.RequestException as erreur:
            derniere_erreur = erreur  # timeout, DNS, connexion refusee...

        if tentative < nb_tentatives:
            logger.warning(
                f"  Tentative {tentative}/{nb_tentatives} echouee ({derniere_erreur}). "
                f"Nouvel essai dans {delai}s..."
            )
            time.sleep(delai)
            delai *= 2

    raise derniere_erreur


# -------------------------------
# GBIF : observations d'oiseaux
# -------------------------------

def creer_bbox_geometrie() -> str:
    """Rectangle de la zone d'etude au format WKT, envoye a GBIF pour le filtre spatial."""
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


def extraire_colonnes(observations: List[Dict], nom_espece: str) -> List[Dict]:
    """Ne garde de chaque observation GBIF que les champs utiles au projet."""
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


def telecharger_observations_espece(nom_espece: str, infos_espece: Dict) -> pd.DataFrame:
    """Telecharge les observations GBIF d'une espece dans la zone, page par page (300 par page)."""
    logger.info(f"Telechargement {infos_espece['nom_francais']}...")

    observations_liste = []
    decalage = 0
    limite = ParametresAcquisition.LIMITE_RESULTATS_PAR_ESPECE
    taille_page = 300

    while decalage < limite:
        parametres = {
            "taxonKey": infos_espece["code_gbif"],
            "geometry": creer_bbox_geometrie(),
            "year": f"{ParametresAcquisition.ANNEE_DEBUT},{ParametresAcquisition.ANNEE_FIN}",
            "hasCoordinate": "true",
            "hasGeospatialIssue": "false",
            "occurrenceStatus": "PRESENT",
            "fields": "gbifID,scientificName,eventDate,decimalLatitude,decimalLongitude,coordinateUncertaintyInMeters,country",
            "limit": min(taille_page, limite - decalage),
            "offset": decalage,
        }
        try:
            reponse = get_avec_retry(URL_GBIF, parametres)
            resultats = reponse.json().get("results", [])
            if not resultats:
                break
            observations_liste.extend(resultats)
            decalage += len(resultats)
            logger.debug(f"  Recupere {len(observations_liste)} observations")
            time.sleep(ParametresAcquisition.DELAI_ENTRE_REQUETES)  # on menage le serveur public
        except Exception as erreur:
            logger.error(f"  Erreur requete GBIF apres {ParametresAcquisition.NB_TENTATIVES_MAX} tentatives : {erreur}")
            break

    df = pd.DataFrame(extraire_colonnes(observations_liste, nom_espece), columns=COLONNES_OBSERVATIONS)
    logger.info(f"  {len(df)} observations telechargees pour {infos_espece['nom_francais']}")
    return df


# ------------------------------
# Open-Meteo : historique meteo
# ------------------------------

def telecharger_meteo(latitude: float, longitude: float, date_debut: str, date_fin: str) -> pd.DataFrame:
    """Telecharge l'historique meteo journalier d'un point (dates au format YYYY-MM-DD)."""
    parametres = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": date_debut,
        "end_date": date_fin,
        "daily": ",".join(ParametresAcquisition.VARIABLES_METEO),
        "timezone": "Europe/Paris",
    }
    try:
        donnees = get_avec_retry(URL_OPEN_METEO, parametres).json()
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


# --------------
# Orchestration
# --------------

def executer_acquisition(forcer: bool = False) -> None:
    """Telecharge les donnees brutes GBIF + Open-Meteo, sauf si deja presentes sur disque."""
    fichier_obs = REPERTOIRE_DONNEES_BRUTES / "observations_gbif.csv"
    fichier_meteo = REPERTOIRE_DONNEES_BRUTES / "meteo_npdc.csv"

    if fichier_obs.exists() and fichier_meteo.exists() and not forcer:
        logger.info("Donnees brutes deja presentes sur disque -> telechargement saute.")
        logger.info("  (utiliser --forcer-telechargement pour re-telecharger depuis GBIF/Open-Meteo)")
        return

    logger.info("=" * 60)
    logger.info("ACQUISITION - Telechargement GBIF + Open-Meteo")
    logger.info("=" * 60)

    # 1. GBIF : une requete paginee par espece, puis on concatene tout
    tables_par_espece = [
        telecharger_observations_espece(nom_espece, infos)
        for nom_espece, infos in ESPECES.items()
    ]
    tables_non_vides = [df for df in tables_par_espece if not df.empty]
    observations = (
        pd.concat(tables_non_vides, ignore_index=True) if tables_non_vides
        else pd.DataFrame(columns=COLONNES_OBSERVATIONS)
    )
    observations = observations.reindex(columns=COLONNES_OBSERVATIONS)
    observations.to_csv(fichier_obs, index=False)
    logger.info(f"Donnees GBIF sauvegardees : {fichier_obs}")

    # 2. Open-Meteo : une seule requete pour tout l'historique au centre de la zone
    logger.info("Telechargement meteo Open-Meteo...")
    df_meteo = telecharger_meteo(
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
