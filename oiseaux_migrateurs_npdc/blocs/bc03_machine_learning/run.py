"""
BC03 - Machine Learning : prediction sur donnees structurees
================================================================

Lit la grille et la meteo produites par BC01 (donnees/traitees/, versionnees
dans le depot). Lancer BC01 d'abord si ces fichiers sont absents.

Il enchaine quatre etapes :
  1. Preparation des features (position, periode, meteo) et de la cible.
  2. Supervise : entrainement et comparaison de 3 modeles (Regression
     logistique, Foret aleatoire, XGBoost), chaque run journalise dans MLflow.
  3. Validation du modele retenu : validation croisee stratifiee + ecart
     train/test (detection du sur-apprentissage).
  4. Non supervise : segmentation des zones de densite d'observations (K-Means).

Utilisation :
    python blocs/bc03_machine_learning/run.py

Duree : ~1 a 2 minutes selon la machine.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

_racine = next(p for p in Path(__file__).resolve().parents if (p / "commun").is_dir())
sys.path.insert(0, str(_racine))  # racine du projet -> package commun/

from commun.config import REPERTOIRE_DONNEES_TRAITEES, REPERTOIRE_MODELES, REPERTOIRE_RACINE, ParametresML
from commun.journalisation import configurer_logger
from commun.chargement import charger_grille_hebdomadaire, charger_meteo_traitee
from gestion_modeles import (
    GestionnaireModeles,
    comparer_modeles,
    demarrer_suivi_experience,
    journaliser_run,
)
from segmentation import segmenter_zones_densite

RACINE_PROJET = REPERTOIRE_RACINE
logger = configurer_logger()

MODELE_RETENU = "xgboost"                       # modele mis "en production"
FICHIER_MODELE = {"xgboost": "pipeline_ml"}     # nom de fichier .pkl par modele (defaut = son nom)


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


def construire_modeles() -> dict:
    """Les 3 modeles a comparer, du plus simple au plus complexe (tous precedes d'une normalisation)."""
    def avec_normalisation(estimateur):
        return Pipeline([("normalisation", StandardScaler()), ("modele", estimateur)])

    return {
        "regression_logistique": avec_normalisation(
            LogisticRegression(max_iter=1000, random_state=ParametresML.RANDOM_STATE)),
        "foret_aleatoire": avec_normalisation(
            RandomForestClassifier(**ParametresML.RANDOM_FOREST_PARAMS, n_jobs=-1)),
        "xgboost": avec_normalisation(
            XGBClassifier(**ParametresML.XGBOOST_PARAMS,
                          random_state=ParametresML.RANDOM_STATE, eval_metric="logloss")),
    }


def entrainer_modeles(X_train, X_test, y_train, y_test) -> tuple:
    """Entraine, evalue, sauvegarde les 3 modeles et journalise chaque run dans MLflow.

    Retourne (tableau_comparaison, pipeline_du_modele_retenu).
    """
    logger.info("=" * 60)
    logger.info("ENTRAINEMENT DES MODELES (supervise)")
    logger.info("=" * 60)

    gestionnaire = GestionnaireModeles(REPERTOIRE_MODELES)
    mlflow = demarrer_suivi_experience()
    resultats, pipelines = {}, {}

    for nom, pipeline in construire_modeles().items():
        logger.info(f"\nEntrainement {nom}...")
        pipeline.fit(X_train, y_train)
        metriques = gestionnaire.evaluer_modele(pipeline, X_test, y_test, nom)
        gestionnaire.sauvegarder_modele(pipeline, FICHIER_MODELE.get(nom, nom), metriques)
        journaliser_run(mlflow, nom, pipeline, metriques)
        resultats[nom], pipelines[nom] = metriques, pipeline

    return comparer_modeles(resultats), pipelines[MODELE_RETENU]


def valider_modele_retenu(pipeline, X_train, y_train, X_test, y_test) -> None:
    """Validation croisee stratifiee + ecart train/test (sur-apprentissage / sous-apprentissage)."""
    logger.info("\n--- VALIDATION DU MODELE RETENU ---")
    validation_croisee = StratifiedKFold(
        n_splits=ParametresML.N_SPLITS_CV, shuffle=True, random_state=ParametresML.RANDOM_STATE
    )
    scores = cross_val_score(pipeline, X_train, y_train, cv=validation_croisee, scoring="roc_auc")
    logger.info(f"AUC-ROC {ParametresML.N_SPLITS_CV}-fold : {scores.mean():.3f} +/- {scores.std():.3f}")

    auc_train = roc_auc_score(y_train, pipeline.predict_proba(X_train)[:, 1])
    auc_test = roc_auc_score(y_test, pipeline.predict_proba(X_test)[:, 1])
    ecart = auc_train - auc_test
    logger.info(f"AUC-ROC train {auc_train:.3f} | test {auc_test:.3f} | ecart {ecart:.3f}")
    logger.info(
        "  Ecart faible : pas de sur-apprentissage marque."
        if ecart <= 0.05
        else "  Ecart eleve (> 0.05) : sur-apprentissage probable."
    )


def analyser_influence_variables(pipeline, noms_features) -> None:
    """Importance des variables du modele retenu -> CSV + graphique (competence C3.4)."""
    logger.info("\n--- INFLUENCE DES VARIABLES ---")
    importances = pd.Series(
        pipeline.named_steps["modele"].feature_importances_, index=noms_features, name="importance"
    ).sort_values(ascending=False)

    importances.to_csv(REPERTOIRE_MODELES / "influence_variables.csv")

    axe = importances.iloc[::-1].plot.barh(figsize=(8, 5), color="steelblue")
    axe.set_title("Influence des variables - modele retenu", fontweight="bold")
    axe.set_xlabel("Importance (gain XGBoost)")
    axe.figure.tight_layout()
    axe.figure.savefig(REPERTOIRE_MODELES / "influence_variables.png", dpi=150)
    plt.close(axe.figure)

    for nom, valeur in importances.head().items():
        logger.info(f"  {nom:<22} {valeur:.3f}")


def main() -> None:
    print("\n" + "#" * 70)
    print("# BC03 - MACHINE LEARNING (donnees structurees)")
    print("#" * 70 + "\n")

    chemin_grille = REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet"
    if not chemin_grille.exists():
        logger.error("Donnees introuvables dans donnees/traitees/ : lancer d'abord blocs/bc01_infrastructure_donnees/run.py.")
        return

    df_grille = charger_grille_hebdomadaire()
    logger.info(f"Grille chargee : {len(df_grille)} lignes")

    chemin_meteo = REPERTOIRE_DONNEES_TRAITEES / "meteo_processed.parquet"
    df_meteo = charger_meteo_traitee() if chemin_meteo.exists() else None
    if df_meteo is None:
        logger.warning("Fichier meteo traite absent, entrainement sans meteo")

    X, y, noms_features = preparer_features(df_grille, df_meteo)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=ParametresML.TEST_SIZE, random_state=ParametresML.RANDOM_STATE, stratify=y,
    )
    logger.info(f"\nSplit donnees : Train {len(X_train)} | Test {len(X_test)}")

    df_comparaison, modele_retenu = entrainer_modeles(X_train, X_test, y_train, y_test)
    df_comparaison.to_csv(REPERTOIRE_MODELES / "evaluations.csv")

    valider_modele_retenu(modele_retenu, X_train, y_train, X_test, y_test)
    analyser_influence_variables(modele_retenu, noms_features)
    segmenter_zones_densite(df_grille)

    print("\nPreuves produites (fichiers verifiables sur disque) :")
    for chemin in [
        REPERTOIRE_MODELES / "pipeline_ml.pkl",
        REPERTOIRE_MODELES / "foret_aleatoire.pkl",
        REPERTOIRE_MODELES / "regression_logistique.pkl",
        REPERTOIRE_MODELES / "evaluations.csv",
        REPERTOIRE_MODELES / "influence_variables.csv",
        REPERTOIRE_MODELES / "influence_variables.png",
        REPERTOIRE_MODELES / "zones_densite.csv",
    ]:
        marque = "OK" if chemin.exists() else "MANQUANT"
        print(f"  [{marque}] {chemin.relative_to(RACINE_PROJET)}")

    if "auc_roc" in df_comparaison:
        print(f"\nMeilleur modele (AUC-ROC) : {df_comparaison['auc_roc'].idxmax()}")
    print("\nBC03 termine.\n")


if __name__ == "__main__":
    main()
