"""
BC05 - API FastAPI pour les predictions de presence d'oiseaux
================================================================

Ce module expose le modele entraine par BC03 (modeles/pipeline_ml.pkl)
via 3 points d'entree HTTP.

Lancement (depuis la racine du projet oiseaux_migrateurs_npdc) :
    python -m uvicorn blocs.bc05_industrialisation.api:app --reload

Documentation interactive une fois lancee : http://127.0.0.1:8000/docs
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel, Field

RACINE_PROJET = Path(__file__).resolve().parents[2]
if str(RACINE_PROJET) not in sys.path:
    sys.path.insert(0, str(RACINE_PROJET))

from commun.config import ESPECES, ParametresAPI, FORMAT_LOG, REPERTOIRE_MODELES  # noqa: E402

logger.remove()
logger.add(lambda msg: print(msg, end=""), format=FORMAT_LOG)


# ========== SCHEMAS PYDANTIC ==========

class ObservationMeteo(BaseModel):
    """Donnees meteorologiques pour prediction"""
    temperature_max: float = Field(..., ge=-50, le=50)
    temperature_min: float = Field(..., ge=-50, le=50)
    precipitation_sum: float = Field(..., ge=0, le=500)
    vent_max: float = Field(..., ge=0, le=50)
    humidite_moyenne: float = Field(..., ge=0, le=100)
    jour_annee: int = Field(..., ge=1, le=365)


class DemandePredicton(BaseModel):
    """Demande de prediction"""
    espece: str = Field(..., description="Nom espece (ex: hirondelle_rustique)")
    latitude: float = Field(..., ge=49.5, le=51.5)
    longitude: float = Field(..., ge=1.5, le=4.0)
    meteo: ObservationMeteo

    class Config:
        json_schema_extra = {
            "example": {
                "espece": "hirondelle_rustique",
                "latitude": 50.5,
                "longitude": 2.75,
                "meteo": {
                    "temperature_max": 18.5,
                    "temperature_min": 12.3,
                    "precipitation_sum": 2.1,
                    "vent_max": 15.0,
                    "humidite_moyenne": 65.0,
                    "jour_annee": 120,
                },
            }
        }


class ReponsePredicton(BaseModel):
    """Reponse prediction"""
    espece: str
    probabilite_presence: float = Field(..., ge=0, le=1, description="Probabilite 0-1")
    confiance: str = Field(..., description="BASSE / MOYENNE / HAUTE")
    date_prediction: datetime
    modele_utilise: str = Field(default="XGBoost")

    class Config:
        json_schema_extra = {
            "example": {
                "espece": "hirondelle_rustique",
                "probabilite_presence": 0.87,
                "confiance": "HAUTE",
                "date_prediction": "2024-05-15T10:30:00",
                "modele_utilise": "XGBoost",
            }
        }


class EspeceInfo(BaseModel):
    """Information espece"""
    nom_francais: str
    nom_scientifique: str
    mois_arrivee: List[int]
    mois_depart: List[int]


class Sante(BaseModel):
    """Status sante API"""
    statut: str = Field(default="OK")
    modele_charge: bool
    version: str
    timestamp: datetime


# ========== INITIALISATION API ==========

app = FastAPI(
    title=ParametresAPI.TITRE,
    description=ParametresAPI.DESCRIPTION,
    version=ParametresAPI.VERSION,
)

MODELE_CHARGE = None
try:
    chemin_modele = REPERTOIRE_MODELES / "pipeline_ml.pkl"
    if chemin_modele.exists():
        MODELE_CHARGE = joblib.load(chemin_modele)
        logger.info(f"Modele charge : {chemin_modele}")
    else:
        logger.warning(f"Modele non trouve : {chemin_modele} (lancez d'abord blocs/bc03_machine_learning/run.py)")
except Exception as e:
    logger.error(f"Erreur chargement modele : {e}")
    MODELE_CHARGE = None


# ========== ENDPOINTS ==========

@app.get("/health", response_model=Sante, tags=["Sante"])
def verifier_sante():
    """Verifie statut API et modeles"""
    return Sante(
        statut="OK",
        modele_charge=(MODELE_CHARGE is not None),
        version=ParametresAPI.VERSION,
        timestamp=datetime.now(),
    )


@app.get("/species", response_model=Dict[str, EspeceInfo], tags=["Donnees"])
def lister_especes():
    """Liste toutes especes disponibles"""
    return {
        cle: EspeceInfo(
            nom_francais=infos["nom_francais"],
            nom_scientifique=infos["nom_scientifique"],
            mois_arrivee=infos["mois_arrivee"],
            mois_depart=infos["mois_depart"],
        )
        for cle, infos in ESPECES.items()
    }


@app.post("/predict", response_model=ReponsePredicton, tags=["Predictions"])
async def predire_presence(demande: DemandePredicton) -> ReponsePredicton:
    """
    Predit la presence d'un oiseau migrateur.

    - espece : hirondelle_rustique, cigogne_blanche, martinet_noir, bergeronnette_printaniere
    - latitude / longitude : coordonnees NPDC (49.5-51.5 deg N, 1.5-4.0 deg E)
    - meteo : conditions meteorologiques
    - Retour : probabilite_presence (0-1) et confiance (BASSE < 0.6, MOYENNE 0.6-0.75, HAUTE > 0.75)
    """
    if demande.espece not in ESPECES:
        raise HTTPException(status_code=400, detail=f"Espece inconnue. Valeurs acceptees : {list(ESPECES.keys())}")

    if MODELE_CHARGE is None:
        raise HTTPException(status_code=503, detail="Modele non disponible. Lancez d'abord blocs/bc03_machine_learning/run.py")

    jour_annee = demande.meteo.jour_annee
    semaine = (jour_annee - 1) // 7 + 1
    donnees_features = {
        "annee": datetime.now().year,
        "semaine": semaine,
        "lat_discrete": round(demande.latitude, 1),
        "lon_discrete": round(demande.longitude, 1),
        "temperature_max": demande.meteo.temperature_max,
        "temperature_min": demande.meteo.temperature_min,
        "precipitation_sum": demande.meteo.precipitation_sum,
        "vent_max": demande.meteo.vent_max,
        "humidite_moyenne": demande.meteo.humidite_moyenne,
        "temperature_moyenne": (demande.meteo.temperature_max + demande.meteo.temperature_min) / 2,
        "pression_moyenne": np.nan,
    }

    colonnes_attendues = list(getattr(MODELE_CHARGE, "feature_names_in_", []))
    if colonnes_attendues:
        donnees_features = {col: donnees_features.get(col, 0) for col in colonnes_attendues}

    features = pd.DataFrame([donnees_features])
    for col in features.columns:
        if features[col].isna().any():
            features[col] = features[col].fillna(0)

    try:
        prediction = float(MODELE_CHARGE.predict_proba(features)[0][1])
    except Exception as e:
        logger.error(f"Erreur prediction : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prediction : {str(e)}")

    confiance = "HAUTE" if prediction > 0.75 else ("MOYENNE" if prediction > 0.60 else "BASSE")

    return ReponsePredicton(
        espece=demande.espece,
        probabilite_presence=prediction,
        confiance=confiance,
        date_prediction=datetime.now(),
        modele_utilise="XGBoost",
    )


@app.get("/", tags=["Root"])
def index():
    """Racine API - Documentation interactive"""
    return {
        "titre": ParametresAPI.TITRE,
        "version": ParametresAPI.VERSION,
        "documentation": "/docs",
        "endpoints": {"health": "GET /health", "species": "GET /species", "predict": "POST /predict"},
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gere erreurs globales"""
    logger.error(f"Erreur API : {str(exc)}")
    return JSONResponse(status_code=500, content={"detail": "Erreur serveur interne", "type": type(exc).__name__})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=ParametresAPI.HOST, port=ParametresAPI.PORT, log_level=ParametresAPI.LOG_LEVEL)
