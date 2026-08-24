"""
BC03 - Machine Learning : prediction sur donnees structurees
================================================================

Ce script est AUTONOME : il lit la grille et la meteo produites par
BC01 (donnees/traitees/*.parquet), prepare les features, entraine et
compare 3 modeles de classification (Regression logistique, Foret
aleatoire, XGBoost), et sauvegarde les modeles + leurs metriques.

Utilisation :
    python blocs/bc03_machine_learning/run.py

Duree : quelques dizaines de secondes a ~2 minutes selon la machine
(l'essentiel du temps est pris par l'entrainement de la foret
aleatoire sur environ 900 000 lignes).
"""

import sys
from pathlib import Path

import pandas as pd
from loguru import logger
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

RACINE_PROJET = Path(__file__).resolve().parents[2]
if str(RACINE_PROJET) not in sys.path:
    sys.path.insert(0, str(RACINE_PROJET))

from commun.config import (  # noqa: E402
    REPERTOIRE_DONNEES_TRAITEES,
    REPERTOIRE_MODELES,
    ParametresML,
    FORMAT_LOG,
    FICHIER_LOG,
)
from blocs.bc03_machine_learning.gestion_modeles import GestionnaireModeles, comparer_modeles  # noqa: E402

logger.remove()
logger.add(lambda msg: print(msg, end=""), format=FORMAT_LOG)
logger.add(FICHIER_LOG, format=FORMAT_LOG)


def preparer_features(df_grille: pd.DataFrame, df_meteo: pd.DataFrame = None) -> tuple:
    """Prepare features (X) et cible (y) pour l'entrainement. Retourne X, y, noms_features."""
    logger.info("Preparation features...")
    feature_cols = ["annee", "semaine", "lat_discrete", "lon_discrete"]

    if df_meteo is not None and not df_meteo.empty:
        logger.info("  Fusion des variables meteo hebdomadaires...")
        meteo = df_meteo.copy()
        meteo["date"] = pd.to_datetime(meteo["date"], errors="coerce")
        meteo = meteo.dropna(subset=["date"])
        meteo["annee"] = meteo["date"].dt.isocalendar().year.astype(int)
        meteo["semaine"] = meteo["date"].dt.isocalendar().week.astype(int)

        colonnes_meteo = [
            "temperature_max", "temperature_min", "temperature_moyenne",
            "precipitation_sum", "vent_max", "humidite_moyenne", "pression_moyenne",
        ]
        colonnes_meteo_presentes = [c for c in colonnes_meteo if c in meteo.columns]
        if colonnes_meteo_presentes:
            meteo_hebdo = meteo.groupby(["annee", "semaine"], as_index=False)[colonnes_meteo_presentes].mean()
            df_grille = df_grille.merge(meteo_hebdo, on=["annee", "semaine"], how="left")
            feature_cols.extend(colonnes_meteo_presentes)
            logger.info(f"  Variables meteo ajoutees : {colonnes_meteo_presentes}")

    available_features = [c for c in feature_cols if c in df_grille.columns]
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
    """Entraine 3 modeles et les compare"""
    logger.info("=" * 60)
    logger.info("ENTRAINEMENT MODELES")
    logger.info("=" * 60)

    gestionnaire = GestionnaireModeles(REPERTOIRE_MODELES)
    resultats = {}

    logger.info("\nEntrainement Regression logistique...")
    pipeline_lr = Pipeline([
        ("scaler", StandardScaler()),
        ("lr", LogisticRegression(max_iter=1000, random_state=ParametresML.RANDOM_STATE)),
    ])
    pipeline_lr.fit(X_train, y_train)
    metriques_lr = gestionnaire.evaluator_modele(pipeline_lr, X_test, y_test, "logistic_regression")
    gestionnaire.sauvegarder_modele(pipeline_lr, "logistic_regression", metriques_lr)
    resultats["LogisticRegression"] = metriques_lr

    logger.info("\nEntrainement Foret aleatoire...")
    rf_params = dict(ParametresML.RANDOM_FOREST_PARAMS)
    rf_params["n_jobs"] = -1  # parallelise sur tous les coeurs, ne change pas le resultat
    pipeline_rf = Pipeline([("scaler", StandardScaler()), ("rf", RandomForestClassifier(**rf_params))])
    pipeline_rf.fit(X_train, y_train)
    metriques_rf = gestionnaire.evaluator_modele(pipeline_rf, X_test, y_test, "random_forest")
    gestionnaire.sauvegarder_modele(pipeline_rf, "random_forest", metriques_rf)
    resultats["RandomForest"] = metriques_rf

    logger.info("\nEntrainement XGBoost...")
    xgb_params = dict(ParametresML.XGBOOST_PARAMS)
    xgb_params["random_state"] = ParametresML.RANDOM_STATE
    xgb_params["eval_metric"] = "logloss"
    pipeline_xgb = Pipeline([("scaler", StandardScaler()), ("xgb", XGBClassifier(**xgb_params))])
    pipeline_xgb.fit(X_train, y_train)
    metriques_xgb = gestionnaire.evaluator_modele(pipeline_xgb, X_test, y_test, "xgboost")
    gestionnaire.sauvegarder_modele(pipeline_xgb, "pipeline_ml", metriques_xgb)
    resultats["XGBoost"] = metriques_xgb

    df_comparaison = comparer_modeles(resultats)
    return resultats, df_comparaison


def main() -> None:
    print("\n" + "#" * 70)
    print("# BC03 - MACHINE LEARNING (donnees structurees)")
    print("#" * 70 + "\n")

    chemin_grille = REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet"
    if not chemin_grille.exists():
        logger.error("Donnees de BC01 introuvables. Lancez d'abord : python blocs/bc01_infrastructure_donnees/run.py")
        return

    df_grille = pd.read_parquet(chemin_grille)
    logger.info(f"Grille chargee : {len(df_grille)} lignes")

    chemin_meteo = REPERTOIRE_DONNEES_TRAITEES / "meteo_processed.parquet"
    df_meteo = pd.read_parquet(chemin_meteo) if chemin_meteo.exists() else None
    if df_meteo is None:
        logger.warning("Fichier meteo traite absent, entrainement sans meteo")

    X, y, _ = preparer_features(df_grille, df_meteo)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=ParametresML.TEST_SIZE, random_state=ParametresML.RANDOM_STATE, stratify=y,
    )
    logger.info(f"\nSplit donnees : Train {len(X_train)} | Test {len(X_test)}")

    resultats, df_comparaison = entrainer_modeles(X_train, X_test, y_train, y_test)

    chemin_csv = REPERTOIRE_MODELES / "evaluations.csv"
    df_comparaison.to_csv(chemin_csv)

    print("\nPreuves produites (fichiers verifiables sur disque) :")
    for chemin in [
        REPERTOIRE_MODELES / "pipeline_ml.pkl",
        REPERTOIRE_MODELES / "random_forest.pkl",
        REPERTOIRE_MODELES / "logistic_regression.pkl",
        REPERTOIRE_MODELES / "evaluations.csv",
    ]:
        marque = "OK" if chemin.exists() else "MANQUANT"
        print(f"  [{marque}] {chemin.relative_to(RACINE_PROJET)}")

    print(f"\nMeilleur modele (AUC-ROC) : "
          f"{df_comparaison['auc_roc'].idxmax() if 'auc_roc' in df_comparaison else '?'}")
    print("\nBC03 termine. Bloc suivant : blocs/bc04_deep_learning/run.py\n")


if __name__ == "__main__":
    main()
