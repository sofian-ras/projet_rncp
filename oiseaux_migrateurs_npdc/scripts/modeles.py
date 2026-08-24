"""
Utilitaires gestion modeles ML
Serialisation, chargement, evaluation
"""

import pickle
import json
from pathlib import Path
from typing import Any, Dict, Tuple
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, confusion_matrix
from loguru import logger

from config import REPERTOIRE_MODELES, FORMAT_LOG, FICHIER_LOG

logger.remove()
logger.add(lambda msg: print(msg, end=""), format=FORMAT_LOG)
logger.add(FICHIER_LOG, format=FORMAT_LOG)


class GestionnaireModeles:
    """Gere cycle vie modeles ML"""
    
    def __init__(self, repertoire: Path = REPERTOIRE_MODELES):
        self.repertoire = repertoire
        self.repertoire.mkdir(parents=True, exist_ok=True)
        self.metadonnees = {}
    
    def sauvegarder_modele(
        self,
        modele: Any,
        nom_modele: str,
        metriques: Dict[str, float] = None,
        metadata: Dict[str, Any] = None
    ) -> Path:
        """
        Sauvegarde modele sklearn en pickle
        
        Args:
            modele : Modele sklearn entraine
            nom_modele : Identificateur (ex: "xgboost_v1")
            metriques : Dictionnaire metriques d'evaluation
            metadata : Metadonnees additionnelles
        """
        chemin_modele = self.repertoire / f"{nom_modele}.pkl"
        
        try:
            with open(chemin_modele, "wb") as f:
                pickle.dump(modele, f)
            
            logger.info(f"Modele sauvegarde : {chemin_modele}")
            
            # Sauvegarder metadata
            if metriques or metadata:
                self._sauvegarder_metadata(nom_modele, metriques, metadata)
            
            return chemin_modele
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde modele : {e}")
            raise
    
    def charger_modele(self, nom_modele: str) -> Any:
        """Charge modele depuis pickle"""
        chemin_modele = self.repertoire / f"{nom_modele}.pkl"
        
        if not chemin_modele.exists():
            raise FileNotFoundError(f"Modele non trouve : {chemin_modele}")
        
        try:
            with open(chemin_modele, "rb") as f:
                modele = pickle.load(f)
            
            logger.info(f"Modele charge : {nom_modele}")
            return modele
            
        except Exception as e:
            logger.error(f"Erreur chargement modele : {e}")
            raise
    
    def evaluator_modele(
        self,
        modele: Any,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        nom_modele: str = "evaluation"
    ) -> Dict[str, float]:
        """
        Evalue modele sur donnees test
        
        Retourne : Accuracy, F1, AUC-ROC
        """
        logger.info(f"Evaluation modele : {nom_modele}")
        
        # Predictions
        y_pred = modele.predict(X_test)
        
        try:
            y_pred_proba = modele.predict_proba(X_test)[:, 1]
        except AttributeError:
            y_pred_proba = None
            logger.warning("  Predictions probabilistes non disponibles")
        
        # Metriques
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
        
        # Log
        logger.info(f"  Accuracy : {metriques['accuracy']:.4f}")
        logger.info(f"  F1-Score : {metriques['f1_score']:.4f}")
        if "auc_roc" in metriques:
            logger.info(f"  AUC-ROC  : {metriques['auc_roc']:.4f}")
        
        return metriques
    
    def _sauvegarder_metadata(
        self,
        nom_modele: str,
        metriques: Dict = None,
        metadata: Dict = None
    ):
        """Sauvegarde metadonnees en JSON"""
        donnees_metadata = {
            "nom_modele": nom_modele,
            "date_sauvegarde": datetime.now().isoformat(),
            "metriques": metriques or {},
            "metadata": metadata or {},
        }
        
        chemin_json = self.repertoire / f"{nom_modele}_metadata.json"
        
        with open(chemin_json, "w", encoding="utf-8") as f:
            json.dump(donnees_metadata, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Metadata sauvegardee : {chemin_json.name}")
    
    def lister_modeles(self) -> list:
        """Liste tous modeles disponibles"""
        modeles = [f.stem for f in self.repertoire.glob("*.pkl")]
        logger.info(f"Modeles disponibles : {len(modeles)}")
        for m in modeles:
            logger.info(f"  - {m}")
        return modeles


def comparer_modeles(resultats_eval: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """
    Compare performances plusieurs modeles
    
    Args:
        resultats_eval : {nom_modele: {metrique: valeur}}
    
    Returns:
        DataFrame comparatif
    """
    df_comparaison = pd.DataFrame(resultats_eval).T
    
    # Ordonner par accuracy
    df_comparaison = df_comparaison.sort_values("accuracy", ascending=False)
    
    logger.info("\n" + "=" * 60)
    logger.info("COMPARAISON MODELES")
    logger.info("=" * 60)
    logger.info(df_comparaison.to_string())
    logger.info("=" * 60 + "\n")
    
    return df_comparaison


if __name__ == "__main__":
    # Test
    gestionnaire = GestionnaireModeles()
    modeles = gestionnaire.lister_modeles()
