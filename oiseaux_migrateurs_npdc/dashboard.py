"""
BC05 - Dashboard Streamlit pour prédictions oiseaux migrateurs
Interface utilisateur interactive
"""

import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime
import plotly.express as px
from pathlib import Path

from config import REPERTOIRE_DONNEES_TRAITEES, REPERTOIRE_MODELES, REPERTOIRE_RACINE

# Configuration page
st.set_page_config(
    page_title="🐦 Oiseaux Migrateurs NPDC",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Styles
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Titre principal
st.markdown('<p class="main-header">🐦 Prédiction Oiseaux Migrateurs - Nord-Pas-de-Calais</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Vérifier santé API
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            st.success("✅ API connectée")
            st.metric("Version API", health.get("version", "N/A"))
            st.metric("Modèle chargé", "✅ Oui" if health.get("modele_charge") else "❌ Non")
        else:
            st.error("⚠️ API non disponible")
    except Exception as e:
        st.error(f"❌ Erreur connexion API : {e}")
    
    st.markdown("---")
    st.markdown("### 📊 À propos")
    st.markdown("""
    Ce dashboard permet de prédire la probabilité de présence d'oiseaux migrateurs 
    en fonction de la saison et des conditions météorologiques.
    
    **Modèle :** XGBoost  
    **Région :** Nord-Pas-de-Calais  
    **Données :** GBIF + Open-Meteo
    """)


# Onglets
tab1, tab2, tab3, tab4 = st.tabs(["🔮 Prédiction", "📈 Statistiques", "📂 Données", "ℹ️ Documentation"])

# ========== ONGLET 1 : PRÉDICTION ==========
with tab1:
    st.header("🔮 Faire une prédiction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🐦 Paramètres biologiques")
        
        espece = st.selectbox(
            "Espèce",
            options=["cigogne_blanche", "hirondelle_rustique", "martinet_noir", "bergeronnette_printaniere"],
            format_func=lambda x: {
                "cigogne_blanche": "Cigogne blanche",
                "hirondelle_rustique": "Hirondelle rustique",
                "martinet_noir": "Martinet noir",
                "bergeronnette_printaniere": "Bergeronnette printanière"
            }[x]
        )
        
        jour_annee = st.slider(
            "Jour de l'année",
            min_value=1,
            max_value=365,
            value=120,
            help="1 = 1er janvier, 120 = début mai"
        )
        
        # Afficher date correspondante
        date_correspondante = pd.Timestamp('2024-01-01') + pd.Timedelta(days=jour_annee-1)
        st.info(f"📅 {date_correspondante.strftime('%d %B')}")
    
    with col2:
        st.subheader("🌦️ Conditions météorologiques")
        
        temperature_max = st.slider("Température max (°C)", -10.0, 40.0, 18.5, 0.5)
        temperature_min = st.slider("Température min (°C)", -20.0, 30.0, 12.3, 0.5)
        precipitation_sum = st.slider("Précipitations (mm)", 0.0, 100.0, 2.1, 0.1)
        vent_max = st.slider("Vent max (km/h)", 0.0, 100.0, 15.0, 1.0)
        humidite_moyenne = st.slider("Humidité moyenne (%)", 0.0, 100.0, 65.0, 1.0)
    
    st.subheader("📍 Localisation")
    col_lat, col_lon = st.columns(2)
    with col_lat:
        latitude = st.number_input("Latitude", 49.5, 51.5, 50.5, 0.1)
    with col_lon:
        longitude = st.number_input("Longitude", 1.5, 4.0, 2.75, 0.1)
    
    # Bouton prédiction
    if st.button("🚀 Lancer la prédiction", type="primary", use_container_width=True):
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
                        "jour_annee": jour_annee
                    }
                }
                
                response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
                
                if response.status_code == 200:
                    resultat = response.json()
                    
                    # Affichage résultats
                    st.success("✅ Prédiction réussie !")
                    
                    col_res1, col_res2, col_res3 = st.columns(3)
                    
                    with col_res1:
                        st.metric(
                            "Probabilité de présence",
                            f"{resultat['probabilite_presence']*100:.2f}%"
                        )
                    
                    with col_res2:
                        confiance = resultat['confiance']
                        couleur = {"HAUTE": "🟢", "MOYENNE": "🟡", "BASSE": "🔴"}
                        st.metric("Confiance", f"{couleur.get(confiance, '⚪')} {confiance}")
                    
                    with col_res3:
                        st.metric("Modèle", resultat['modele_utilise'])
                    
                    # Jauge visuelle
                    fig = px.bar(
                        x=[resultat['probabilite_presence']],
                        y=["Probabilité"],
                        orientation='h',
                        range_x=[0, 1],
                        color_discrete_sequence=['#1f77b4']
                    )
                    fig.update_layout(
                        showlegend=False,
                        height=150,
                        margin=dict(l=0, r=0, t=20, b=0),
                        xaxis_title="Probabilité",
                        yaxis_title=""
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                else:
                    st.error(f"❌ Erreur API : {response.status_code}")
                    st.json(response.json())
                    
            except Exception as e:
                st.error(f"❌ Erreur : {e}")


# ========== ONGLET 2 : STATISTIQUES ==========
with tab2:
    st.header("📈 Statistiques du projet")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Données")
        try:
            from pathlib import Path
            from config import REPERTOIRE_DONNEES_TRAITEES
            
            chemin_obs = REPERTOIRE_DONNEES_TRAITEES / "observations_nettoyees.parquet"
            chemin_grille = REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet"
            
            if chemin_obs.exists():
                df_obs = pd.read_parquet(chemin_obs)
                st.metric("Observations nettoyées", f"{len(df_obs):,}")
                st.metric("Espèces", df_obs['espece'].nunique())
                
                if 'date_observation' in df_obs.columns:
                    date_min = pd.to_datetime(df_obs['date_observation']).min()
                    date_max = pd.to_datetime(df_obs['date_observation']).max()
                    st.metric("Période", f"{date_min.year} - {date_max.year}")
            else:
                st.warning("Données non disponibles")
                
        except Exception as e:
            st.error(f"Erreur chargement données : {e}")
    
    with col2:
        st.subheader("🤖 Modèles")
        try:
            chemin_eval = REPERTOIRE_MODELES / "evaluations.csv"
            if chemin_eval.exists():
                df_eval = pd.read_csv(chemin_eval, index_col=0)
                st.dataframe(df_eval.style.highlight_max(axis=0), use_container_width=True)
            else:
                st.info("Évaluations non disponibles")
        except Exception as e:
            st.error(f"Erreur : {e}")
    
    # Graphique saisonnalité
    st.subheader("📅 Saisonnalité des observations")
    try:
        image_path = REPERTOIRE_RACINE / "outputs" / "eda" / "saisonnalite.png"
        if image_path.exists():
            st.image(str(image_path), use_column_width=True)
        else:
            st.info("Graphique non disponible. Exécutez scripts/eda.py")
    except Exception as e:
        st.warning(f"Image non chargée : {e}")


# ========== ONGLET 3 : DONNÉES ==========
with tab3:
    st.header("📂 Données visibles")
    st.caption("Aperçu des données nettoyées et des distributions principales.")

    try:
        from config import REPERTOIRE_DONNEES_TRAITEES

        chemin_obs = REPERTOIRE_DONNEES_TRAITEES / "observations_nettoyees.parquet"
        chemin_grille = REPERTOIRE_DONNEES_TRAITEES / "grille_presence_hebdo.parquet"

        if chemin_obs.exists():
            df_obs = pd.read_parquet(chemin_obs)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Aperçu des observations")
                st.dataframe(df_obs.head(50), use_container_width=True)

            with col2:
                st.subheader("Répartition par espèce")
                if "espece" in df_obs.columns:
                    counts = df_obs["espece"].value_counts().reset_index()
                    counts.columns = ["espece", "nombre_observations"]
                    fig = px.bar(
                        counts,
                        x="espece",
                        y="nombre_observations",
                        color="espece",
                        title="Nombre d'observations par espèce",
                    )
                    st.plotly_chart(fig, use_container_width=True)

            if chemin_grille.exists():
                df_grille = pd.read_parquet(chemin_grille)
                st.subheader("Présence / absence")
                if "presence" in df_grille.columns:
                    presence_counts = df_grille["presence"].value_counts().reset_index()
                    presence_counts.columns = ["presence", "nombre"]
                    fig2 = px.pie(
                        presence_counts,
                        names="presence",
                        values="nombre",
                        title="Répartition présence / absence",
                    )
                    st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("Les données nettoyées ne sont pas encore disponibles. Lance d'abord le pipeline.")

    except Exception as e:
        st.error(f"Erreur affichage données : {e}")


# ========== ONGLET 3 : DOCUMENTATION ==========
with tab4:
    st.header("ℹ️ Documentation")
    
    st.markdown("""
    ### 🎯 Objectif du projet
    
    Prédire la probabilité de présence d'oiseaux migrateurs dans le Nord-Pas-de-Calais 
    en fonction de :
    - La **saison** (jour de l'année)
    - Les **conditions météorologiques** (température, pluie, vent, humidité)
    - La **géolocalisation** (latitude, longitude)
    
    ### 📊 Sources de données
    
    - **GBIF** : Global Biodiversity Information Facility (observations d'oiseaux)
    - **Open-Meteo** : Données météorologiques historiques gratuites
    
    ### 🤖 Modèles
    
    - **XGBoost** : Gradient Boosting optimisé (en production)
    - **Random Forest** : Forêts aléatoires (comparaison)
    - **Logistic Regression** : Régression logistique (baseline)
    
    ### 🐦 Espèces étudiées
    
    1. **Hirondelle rustique** (*Barn Swallow*) - Arrive en avril-mai
    2. **Cigogne blanche** (*White Stork*) - Arrive en mars-avril
    3. **Martinet noir** (*Common Swift*) - Arrive en mai-juin
    4. **Bergeronnette printanière** (*White Wagtail*) - Arrive en mars-avril
    
    ### 📁 Architecture
    
    ```
    oiseaux_migrateurs_npdc/
    ├── api/                    # API FastAPI
    ├── scripts/                # Pipeline data + ML
    ├── donnees/                # Datasets
    ├── modeles/                # Modèles sérialisés
    ├── dashboard.py            # Cette interface
    └── requirements.txt
    ```
    
    ### 🚀 Utilisation API
    
    ```bash
    # Santé
    GET http://localhost:8000/health
    
    # Liste espèces
    GET http://localhost:8000/species
    
    # Prédiction
    POST http://localhost:8000/predict
    {
      "espece": "cigogne_blanche",
      "latitude": 50.5,
      "longitude": 2.75,
      "meteo": {
        "temperature_max": 18.5,
        "temperature_min": 12.3,
        "precipitation_sum": 2.1,
        "vent_max": 15.0,
        "humidite_moyenne": 65.0,
        "jour_annee": 120
      }
    }
    ```

    ### 🌐 Mise en ligne

    Pour rendre l'interface accessible sur internet :
    - déployer l'API FastAPI sur Render, Railway ou Cloud Run ;
    - déployer le dashboard Streamlit sur Streamlit Community Cloud ou un service équivalent ;
    - configurer la variable d'environnement `API_URL` avec l'URL publique de l'API.

    Exemple :
    ```bash
    API_URL=https://mon-api-publique.example.com
    ```
    
    ### 👨‍💻 Développeur
    
    Projet RNCP - Concepteur Développeur en Science des Données  
    Année 2026
    """)


# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>🐦 Oiseaux Migrateurs NPDC | "
    "Propulsé par FastAPI + Streamlit + XGBoost</div>",
    unsafe_allow_html=True
)
