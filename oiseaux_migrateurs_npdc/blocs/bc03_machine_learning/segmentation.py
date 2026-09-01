"""
BC03 - Segmentation non supervisee : zones de densite d'observations
=====================================================================

Complement non supervise de run.py (competence C3.3 du referentiel :
segmenter une base en groupes homogenes, sans variable cible).

On regroupe par K-Means les cellules geographiques ou les especes sont
presentes. Le nombre de zones K n'est pas fixe a l'avance : on teste
plusieurs valeurs et on retient celle qui maximise le score de silhouette.
"""

import pandas as pd
from loguru import logger
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from commun.config import REPERTOIRE_MODELES, ParametresML, ParametresSegmentation


def choisir_nombre_zones(coordonnees: pd.DataFrame) -> int:
    """Retient le K (entre K_MIN et K_MAX) qui maximise le score de silhouette."""
    scores = {}
    for k in range(ParametresSegmentation.K_MIN, ParametresSegmentation.K_MAX + 1):
        etiquettes = KMeans(
            n_clusters=k, n_init=10, random_state=ParametresML.RANDOM_STATE
        ).fit_predict(coordonnees)
        scores[k] = silhouette_score(coordonnees, etiquettes)
        logger.info(f"  K={k} : silhouette={scores[k]:.3f}")
    meilleur = max(scores, key=scores.get)
    logger.info(f"  -> {meilleur} zones retenues (silhouette={scores[meilleur]:.3f})")
    return meilleur


def segmenter_zones_densite(df_grille: pd.DataFrame) -> pd.DataFrame:
    """Regroupe les cellules de presence en zones geographiques homogenes (K-Means).

    Ecrit modeles/zones_densite.csv (centre et volume de chaque zone).
    """
    logger.info("\n--- SEGMENTATION NON SUPERVISEE (zones de densite) ---")
    presences = (
        df_grille.loc[df_grille["presence"] == 1, ["lat_discrete", "lon_discrete"]]
        .dropna()
        .reset_index(drop=True)
    )
    if len(presences) < ParametresSegmentation.K_MAX:
        logger.warning("  Trop peu de cellules de presence pour segmenter.")
        return pd.DataFrame()

    nombre_zones = choisir_nombre_zones(presences)
    modele = KMeans(n_clusters=nombre_zones, n_init=10, random_state=ParametresML.RANDOM_STATE)
    presences["zone"] = modele.fit_predict(presences)

    zones = (
        presences.groupby("zone")
        .agg(
            latitude=("lat_discrete", "mean"),
            longitude=("lon_discrete", "mean"),
            cellules_presence=("zone", "size"),
        )
        .sort_values("cellules_presence", ascending=False)
        .reset_index(drop=True)
    )
    chemin = REPERTOIRE_MODELES / "zones_densite.csv"
    zones.round(3).to_csv(chemin, index=False)
    logger.info(f"  {nombre_zones} zones -> {chemin.name}")
    return zones
