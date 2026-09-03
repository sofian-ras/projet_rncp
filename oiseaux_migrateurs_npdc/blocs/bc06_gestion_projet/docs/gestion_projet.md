# BC06 — Cadrage, rétroplanning, risques et ROI

## 1. Problématique métier traduite en problématique data

| Enjeu métier | Traduction data |
|---|---|
| Savoir *quand* les oiseaux migrateurs arrivent dans le Nord-Pas-de-Calais | Problème de **classification binaire** : présence / absence d'une espèce, par semaine et par maille géographique |
| Comprendre si la météo explique ces arrivées | **Analyse de corrélation** + **importance des variables** d'un modèle supervisé |
| Rendre la prévision utilisable par un non-technicien | **API** + **tableau de bord** exposant la probabilité de présence |

**Problématique scientifique retenue :** peut-on modéliser l'arrivée des migrations à partir de
variables climatiques et de la position géographique ?

## 2. Rétroplanning (session de septembre 2026)

Planification à rebours depuis la soutenance. Dates à adapter pour une autre session.

| Semaine | Dates | Bloc(s) | Livrables attendus | Dépend de |
|---|---|---|---|---|
| S1 | 11–15 août 2026 | BC01 | Acquisition GBIF + Open-Meteo, pipeline ETL, grille présence/absence | — |
| S2 | 18–22 août 2026 | BC02 | Saisonnalité, distributions univariées, corrélations, test χ² | BC01 |
| S3 | 25–29 août 2026 | BC03 + BC04 | 3 modèles ML comparés + validation croisée + segmentation ; réseau LSTM de sentiment | BC01 |
| S4 | 1–5 sept. 2026 | BC05 + BC06 | API FastAPI, dashboard Streamlit, Docker ; tests, documentation, cette note | BC03 (+ BC04) |
| Soutenance | semaine du 8 sept. 2026 | — | Support oral (10 min) + démo live | tous |

**Jalons :**
- J1 (fin S1) : `grille_presence_hebdo.parquet` produite → feu vert pour BC02/BC03.
- J2 (fin S3) : modèle de production figé (`pipeline_ml.pkl`) → feu vert pour BC05.
- J3 (mi-S4) : API + dashboard fonctionnels en local → répétition de la démo.

**Marge :** une demi-journée tampon par semaine (imprévus API, ré-entraînements). Les parquets de
`donnees/traitees/` et le modèle de production sont versionnés dans le dépôt : un retard sur BC01
ne bloque pas le travail sur les blocs suivants, qui partent de la dernière version figée.

## 3. Analyse des risques

| Risque | Prob. | Impact | Mitigation | Statut |
|---|---|---|---|---|
| API GBIF indisponible (5xx transitoires) | Élevée | Moyen | `get_avec_retry` (backoff exponentiel) + `donnees/traitees/` versionnées dans le dépôt | **Traité** |
| Fort déséquilibre des classes (~97,7 % d'absences) | Certaine | Élevé | Métriques adaptées (F1, AUC-ROC, matrice de confusion) plutôt que l'accuracy ; période bornée à 2019-2024 pour ne pas ajouter d'absences fictives ; SMOTE identifié comme prochaine itération | **Traité (partiel)** |
| Sur-apprentissage du modèle retenu | Moyenne | Moyen | Validation croisée stratifiée 5-fold + écart train/test contrôlé (< 0,05) | **Traité** |
| Météo passée seule, peu prédictive de la présence | Moyenne | Moyen | Limite assumée et documentée ; piste : intégrer des prévisions météo | **Accepté** |
| Biais d'effort d'observation dans les données GBIF | Certaine | Moyen | Signalé explicitement (science citoyenne) ; interprétation prudente des résultats | **Accepté** |
| Déploiement cloud non réalisé (pas d'URL publique) | Certaine | Moyen | Fichiers de déploiement prêts (`Procfile`, `render.yaml`) + procédure documentée dans BC05 | **Ouvert** |
| Incompatibilité de versions au `pip install` (numpy/pandas/mlflow/xgboost) | Faible | Faible | `requirements.txt` épinglé ; suivi MLflow optionnel (dégradation propre si absent) ; validation croisée BC03 réécrite en boucle explicite pour rester insensible aux versions de scikit-learn/xgboost | **Traité** |

## 4. Coûts et bénéfices (ROI)

**Coûts**
- Charge : ~4 semaines-personne (1 personne).
- Infrastructure : **0 €/mois** (sources publiques gratuites, exécution locale). Un déploiement
  cloud minimal (API + dashboard) coûterait ~0–7 €/mois sur une offre gratuite/entrée de gamme.

**Bénéfices**
- **Réutilisabilité** : la chaîne (acquisition → ETL → grille → modèle → API) est générique ;
  changer d'espèces ou de région ne demande que d'ajuster `commun/config.py`.
- **Base d'un service opérationnel** : une association de suivi ornithologique (type LPO) pourrait
  s'en servir pour **prioriser les sorties de comptage** aux semaines et zones à forte probabilité
  de présence — gain de temps bénévole estimé à 1–2 sorties évitées par mois et par observateur.
- **Compétences démontrées** : les 6 blocs du référentiel, de l'infrastructure à l'industrialisation.

**ROI qualitatif** : coût d'infrastructure quasi nul, effort de développement modéré, et un socle
directement transposable à d'autres problématiques de prévision spatio-temporelle sur données
publiques.

## 5. Gouvernance des données et RGPD

- **RGPD** : le projet ne traite **aucune donnée à caractère personnel** (occurrences d'espèces,
  mesures météo). Détail des sources, licences et minimisation dans le document d'architecture de
  BC01 (`bc01_infrastructure_donnees/docs/architecture.md`).
- **Traçabilité** : les URL des API sources sont dans le code (`acquisition.py`) ; les jeux de
  données intermédiaires (`donnees/traitees/`) et le modèle de production (`modeles/pipeline_ml.pkl`)
  sont figés et versionnés à la racine du projet.
- **Reproductibilité** : graines aléatoires fixées (`RANDOM_STATE`), hyperparamètres dans
  `commun/config.py`, suivi des entraînements dans MLflow (`mlruns/` a la racine).
