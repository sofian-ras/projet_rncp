"""
BC05 - Industrialisation : demonstration hors-serveur
========================================================

Ce script ne lance pas de serveur (l'API et le dashboard sont des processus
longue duree, lances a la main -- voir les commandes affichees a la fin).
A la place, il PROUVE que la chaine d'industrialisation fonctionne :

  1. Il charge le modele de production (modeles/pipeline_ml.pkl, produit par
     BC03) exactement comme le fait api.py au demarrage.
  2. Il rejoue, sans serveur, la logique exacte de l'endpoint POST /predict
     sur un exemple concret, et affiche le resultat.
  3. Il rappelle les commandes pour lancer reellement l'API, le dashboard,
     et l'image Docker, pour la demonstration live devant le jury.

Utilisation :
    python run.py
"""

import sys
from pathlib import Path

import joblib

_racine = next(p for p in Path(__file__).resolve().parents if (p / "commun").is_dir())
sys.path.insert(0, str(_racine))  # racine du projet -> package commun/

from commun.config import REPERTOIRE_MODELES, ESPECES
from commun.journalisation import configurer_logger
from prediction import predire

logger = configurer_logger()


def demo_prediction() -> None:
    chemin_modele = REPERTOIRE_MODELES / "pipeline_ml.pkl"
    if not chemin_modele.exists():
        logger.warning("Modele de production introuvable. Lancez d'abord : python blocs/bc03_machine_learning/run.py")
        return

    modele = joblib.load(chemin_modele)
    logger.info(f"Modele de production charge : {chemin_modele.name}")

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

    probabilite, confiance = predire(
        modele, exemple_requete["latitude"], exemple_requete["longitude"], exemple_requete["meteo"],
    )

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
    print("Pour lancer reellement les services (dans des terminaux separes,")
    print("depuis ce dossier blocs/bc05_industrialisation/) :")
    print("-" * 70)
    print("  # API (http://127.0.0.1:8000/docs pour la documentation interactive)")
    print("  python -m uvicorn api:app --reload")
    print()
    print("  # Dashboard (http://localhost:8501)")
    print("  python -m streamlit run dashboard.py")
    print()
    print("  # Conteneur Docker (empaquette l'API)")
    print("  docker build -t oiseaux-migrateurs-api .")
    print("  docker run -p 8000:8000 oiseaux-migrateurs-api")

    print("\nBC05 termine.\n")


if __name__ == "__main__":
    main()
