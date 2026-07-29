"""
BC02 - Analyse Exploratoire des observations et météo
Visualisations et tests statistiques
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
import logging

import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
from scipy import stats
from loguru import logger

from config import (
    REPERTOIRE_DONNEES_TRAITEES,
    REPERTOIRE_RACINE,
    ESPECES,
    ZONE_GEOGRAPHIQUE,
    FORMAT_LOG,
    FICHIER_LOG,
)

logger.remove()
logger.add(lambda msg: print(msg, end=""), format=FORMAT_LOG)
logger.add(FICHIER_LOG, format=FORMAT_LOG)

# Configuration plots
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")


class AnalyseurExploratoire:
    """Analyse exploratoire observations + météo"""
    
    def __init__(self):
        self.repertoire_sorties = REPERTOIRE_RACINE / "outputs" / "eda"
        self.repertoire_sorties.mkdir(parents=True, exist_ok=True)
    
    def charger_donnees(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Charge observations, grille et météo traitée"""
        chemin_obs = REPERTOIRE_DONNEES_TRAITEES / "observations_nettoyees.parquet"
        chemin_grille = REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet"
        chemin_meteo = REPERTOIRE_DONNEES_TRAITEES / "meteo_processed.parquet"
        
        df_obs = pd.read_parquet(chemin_obs)
        df_grille = pd.read_parquet(chemin_grille)
        df_meteo = pd.read_parquet(chemin_meteo) if chemin_meteo.exists() else pd.DataFrame()
        
        logger.info(f"✓ Observations chargées : {len(df_obs)}")
        logger.info(f"✓ Grille chargée : {len(df_grille)}")
        logger.info(f"✓ Météo chargée : {len(df_meteo)}")
        
        return df_obs, df_grille, df_meteo
    
    def analyser_saisonnalite(self, df_obs: pd.DataFrame) -> pd.DataFrame:
        """Analyse distribution observations par mois/semaine"""
        logger.info("📊 Analyse saisonnalité...")
        
        df_obs["mois"] = pd.to_datetime(df_obs["date_observation"]).dt.month
        df_obs["semaine_annee"] = pd.to_datetime(df_obs["date_observation"]).dt.isocalendar().week
        
        # Agrégation par mois et espèce
        saisonnalite = df_obs.groupby(["mois", "espece"]).size().reset_index(name="nombre_observations")
        
        # Visualiser
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Saisonnalité des Observations - NPDC", fontsize=16, fontweight="bold")
        
        for idx, (espece, infos) in enumerate(ESPECES.items()):
            ax = axes[idx // 2, idx % 2]
            
            donnees_espece = saisonnalite[saisonnalite["espece"] == espece]
            
            ax.bar(donnees_espece["mois"], donnees_espece["nombre_observations"], 
                   color="steelblue", alpha=0.7, edgecolor="black")
            ax.set_xlabel("Mois", fontsize=11)
            ax.set_ylabel("Nombre observations", fontsize=11)
            ax.set_title(infos["nom_francais"], fontsize=12, fontweight="bold")
            ax.set_xticks(range(1, 13))
            ax.grid(True, alpha=0.3, axis="y")
            
            # Ajouter period attendue
            mois_arrivee = infos["mois_arrivee"]
            for mois in mois_arrivee:
                ax.axvline(mois, color="green", linestyle="--", alpha=0.5, linewidth=2)
        
        plt.tight_layout()
        plt.savefig(self.repertoire_sorties / "saisonnalite.png", dpi=300, bbox_inches="tight")
        logger.info("  ✓ Graphique saisonnalité sauvegardé")
        
        return saisonnalite
    
    def creer_carte_densite(self, df_obs: pd.DataFrame) -> folium.Map:
        """Crée carte heatmap densité observations"""
        logger.info("🗺️ Création carte densité...")
        
        # Centre NPDC
        centre = [ZONE_GEOGRAPHIQUE.centre_latitude, ZONE_GEOGRAPHIQUE.centre_longitude]
        
        # Carte folium
        carte = folium.Map(
            location=centre,
            zoom_start=9,
            tiles="OpenStreetMap"
        )
        
        # Données heatmap
        donnees_heatmap = df_obs[["latitude", "longitude"]].values.tolist()
        
        HeatMap(donnees_heatmap, radius=15, blur=25, max_zoom=1).add_to(carte)
        
        # Ajouter marqueur centre
        folium.CircleMarker(
            location=centre,
            radius=5,
            color="red",
            fill=True,
            popup="Centre NPDC"
        ).add_to(carte)
        
        # Sauvegarder
        chemin_carte = self.repertoire_sorties / "carte_densite.html"
        carte.save(str(chemin_carte))
        logger.info(f"  ✓ Carte sauvegardée : {chemin_carte.name}")
        
        return carte
    
    def analyser_correlations(self, df_grille: pd.DataFrame, df_meteo: pd.DataFrame) -> pd.DataFrame:
        """Analyse corrélations météo ↔ présence"""
        logger.info("🔗 Analyse corrélations...")

        if df_meteo.empty:
            logger.warning("  Données météo absentes. Corrélations non calculées.")
            return pd.DataFrame()
        
        # Préparer météo en agrégation hebdomadaire
        df_meteo["date"] = pd.to_datetime(df_meteo["date"])
        df_meteo["annee"] = df_meteo["date"].dt.isocalendar().year.astype(int)
        df_meteo["semaine"] = df_meteo["date"].dt.isocalendar().week.astype(int)

        variables_meteo = [
            "temperature_max",
            "temperature_min",
            "precipitation_sum",
            "vent_max",
            "humidite_moyenne",
            "temperature_moyenne",
            "pression_moyenne",
        ]
        variables_meteo = [v for v in variables_meteo if v in df_meteo.columns]

        meteo_hebdo = df_meteo.groupby(["annee", "semaine"], as_index=False)[variables_meteo].mean()

        # Fusionner grille présence/absence + météo
        df_fusion = df_grille.merge(meteo_hebdo, on=["annee", "semaine"], how="left")

        if df_fusion.empty or "presence" not in df_fusion.columns:
            logger.warning("  Aucune donnée exploitable pour les corrélations.")
            return pd.DataFrame()

        if df_fusion["presence"].nunique() < 2:
            logger.warning(
                "  La variable 'presence' est constante dans ce jeu de données. "
                "Corrélations non interprétables."
            )
            return pd.DataFrame()
        
        # Corrélations par espèce
        correlations = {}
        for espece in df_fusion["espece"].unique():
            df_espece = df_fusion[df_fusion["espece"] == espece]
            
            corr_espece = {}
            for var in variables_meteo:
                if var in df_espece.columns and df_espece[var].notna().sum() > 0:
                    correlation = df_espece["presence"].corr(df_espece[var])
                    corr_espece[var] = correlation
            
            correlations[espece] = corr_espece
        
        # Visualiser
        df_corr = pd.DataFrame(correlations).T
        
        if not df_corr.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(df_corr, annot=True, fmt=".3f", cmap="RdBu_r", 
                        center=0, cbar_kws={"label": "Corrélation"}, ax=ax,
                        vmin=-0.5, vmax=0.5)
            ax.set_title("Corrélations Météo ↔ Présence Oiseaux", fontsize=14, fontweight="bold")
            ax.set_xlabel("Variables météorologiques", fontsize=11)
            ax.set_ylabel("Espèces", fontsize=11)
            
            plt.tight_layout()
            plt.savefig(self.repertoire_sorties / "correlations_meteo.png", dpi=300, bbox_inches="tight")
            logger.info("  ✓ Heatmap corrélations sauvegardée")
        
        return df_corr
    
    @staticmethod
    def test_independance_chi2(df_obs: pd.DataFrame) -> Dict[str, float]:
        """Test indépendance χ² entre espèce et mois"""
        logger.info("📈 Tests d'indépendance (χ²)...")
        
        df_obs["mois"] = pd.to_datetime(df_obs["date_observation"]).dt.month
        
        # Contingency table
        tableau_contingence = pd.crosstab(df_obs["espece"], df_obs["mois"])
        
        # χ² test
        chi2, p_value, dof, expected = stats.chi2_contingency(tableau_contingence)
        
        logger.info(f"  χ² = {chi2:.4f}, p-value = {p_value:.2e}, ddl = {dof}")
        
        if p_value < 0.05:
            logger.info("  ✓ Saisonnalité SIGNIFICATIVE (p < 0.05)")
        else:
            logger.info("  ✗ Pas de saisonnalité significative")
        
        return {
            "chi2": chi2,
            "p_value": p_value,
            "ddl": dof,
        }


def executer_eda():
    """Exécute pipeline complet EDA"""
    logger.info("=" * 60)
    logger.info("📊 DEBUT ANALYSE EXPLORATOIRE")
    logger.info("=" * 60)
    
    analyseur = AnalyseurExploratoire()
    
    # Charger données
    try:
        df_obs, df_grille, df_meteo = analyseur.charger_donnees()
    except FileNotFoundError:
        logger.error("Données non trouvées. Exécutez scripts/nettoyage.py d'abord.")
        return
    
    # Analyses
    logger.info("\n--- SAISONNALITE ---")
    saisonnalite = analyseur.analyser_saisonnalite(df_obs)
    
    logger.info("\n--- CARTE DENSITE ---")
    analyseur.creer_carte_densite(df_obs)

    logger.info("\n--- CORRELATIONS METEO ---")
    analyseur.analyser_correlations(df_grille, df_meteo)
    
    logger.info("\n--- TESTS STATISTIQUES ---")
    resultats_test = analyseur.test_independance_chi2(df_obs)
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ EXPLORATION TERMINEE")
    logger.info(f"Sorties : {analyseur.repertoire_sorties}")
    logger.info("=" * 60)


if __name__ == "__main__":
    executer_eda()
