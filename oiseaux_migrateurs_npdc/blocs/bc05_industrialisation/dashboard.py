"""
BC05 - Dashboard Streamlit pour predictions oiseaux migrateurs
==================================================================

Interface utilisateur interactive, pensee pour un utilisateur qui ne
sait pas coder. Appelle l'API definie dans api.py (meme dossier).

Ce bloc est autonome : lancement depuis son propre dossier
(blocs/bc05_industrialisation/) :
    python -m streamlit run dashboard.py
"""

import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from commun.config import REPERTOIRE_DONNEES_TRAITEES, REPERTOIRE_MODELES, REPERTOIRE_RACINE
from commun.chargement import charger_observations_nettoyees, charger_grille_hebdomadaire

st.set_page_config(page_title="Oiseaux Migrateurs NPDC", layout="wide", initial_sidebar_state="expanded")

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1f77b4; text-align: center; margin-bottom: 1rem; }
    .info-box { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">Prediction Oiseaux Migrateurs - Nord-Pas-de-Calais</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Configuration")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            st.success("API connectee")
            st.metric("Version API", health.get("version", "N/A"))
            st.metric("Modele charge", "Oui" if health.get("modele_charge") else "Non")
        else:
            st.error("API non disponible")
    except Exception as e:
        st.error(f"Erreur connexion API : {e}")

    st.markdown("---")
    st.markdown("### A propos")
    st.markdown("""
    Ce dashboard permet de predire la probabilite de presence d'oiseaux migrateurs
    en fonction de la saison et des conditions meteorologiques.

    **Modele :** XGBoost
    **Region :** Nord-Pas-de-Calais
    **Donnees :** GBIF + Open-Meteo
    """)

tab1, tab2, tab3, tab4 = st.tabs(["Prediction", "Statistiques", "Donnees", "Documentation"])

# ========== ONGLET 1 : PREDICTION ==========
with tab1:
    st.header("Faire une prediction")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Parametres biologiques")
        espece = st.selectbox(
            "Espece",
            options=["cigogne_blanche", "hirondelle_rustique", "martinet_noir", "bergeronnette_printaniere"],
            format_func=lambda x: {
                "cigogne_blanche": "Cigogne blanche",
                "hirondelle_rustique": "Hirondelle rustique",
                "martinet_noir": "Martinet noir",
                "bergeronnette_printaniere": "Bergeronnette printaniere",
            }[x],
        )
        jour_annee = st.slider("Jour de l'annee", min_value=1, max_value=365, value=120,
                                help="1 = 1er janvier, 120 = debut mai")
        date_correspondante = pd.Timestamp("2024-01-01") + pd.Timedelta(days=jour_annee - 1)
        st.info(date_correspondante.strftime("%d %B"))

    with col2:
        st.subheader("Conditions meteorologiques")
        temperature_max = st.slider("Temperature max (deg C)", -10.0, 40.0, 18.5, 0.5)
        temperature_min = st.slider("Temperature min (deg C)", -20.0, 30.0, 12.3, 0.5)
        precipitation_sum = st.slider("Precipitations (mm)", 0.0, 100.0, 2.1, 0.1)
        vent_max = st.slider("Vent max (km/h)", 0.0, 100.0, 15.0, 1.0)
        humidite_moyenne = st.slider("Humidite moyenne (%)", 0.0, 100.0, 65.0, 1.0)

    st.subheader("Localisation")
    col_lat, col_lon = st.columns(2)
    with col_lat:
        latitude = st.number_input("Latitude", 49.5, 51.5, 50.5, 0.1)
    with col_lon:
        longitude = st.number_input("Longitude", 1.5, 4.0, 2.75, 0.1)

    if st.button("Lancer la prediction", type="primary", use_container_width=True):
        with st.spinner("Calcul en cours..."):
            try:
                payload = {
                    "espece": espece,
                    "latitude": latitude,
                    "longitude": longitude,
                    "meteo": {
                        "temperature_max": temperature_max,
                        "temperature_min": temperature_min,
                        "precipitation_sum": precipitation_sum,
                        "vent_max": vent_max,
                        "humidite_moyenne": humidite_moyenne,
                        "jour_annee": jour_annee,
                    },
                }
                response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
                if response.status_code == 200:
                    resultat = response.json()
                    st.success("Prediction reussie")
                    col_res1, col_res2, col_res3 = st.columns(3)
                    with col_res1:
                        st.metric("Probabilite de presence", f"{resultat['probabilite_presence']*100:.2f}%")
                    with col_res2:
                        st.metric("Confiance", resultat["confiance"])
                    with col_res3:
                        st.metric("Modele", resultat["modele_utilise"])

                    fig = px.bar(x=[resultat["probabilite_presence"]], y=["Probabilite"], orientation="h",
                                 range_x=[0, 1], color_discrete_sequence=["#1f77b4"])
                    fig.update_layout(showlegend=False, height=150, margin=dict(l=0, r=0, t=20, b=0),
                                       xaxis_title="Probabilite", yaxis_title="")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(f"Erreur API : {response.status_code}")
                    st.json(response.json())
            except Exception as e:
                st.error(f"Erreur : {e}")

# ========== ONGLET 2 : STATISTIQUES ==========
with tab2:
    st.header("Statistiques du projet")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Donnees")
        try:
            chemin_obs = REPERTOIRE_DONNEES_TRAITEES / "observations_nettoyees.parquet"
            if chemin_obs.exists():
                df_obs = charger_observations_nettoyees()
                st.metric("Observations nettoyees", f"{len(df_obs):,}")
                st.metric("Especes", df_obs["espece"].nunique())
                if "date_observation" in df_obs.columns:
                    date_min = pd.to_datetime(df_obs["date_observation"]).min()
                    date_max = pd.to_datetime(df_obs["date_observation"]).max()
                    st.metric("Periode", f"{date_min.year} - {date_max.year}")
            else:
                st.warning("Donnees non disponibles (donnees/traitees/ manquant dans ce dossier).")
        except Exception as e:
            st.error(f"Erreur chargement donnees : {e}")

    with col2:
        st.subheader("Modeles")
        try:
            chemin_eval = REPERTOIRE_MODELES / "evaluations.csv"
            if chemin_eval.exists():
                df_eval = pd.read_csv(chemin_eval, index_col=0)
                st.dataframe(df_eval.style.highlight_max(axis=0), use_container_width=True)
            else:
                st.info("Evaluations non disponibles (modeles/evaluations.csv manquant dans ce dossier).")
        except Exception as e:
            st.error(f"Erreur : {e}")

    st.subheader("Saisonnalite des observations")
    try:
        image_path = REPERTOIRE_RACINE / "outputs" / "eda" / "saisonnalite.png"
        if image_path.exists():
            st.image(str(image_path), use_column_width=True)
        else:
            st.info("Graphique non disponible (outputs/eda/saisonnalite.png manquant dans ce dossier).")
    except Exception as e:
        st.warning(f"Image non chargee : {e}")

# ========== ONGLET 3 : DONNEES ==========
with tab3:
    st.header("Donnees visibles")
    st.caption("Apercu des donnees nettoyees et des distributions principales.")
    try:
        chemin_obs = REPERTOIRE_DONNEES_TRAITEES / "observations_nettoyees.parquet"
        chemin_grille = REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet"

        if chemin_obs.exists():
            df_obs = charger_observations_nettoyees()
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Apercu des observations")
                st.dataframe(df_obs.head(50), use_container_width=True)
            with col2:
                st.subheader("Repartition par espece")
                if "espece" in df_obs.columns:
                    counts = df_obs["espece"].value_counts().reset_index()
                    counts.columns = ["espece", "nombre_observations"]
                    fig = px.bar(counts, x="espece", y="nombre_observations", color="espece",
                                 title="Nombre d'observations par espece")
                    st.plotly_chart(fig, use_container_width=True)

            if chemin_grille.exists():
                df_grille = charger_grille_hebdomadaire()
                st.subheader("Presence / absence")
                if "presence" in df_grille.columns:
                    presence_counts = df_grille["presence"].value_counts().reset_index()
                    presence_counts.columns = ["presence", "nombre"]
                    fig2 = px.pie(presence_counts, names="presence", values="nombre",
                                  title="Repartition presence / absence")
                    st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("Les donnees nettoyees ne sont pas disponibles (donnees/traitees/ manquant "
                       "dans ce dossier).")
    except Exception as e:
        st.error(f"Erreur affichage donnees : {e}")

# ========== ONGLET 4 : DOCUMENTATION ==========
with tab4:
    st.header("Documentation")
    st.markdown("""
    ### Objectif du projet
    Predire la probabilite de presence d'oiseaux migrateurs dans le Nord-Pas-de-Calais
    en fonction de la saison, des conditions meteorologiques et de la geolocalisation.

    ### Sources de donnees
    - **GBIF** : observations d'oiseaux
    - **Open-Meteo** : donnees meteorologiques historiques gratuites

    ### Modeles
    - **XGBoost** : Gradient Boosting (en production)
    - **Random Forest** : comparaison
    - **Regression logistique** : reference

    ### Ce dossier (BC05 - Industrialisation)
    Ce bloc est autonome : `api.py` (API FastAPI), `dashboard.py` (ce tableau de bord),
    `prediction.py` (logique de prediction partagee) et une copie figee du modele de production
    (`modeles/pipeline_ml.pkl`) et des donnees necessaires a l'affichage (`donnees/traitees/`,
    `outputs/eda/`), produits par les blocs BC01/BC02/BC03 du meme projet RNCP.

    ### Utilisation API
    ```
    GET  http://localhost:8000/health
    GET  http://localhost:8000/species
    POST http://localhost:8000/predict
    ```
    """)

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Oiseaux Migrateurs NPDC | "
    "Propulse par FastAPI + Streamlit + XGBoost</div>",
    unsafe_allow_html=True,
)
