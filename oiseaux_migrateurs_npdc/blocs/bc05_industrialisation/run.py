"""
BC05 - Industrialisation : demonstration hors-serveur
========================================================

Ce script est AUTONOME : il ne lance pas de serveur (l'API et le
dashboard sont des processus longue duree, prevus pour etre lances a la
main -- voir les commandes affichees a la fin de ce script). A la place,
il PROUVE que la chaine d'industrialisation fonctionne :

  1. Il charge le vrai modele de production (modeles/pipeline_ml.pkl,
     produit par BC03) exactement comme le fait blocs/bc05_industrialisation/api.py
     au demarrage.
  2. Il rejoue, sans serveur, la logique exacte de l'endpoint POST /predict
     sur un exemple concret, et affiche le resultat.
  3. Il rappelle les commandes pour lancer reellement l'API, le dashboard,
     et l'image Docker, pour la demonstration live devant le jury.

Utilisation :
    python blocs/bc05_industrialisation/run.py
"""

import sys
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

RACINE_PROJET = Path(__file__).resolve().parents[2]
if str(RACINE_PROJET) not in sys.path:
    sys.path.insert(0, str(RACINE_PROJET))

from commun.config import REPERTOIRE_MODELES, ESPECES  # noqa: E402


def demo_prediction() -> None:
    chemin_modele = REPERTOIRE_MODELES / "pipeline_ml.pkl"
    if not chemin_modele.exists():
        print("Modele de production introuvable. Lancez d'abord : python blocs/bc03_machine_learning/run.py")
        return

    modele = joblib.load(chemin_modele)
    print(f"Modele de production charge : {chemin_modele.name}\n")

    exemple_requete = {
        "espece": "hirondelle_rustique",
        "latitude": 50.5,
        "longitude": 2.75,
        "meteo": {
            "temperature_max": 18.5,
            "temperature_min": 12.3,
            "precipitation_sum": 2.1,
            "vent_max": 15.0,
            "humidite_moyenne": 65.0,
            "jour_annee": 105,
        },
    }

    jour_annee = exemple_requete["meteo"]["jour_annee"]
    semaine = (jour_annee - 1) // 7 + 1
    donnees_features = {
        "annee": datetime.now().year,
        "semaine": semaine,
        "lat_discrete": round(exemple_requete["latitude"], 1),
        "lon_discrete": round(exemple_requete["longitude"], 1),
        "temperature_max": exemple_requete["meteo"]["temperature_max"],
        "temperature_min": exemple_requete["meteo"]["temperature_min"],
        "precipitation_sum": exemple_requete["meteo"]["precipitation_sum"],
        "vent_max": exemple_requete["meteo"]["vent_max"],
        "humidite_moyenne": exemple_requete["meteo"]["humidite_moyenne"],
        "temperature_moyenne": (exemple_requete["meteo"]["temperature_max"] + exemple_requete["meteo"]["temperature_min"]) / 2,
        "pression_moyenne": np.nan,
    }
    colonnes_attendues = list(getattr(modele, "feature_names_in_", donnees_features.keys()))
    donnees_features = {col: donnees_features.get(col, 0) for col in colonnes_attendues}
    features = pd.DataFrame([donnees_features]).fillna(0)

    probabilite = float(modele.predict_proba(features)[0][1])
    confiance = "HAUTE" if probabilite > 0.75 else ("MOYENNE" if probabilite > 0.60 else "BASSE")

    print("Requete envoyee (equivalent d'un appel POST /predict) :")
    for cle, valeur in exemple_requete.items():
        print(f"   {cle}: {valeur}")
    print("\nReponse simulee de l'API :")
    print(f"   probabilite_presence : {probabilite*100:.1f}%")
    print(f"   confiance             : {confiance}")
    print(f"   modele_utilise        : XGBoost")


def main() -> None:
    print("\n" + "#" * 70)
    print("# BC05 - INDUSTRIALISATION (API + Dashboard + Docker)")
    print("#" * 70 + "\n")

    print("Especes exposees par l'API :")
    for cle, infos in ESPECES.items():
        print(f"  - {cle} ({infos['nom_francais']})")

    print("\n--- Demonstration de /predict, sans lancer de serveur ---\n")
    demo_prediction()

    print("\n" + "-" * 70)
    print("Pour lancer reellement les services (dans des terminaux separes) :")
    print("-" * 70)
    print("  # API (http://127.0.0.1:8000/docs pour la documentation interactive)")
    print("  python -m uvicorn blocs.bc05_industrialisation.api:app --reload")
    print()
    print("  # Dashboard (http://localhost:8501)")
    print("  python -m streamlit run blocs/bc05_industrialisation/dashboard.py")
    print()
    print("  # Conteneur Docker (empaquette l'API)")
    print("  docker build -t oiseaux-migrateurs-api .")
    print("  docker run -p 8000:8000 oiseaux-migrateurs-api")

    print("\nBC05 termine. Bloc suivant : blocs/bc06_gestion_projet/run.py\n")


if __name__ == "__main__":
    main()
