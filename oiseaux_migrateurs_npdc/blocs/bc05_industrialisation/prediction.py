"""
BC05 - Logique de prediction partagee entre l'API (api.py::predire_presence)
et la demonstration hors-serveur (run.py::demo_prediction).

Avant ce module, la construction des features et le calcul de la
confiance etaient recopies a l'identique dans les deux fichiers -- un
changement dans l'un (ex: nouvelle feature) pouvait etre oublie dans
l'autre. Desormais, les deux appellent predire().
"""

from datetime import datetime
from typing import Dict, Tuple

import numpy as np
import pandas as pd


def construire_donnees_features(latitude: float, longitude: float, meteo: Dict) -> Dict:
    """Construit le dict de features attendu par le modele, a partir d'une requete de prediction"""
    jour_annee = meteo["jour_annee"]
    semaine = (jour_annee - 1) // 7 + 1
    return {
        "annee": datetime.now().year,
        "semaine": semaine,
        "lat_discrete": round(latitude, 1),
        "lon_discrete": round(longitude, 1),
        "temperature_max": meteo["temperature_max"],
        "temperature_min": meteo["temperature_min"],
        "precipitation_sum": meteo["precipitation_sum"],
        "vent_max": meteo["vent_max"],
        "humidite_moyenne": meteo["humidite_moyenne"],
        "temperature_moyenne": (meteo["temperature_max"] + meteo["temperature_min"]) / 2,
        "pression_moyenne": np.nan,
    }


def aligner_colonnes(modele, donnees_features: Dict) -> pd.DataFrame:
    """Reordonne/complete les features selon celles vues par le modele a l'entrainement"""
    colonnes_attendues = list(getattr(modele, "feature_names_in_", donnees_features.keys()))
    donnees_features = {col: donnees_features.get(col, 0) for col in colonnes_attendues}
    return pd.DataFrame([donnees_features]).fillna(0)


def calculer_confiance(probabilite: float) -> str:
    """BASSE < 0.60, MOYENNE 0.60-0.75, HAUTE > 0.75"""
    return "HAUTE" if probabilite > 0.75 else ("MOYENNE" if probabilite > 0.60 else "BASSE")


def predire(modele, latitude: float, longitude: float, meteo: Dict) -> Tuple[float, str]:
    """Calcule la probabilite de presence et son niveau de confiance pour une requete donnee"""
    donnees_features = construire_donnees_features(latitude, longitude, meteo)
    features = aligner_colonnes(modele, donnees_features)
    probabilite = float(modele.predict_proba(features)[0][1])
    return probabilite, calculer_confiance(probabilite)
