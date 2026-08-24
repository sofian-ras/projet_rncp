"""
BC05 - API FastAPI pour predictions oiseaux
Endpoints de prediction et gestion modeles
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from loguru import logger
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from fastapi.responses import JSONResponse

try:
    from config import ParametresAPI, FORMAT_LOG, REPERTOIRE_MODELES
except ModuleNotFoundError:
    from ..config import ParametresAPI, FORMAT_LOG, REPERTOIRE_MODELES

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
                }
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


# ========== INITIALIZATION API ==========

app = FastAPI(
    title=ParametresAPI.TITRE,
    description=ParametresAPI.DESCRIPTION,
    version=ParametresAPI.VERSION,
)

# Charger modele en memoire
MODELE_CHARGE = None
try:
    chemin_modele = REPERTOIRE_MODELES / "pipeline_ml.pkl"
    if chemin_modele.exists():
        MODELE_CHARGE = joblib.load(chemin_modele)
        logger.info(f"Modele charge : {chemin_modele}")
    else:
        logger.warning(f"Modele non trouve : {chemin_modele}")
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
@app.get("/Species", response_model=Dict[str, EspeceInfo], tags=["Donnees"])
def lister_especes():
    """Liste toutes especes disponibles"""
    from config import ESPECES
    
    resultat = {}
    for key, infos in ESPECES.items():
        resultat[key] = EspeceInfo(
            nom_francais=infos["nom_francais"],
            nom_scientifique=infos["nom_scientifique"],
            mois_arrivee=infos["mois_arrivee"],
            mois_depart=infos["mois_depart"],
        )
    
    return resultat


@app.post("/predict", response_model=ReponsePredicton, tags=["Predictions"])
async def predire_presence(demande: DemandePredicton) -> ReponsePredicton:
    """
    Predire presence oiseau migrateur
    
    **Parametres :**
    - espece : hirondelle_rustique, cigogne_blanche, martinet_noir, bergeronnette_printaniere
    - latitude / longitude : coordonnees NPDC (49.5-51.5 deg N, 1.5-4.0 deg E)
    - meteo : conditions meteorologiques
    
    **Retour :**
    - probabilite_presence : 0-1 (1 = certain, 0 = impossible)
    - confiance : BASSE (<0.6), MOYENNE (0.6-0.75), HAUTE (>0.75)
    """
    
    # Validation espece
    from config import ESPECES
    if demande.espece not in ESPECES:
        raise HTTPException(
            status_code=400,
            detail=f"Espece inconnue. Valeurs acceptees : {list(ESPECES.keys())}"
        )
    
    # Verifier modele charge
    if MODELE_CHARGE is None:
        raise HTTPException(
            status_code=503,
            detail="Modele non disponible. Entrainez d'abord le modele."
        )
    
    # Preparer features pour prediction
    # Le modele a ete entraine sur : annee, semaine, lat_discrete, lon_discrete
    from datetime import datetime as dt
    jour_annee = demande.meteo.jour_annee
    semaine = (jour_annee - 1) // 7 + 1  # Calculer semaine depuis jour_annee
    annee = dt.now().year  # Utiliser annee courante
    
    donnees_features = {
        "annee": annee,
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

    # Respecter exactement l'ordre des colonnes attendues par le pipeline entraine
    colonnes_attendues = list(getattr(MODELE_CHARGE, "feature_names_in_", []))
    if colonnes_attendues:
        donnees_features = {col: donnees_features.get(col, 0) for col in colonnes_attendues}

    features = pd.DataFrame([donnees_features])
    for col in features.columns:
        if features[col].isna().any():
            features[col] = features[col].fillna(0)
    
    # Prediction
    try:
        prediction_proba = MODELE_CHARGE.predict_proba(features)[0][1]
        prediction = float(prediction_proba)
    except Exception as e:
        logger.error(f"Erreur prediction : {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prediction : {str(e)}"
        )
    
    # Determiner confiance
    if prediction > 0.75:
        confiance = "HAUTE"
    elif prediction > 0.60:
        confiance = "MOYENNE"
    else:
        confiance = "BASSE"
    
    return ReponsePredicton(
        espece=demande.espece,
        probabilite_presence=float(prediction),
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
        "endpoints": {
            "health": "GET /health",
            "species": "GET /species",
            "predict": "POST /predict",
        }
    }


# ========== ERROR HANDLING ==========

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gere erreurs globales"""
    logger.error(f"Erreur API : {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erreur serveur interne",
            "type": type(exc).__name__,
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=ParametresAPI.HOST,
        port=ParametresAPI.PORT,
        log_level=ParametresAPI.LOG_LEVEL
    )
