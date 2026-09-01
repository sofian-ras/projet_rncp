"""
BC02 - Analyse exploratoire des observations et de la meteo
=============================================================

Ce script est AUTONOME : il lit les donnees deja nettoyees par BC01
(donnees/traitees/*.parquet) et produit les visualisations et tests
statistiques de l'analyse exploratoire. Il ne re-execute jamais le
code de BC01 : il se contente de lire ses resultats sur disque.

Ce bloc est autonome : donnees/traitees/ embarque une copie figee des
parquets produits par BC01, pour pouvoir etre execute (et envoye) seul.

Utilisation :
    python blocs/bc02_analyse_exploratoire/run.py
"""

from pathlib import Path
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import folium
from folium.plugins import HeatMap
from scipy import stats

from commun.config import REPERTOIRE_DONNEES_TRAITEES, REPERTOIRE_RACINE, ESPECES, ZONE_GEOGRAPHIQUE
from commun.journalisation import configurer_logger
from commun.chargement import (
    charger_observations_nettoyees,
    charger_grille_hebdomadaire,
    charger_meteo_traitee,
)

RACINE_PROJET = REPERTOIRE_RACINE

logger = configurer_logger()

plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")


class AnalyseurExploratoire:
    """Analyse exploratoire observations + meteo"""

    def __init__(self):
        self.repertoire_sorties = REPERTOIRE_RACINE / "outputs" / "eda"
        self.repertoire_sorties.mkdir(parents=True, exist_ok=True)

    def charger_donnees(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Charge observations, grille et meteo traitee -- produites par BC01"""
        chemin_obs = REPERTOIRE_DONNEES_TRAITEES / "observations_nettoyees.parquet"
        chemin_grille = REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet"
        chemin_meteo = REPERTOIRE_DONNEES_TRAITEES / "meteo_processed.parquet"

        if not chemin_obs.exists() or not chemin_grille.exists():
            raise FileNotFoundError(
                "Donnees introuvables dans donnees/traitees/ (copie figee produite par BC01, "
                "livree avec ce dossier)."
            )

        df_obs = charger_observations_nettoyees()
        df_grille = charger_grille_hebdomadaire()
        df_meteo = charger_meteo_traitee() if chemin_meteo.exists() else pd.DataFrame()

        logger.info(f"Observations chargees : {len(df_obs)}")
        logger.info(f"Grille chargee : {len(df_grille)}")
        logger.info(f"Meteo chargee : {len(df_meteo)}")
        return df_obs, df_grille, df_meteo

    def analyser_saisonnalite(self, df_obs: pd.DataFrame) -> pd.DataFrame:
        """Analyse distribution observations par mois/semaine"""
        logger.info("Analyse saisonnalite...")
        df_obs["mois"] = pd.to_datetime(df_obs["date_observation"]).dt.month
        df_obs["semaine_annee"] = pd.to_datetime(df_obs["date_observation"]).dt.isocalendar().week
        saisonnalite = df_obs.groupby(["mois", "espece"]).size().reset_index(name="nombre_observations")

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Saisonnalite des Observations - NPDC", fontsize=16, fontweight="bold")

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
            for mois in infos["mois_arrivee"]:
                ax.axvline(mois, color="green", linestyle="--", alpha=0.5, linewidth=2)

        plt.tight_layout()
        plt.savefig(self.repertoire_sorties / "saisonnalite.png", dpi=300, bbox_inches="tight")
        plt.close(fig)
        logger.info("  Graphique saisonnalite sauvegarde")
        return saisonnalite

    def creer_carte_densite(self, df_obs: pd.DataFrame) -> folium.Map:
        """Cree carte heatmap densite observations"""
        logger.info("Creation carte densite...")
        centre = [ZONE_GEOGRAPHIQUE.centre_latitude, ZONE_GEOGRAPHIQUE.centre_longitude]
        carte = folium.Map(location=centre, zoom_start=9, tiles="OpenStreetMap")

        donnees_heatmap = df_obs[["latitude", "longitude"]].values.tolist()
        HeatMap(donnees_heatmap, radius=15, blur=25, max_zoom=1).add_to(carte)
        folium.CircleMarker(location=centre, radius=5, color="red", fill=True, popup="Centre NPDC").add_to(carte)

        chemin_carte = self.repertoire_sorties / "carte_densite.html"
        carte.save(str(chemin_carte))
        logger.info(f"  Carte sauvegardee : {chemin_carte.name}")
        return carte

    def analyser_distributions(self, df_meteo: pd.DataFrame) -> pd.DataFrame:
        """Analyse univariee des variables meteo : moyennes, ecarts-types, valeurs extremes (regle IQR)."""
        logger.info("Analyse univariee (distributions meteo)...")
        if df_meteo.empty:
            logger.warning("  Donnees meteo absentes. Analyse univariee non calculee.")
            return pd.DataFrame()

        variables = df_meteo.select_dtypes("number").columns
        resume = df_meteo[variables].agg(["mean", "std", "min", "max"]).T

        q1, q3 = df_meteo[variables].quantile(0.25), df_meteo[variables].quantile(0.75)
        iqr = q3 - q1
        resume["extremes_iqr"] = (
            (df_meteo[variables] < q1 - 1.5 * iqr) | (df_meteo[variables] > q3 + 1.5 * iqr)
        ).sum()
        logger.info("\n" + resume.round(2).to_string())

        axes = df_meteo[variables].hist(figsize=(14, 8), bins=30, color="steelblue", edgecolor="black")
        figure = axes.flat[0].get_figure()
        figure.suptitle("Distributions des variables meteo", fontsize=14, fontweight="bold")
        figure.tight_layout()
        figure.savefig(self.repertoire_sorties / "distributions_meteo.png", dpi=150, bbox_inches="tight")
        plt.close(figure)
        logger.info("  Graphique distributions_meteo.png sauvegarde")
        return resume

    def analyser_correlations(self, df_grille: pd.DataFrame, df_meteo: pd.DataFrame) -> pd.DataFrame:
        """Analyse correlations meteo / presence"""
        logger.info("Analyse correlations...")
        if df_meteo.empty:
            logger.warning("  Donnees meteo absentes. Correlations non calculees.")
            return pd.DataFrame()

        df_meteo["date"] = pd.to_datetime(df_meteo["date"])
        df_meteo["annee"] = df_meteo["date"].dt.isocalendar().year.astype(int)
        df_meteo["semaine"] = df_meteo["date"].dt.isocalendar().week.astype(int)

        variables_meteo = [
            "temperature_max", "temperature_min", "precipitation_sum", "vent_max",
            "humidite_moyenne", "temperature_moyenne", "pression_moyenne",
        ]
        variables_meteo = [v for v in variables_meteo if v in df_meteo.columns]
        meteo_hebdo = df_meteo.groupby(["annee", "semaine"], as_index=False)[variables_meteo].mean()

        df_fusion = df_grille.merge(meteo_hebdo, on=["annee", "semaine"], how="left")
        if df_fusion.empty or "presence" not in df_fusion.columns or df_fusion["presence"].nunique() < 2:
            logger.warning("  Aucune donnee exploitable pour les correlations.")
            return pd.DataFrame()

        correlations = {}
        for espece in df_fusion["espece"].unique():
            df_espece = df_fusion[df_fusion["espece"] == espece]
            correlations[espece] = {
                var: df_espece["presence"].corr(df_espece[var])
                for var in variables_meteo if df_espece[var].notna().sum() > 0
            }

        df_corr = pd.DataFrame(correlations).T
        if not df_corr.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(df_corr, annot=True, fmt=".3f", cmap="RdBu_r", center=0,
                        cbar_kws={"label": "Correlation"}, ax=ax, vmin=-0.5, vmax=0.5)
            ax.set_title("Correlations Meteo / Presence Oiseaux", fontsize=14, fontweight="bold")
            ax.set_xlabel("Variables meteorologiques", fontsize=11)
            ax.set_ylabel("Especes", fontsize=11)
            plt.tight_layout()
            plt.savefig(self.repertoire_sorties / "correlations_meteo.png", dpi=300, bbox_inches="tight")
            plt.close(fig)
            logger.info("  Heatmap correlations sauvegardee")

        return df_corr

    @staticmethod
    def test_independance_chi2(df_obs: pd.DataFrame) -> Dict[str, float]:
        """Test independance chi2 entre espece et mois"""
        logger.info("Tests d'independance (chi2)...")
        df_obs["mois"] = pd.to_datetime(df_obs["date_observation"]).dt.month
        tableau_contingence = pd.crosstab(df_obs["espece"], df_obs["mois"])
        chi2, p_value, dof, _ = stats.chi2_contingency(tableau_contingence)

        logger.info(f"  chi2 = {chi2:.4f}, p-value = {p_value:.2e}, ddl = {dof}")
        if p_value < 0.05:
            logger.info("  Saisonnalite SIGNIFICATIVE (p < 0.05)")
        else:
            logger.info("  Pas de saisonnalite significative")
        return {"chi2": chi2, "p_value": p_value, "ddl": dof}


def main() -> None:
    print("\n" + "#" * 70)
    print("# BC02 - ANALYSE EXPLORATOIRE")
    print("#" * 70 + "\n")

    analyseur = AnalyseurExploratoire()
    try:
        df_obs, df_grille, df_meteo = analyseur.charger_donnees()
    except FileNotFoundError as erreur:
        logger.error(str(erreur))
        return

    logger.info("\n--- SAISONNALITE ---")
    analyseur.analyser_saisonnalite(df_obs)

    logger.info("\n--- DISTRIBUTIONS UNIVARIEES ---")
    analyseur.analyser_distributions(df_meteo)

    logger.info("\n--- CARTE DENSITE ---")
    analyseur.creer_carte_densite(df_obs)

    logger.info("\n--- CORRELATIONS METEO ---")
    analyseur.analyser_correlations(df_grille, df_meteo)

    logger.info("\n--- TESTS STATISTIQUES ---")
    analyseur.test_independance_chi2(df_obs)

    print("\nPreuves produites (fichiers verifiables sur disque) :")
    for chemin in [
        analyseur.repertoire_sorties / "saisonnalite.png",
        analyseur.repertoire_sorties / "distributions_meteo.png",
        analyseur.repertoire_sorties / "carte_densite.html",
        analyseur.repertoire_sorties / "correlations_meteo.png",
    ]:
        marque = "OK" if chemin.exists() else "MANQUANT"
        print(f"  [{marque}] {chemin.relative_to(RACINE_PROJET)}")

    print("\nBC02 termine.\n")


if __name__ == "__main__":
    main()
