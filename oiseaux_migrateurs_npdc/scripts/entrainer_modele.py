"""
BC03 - Entraînement modèle XGBoost pour prédiction présence oiseaux
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from loguru import logger

from config import (
    REPERTOIRE_DONNEES_TRAITEES,
    REPERTOIRE_MODELES,
    ParametresML,
    FORMAT_LOG,
    FICHIER_LOG,
)
try:
    from scripts.modeles import GestionnaireModeles, comparer_modeles
except ModuleNotFoundError:
    from modeles import GestionnaireModeles, comparer_modeles

logger.remove()
logger.add(lambda msg: print(msg, end=""), format=FORMAT_LOG)
logger.add(FICHIER_LOG, format=FORMAT_LOG)


def preparer_features(df_grille: pd.DataFrame, df_meteo: pd.DataFrame = None) -> tuple:
    """
    Prépare features pour ML
    
    Returns:
        X, y, feature_names
    """
    logger.info("🔧 Préparation features...")
    
    # Features de base disponibles dans grille
    feature_cols = [
        "annee",
        "semaine",
        "lat_discrete",
        "lon_discrete",
    ]

    if df_meteo is not None and not df_meteo.empty:
        logger.info("  Fusion des variables météo hebdomadaires...")
        meteo = df_meteo.copy()
        meteo["date"] = pd.to_datetime(meteo["date"], errors="coerce")
        meteo = meteo.dropna(subset=["date"])
        meteo["annee"] = meteo["date"].dt.isocalendar().year.astype(int)
        meteo["semaine"] = meteo["date"].dt.isocalendar().week.astype(int)

        colonnes_meteo = [
            "temperature_max",
            "temperature_min",
            "temperature_moyenne",
            "precipitation_sum",
            "vent_max",
            "humidite_moyenne",
            "pression_moyenne",
        ]
        colonnes_meteo_presentes = [c for c in colonnes_meteo if c in meteo.columns]

        if colonnes_meteo_presentes:
            meteo_hebdo = meteo.groupby(["annee", "semaine"], as_index=False)[colonnes_meteo_presentes].mean()
            df_grille = df_grille.merge(meteo_hebdo, on=["annee", "semaine"], how="left")
            feature_cols.extend(colonnes_meteo_presentes)
            logger.info(f"  Variables météo ajoutées : {colonnes_meteo_presentes}")
    
    # Features disponibles
    available_features = [col for col in feature_cols if col in df_grille.columns]
    
    X = df_grille[available_features].copy()
    for col in X.columns:
        if X[col].dtype.kind in "biufc":
            X[col] = X[col].fillna(X[col].median())
    y = df_grille["presence"].copy()
    
    logger.info(f"  Features retenues : {available_features}")
    logger.info(f"  Shape X : {X.shape}")
    logger.info(f"  Distribution y : {y.value_counts().to_dict()}")
    
    return X, y, available_features


def entrainer_modeles(X_train, X_test, y_train, y_test):
    """Entraîne plusieurs modèles et compare"""
    logger.info("=" * 60)
    logger.info("🤖 ENTRAINEMENT MODELES")
    logger.info("=" * 60)
    
    gestionnaire = GestionnaireModeles()
    resultats = {}
    
    # 1. XGBoost
    logger.info("\n📦 Entraînement XGBoost...")
    xgb_params = ParametresML.XGBOOST_PARAMS.copy()
    xgb_params["random_state"] = ParametresML.RANDOM_STATE
    xgb_params["eval_metric"] = "logloss"
    
    pipeline_xgb = Pipeline([
        ("scaler", StandardScaler()),
        ("xgb", XGBClassifier(**xgb_params))
    ])
    
    pipeline_xgb.fit(X_train, y_train)
    metriques_xgb = gestionnaire.evaluator_modele(pipeline_xgb, X_test, y_test, "xgboost")
    gestionnaire.sauvegarder_modele(pipeline_xgb, "pipeline_ml", metriques_xgb)
    resultats["XGBoost"] = metriques_xgb
    
    # 2. Random Forest
    logger.info("\n🌲 Entraînement Random Forest...")
    rf_params = ParametresML.RANDOM_FOREST_PARAMS.copy()
    
    pipeline_rf = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(**rf_params))
    ])
    
    pipeline_rf.fit(X_train, y_train)
    metriques_rf = gestionnaire.evaluator_modele(pipeline_rf, X_test, y_test, "random_forest")
    gestionnaire.sauvegarder_modele(pipeline_rf, "random_forest", metriques_rf)
    resultats["RandomForest"] = metriques_rf
    
    # 3. Logistic Regression
    logger.info("\n📈 Entraînement Logistic Regression...")
    pipeline_lr = Pipeline([
        ("scaler", StandardScaler()),
        ("lr", LogisticRegression(max_iter=1000, random_state=ParametresML.RANDOM_STATE))
    ])
    
    pipeline_lr.fit(X_train, y_train)
    metriques_lr = gestionnaire.evaluator_modele(pipeline_lr, X_test, y_test, "logistic_regression")
    gestionnaire.sauvegarder_modele(pipeline_lr, "logistic_regression", metriques_lr)
    resultats["LogisticRegression"] = metriques_lr
    
    # Comparaison
    logger.info("\n")
    df_comparaison = comparer_modeles(resultats)
    
    return resultats, df_comparaison


def executer_entrainement():
    """Pipeline complet d'entraînement"""
    logger.info("=" * 60)
    logger.info("🚀 DEBUT ENTRAINEMENT MODELES ML")
    logger.info("=" * 60)
    
    # Charger grille
    chemin_grille = REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet"
    
    if not chemin_grille.exists():
        logger.error(f"Grille non trouvée : {chemin_grille}")
        logger.error("Exécutez scripts/nettoyage.py d'abord")
        return
    
    df_grille = pd.read_parquet(chemin_grille)
    logger.info(f"✓ Grille chargée : {len(df_grille)} lignes")

    chemin_meteo = REPERTOIRE_DONNEES_TRAITEES / "meteo_processed.parquet"
    df_meteo = None
    if chemin_meteo.exists():
        df_meteo = pd.read_parquet(chemin_meteo)
        logger.info(f"✓ Météo chargée : {len(df_meteo)} lignes")
    else:
        logger.warning("⚠️ Fichier météo traité absent, entraînement sans météo")
    
    # Préparer features
    X, y, feature_names = preparer_features(df_grille, df_meteo)
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=ParametresML.TEST_SIZE,
        random_state=ParametresML.RANDOM_STATE,
        stratify=y
    )
    
    logger.info(f"\n✓ Split données :")
    logger.info(f"  Train : {len(X_train)} | Test : {len(X_test)}")
    logger.info(f"  Distribution train : {y_train.value_counts().to_dict()}")
    logger.info(f"  Distribution test : {y_test.value_counts().to_dict()}")
    
    # Entraîner modèles
    resultats, df_comparaison = entrainer_modeles(X_train, X_test, y_train, y_test)
    
    # Sauvegarder comparaison
    chemin_csv = REPERTOIRE_MODELES / "evaluations.csv"
    df_comparaison.to_csv(chemin_csv)
    logger.info(f"\n✓ Comparaison sauvegardée : {chemin_csv}")
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ ENTRAINEMENT TERMINE")
    logger.info("=" * 60)
    logger.info(f"Modèles disponibles dans : {REPERTOIRE_MODELES}")
    logger.info("  - pipeline_ml.pkl (XGBoost)")
    logger.info("  - random_forest.pkl")
    logger.info("  - logistic_regression.pkl")


if __name__ == "__main__":
    executer_entrainement()
