"""
Utilitaires de gestion des modeles ML pour BC03 : sauvegarde, chargement,
evaluation et comparaison. Separe de run.py pour rester lisible, mais
fait partie du meme bloc (pas partage avec les autres blocs).
"""

import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from loguru import logger
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, roc_auc_score

from commun.config import REPERTOIRE_MODELES, REPERTOIRE_RACINE


class GestionnaireModeles:
    """Gere le cycle de vie des modeles ML : sauvegarde, chargement, evaluation"""

    def __init__(self, repertoire: Path):
        self.repertoire = repertoire
        self.repertoire.mkdir(parents=True, exist_ok=True)

    def sauvegarder_modele(self, modele: Any, nom_modele: str, metriques: Dict[str, float] = None,
                            metadata: Dict[str, Any] = None) -> Path:
        """Sauvegarde un modele sklearn en pickle, avec ses metriques en JSON a cote"""
        chemin_modele = self.repertoire / f"{nom_modele}.pkl"
        with open(chemin_modele, "wb") as f:
            pickle.dump(modele, f)
        logger.info(f"Modele sauvegarde : {chemin_modele}")

        if metriques or metadata:
            self._sauvegarder_metadata(nom_modele, metriques, metadata)
        return chemin_modele

    def charger_modele(self, nom_modele: str) -> Any:
        chemin_modele = self.repertoire / f"{nom_modele}.pkl"
        if not chemin_modele.exists():
            raise FileNotFoundError(f"Modele non trouve : {chemin_modele}")
        with open(chemin_modele, "rb") as f:
            return pickle.load(f)

    def evaluer_modele(self, modele: Any, X_test: pd.DataFrame, y_test: pd.Series,
                        nom_modele: str = "evaluation") -> Dict[str, float]:
        """Evalue un modele sur le jeu de test : Accuracy, F1, AUC-ROC, matrice de confusion"""
        logger.info(f"Evaluation modele : {nom_modele}")
        y_pred = modele.predict(X_test)
        try:
            y_pred_proba = modele.predict_proba(X_test)[:, 1]
        except AttributeError:
            y_pred_proba = None

        metriques = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
        }
        if y_pred_proba is not None:
            metriques["auc_roc"] = float(roc_auc_score(y_test, y_pred_proba))

        confusion = confusion_matrix(y_test, y_pred)
        metriques["tn"] = int(confusion[0, 0])
        metriques["fp"] = int(confusion[0, 1])
        metriques["fn"] = int(confusion[1, 0])
        metriques["tp"] = int(confusion[1, 1])

        logger.info(f"  Accuracy : {metriques['accuracy']:.4f}")
        logger.info(f"  F1-Score : {metriques['f1_score']:.4f}")
        if "auc_roc" in metriques:
            logger.info(f"  AUC-ROC  : {metriques['auc_roc']:.4f}")
        return metriques

    def _sauvegarder_metadata(self, nom_modele: str, metriques: Dict = None, metadata: Dict = None):
        donnees_metadata = {
            "nom_modele": nom_modele,
            "date_sauvegarde": datetime.now().isoformat(),
            "metriques": metriques or {},
            "metadata": metadata or {},
        }
        chemin_json = self.repertoire / f"{nom_modele}_metadata.json"
        with open(chemin_json, "w", encoding="utf-8") as f:
            json.dump(donnees_metadata, f, indent=2, ensure_ascii=False)


def comparer_modeles(resultats_eval: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """Compare les performances de plusieurs modeles, tries par accuracy"""
    df_comparaison = pd.DataFrame(resultats_eval).T.sort_values("accuracy", ascending=False)
    logger.info("\n" + "=" * 60)
    logger.info("COMPARAISON MODELES")
    logger.info("=" * 60)
    logger.info(df_comparaison.to_string())
    logger.info("=" * 60 + "\n")
    return df_comparaison


def demarrer_suivi_experience(nom_experience: str = "bc03_oiseaux_migrateurs"):
    """Active le suivi d'experience MLflow s'il est installe. Retourne le module mlflow, ou None.

    Rend le suivi optionnel : le projet reste executable sans le paquet mlflow.
    Le suivi est ecrit dans mlruns/ a la racine du projet.
    """
    try:
        import mlflow
    except ImportError:
        logger.warning("mlflow non installe : suivi d'experience ignore (pip install mlflow)")
        return None
    mlflow.set_tracking_uri((REPERTOIRE_RACINE / "mlruns").as_uri())
    mlflow.set_experiment(nom_experience)
    return mlflow


def journaliser_run(mlflow, nom_modele: str, pipeline, metriques: Dict[str, float]) -> None:
    """Enregistre un entrainement (parametres du modele + metriques) comme un run MLflow."""
    if mlflow is None:
        return
    with mlflow.start_run(run_name=nom_modele):
        mlflow.log_params(pipeline.named_steps["modele"].get_params())
        mlflow.log_metrics({cle: float(valeur) for cle, valeur in metriques.items()})
