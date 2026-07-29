# Sujets de Soutenance pour le RNCP35288

**Référentiel : Titre RNCP — Concepteur Développeur en Science des Données**

Ce document propose plusieurs sujets de projet couvrant l'ensemble des **6 blocs de compétences** du titre RNCP35288 (niveau 6).

---

## Rappel des blocs de compétences

| Code | Intitulé |
|------|----------|
| **BC01** | Construction et alimentation d'une infrastructure de gestion de données |
| **BC02** | Analyse exploratoire, descriptive et inférentielle de données |
| **BC03** | Analyse prédictive de données structurées par IA (Machine Learning) |
| **BC04** | Analyse prédictive de données non-structurées par IA (Deep Learning) |
| **BC05** | Industrialisation d'un algorithme et automatisation des processus de décision |
| **BC06** | Direction de projets de gestion de données |

---

## Sujet 1 : Plateforme de prédiction de la qualité de l'air

### Contexte

Créer un système end-to-end de prévision de la pollution atmosphérique pour les grandes agglomérations françaises.

### Application par bloc

| Bloc | Application concrète |
|------|----------------------|
| **BC01** | Data Lake ingérant données météo (Open-Meteo API), capteurs pollution (data.gouv.fr - LCSQA), trafic routier. Pipeline ETL avec Airflow + stockage Parquet/DuckDB |
| **BC02** | Analyse exploratoire des corrélations pollution/météo/saison, visualisations Plotly, tests statistiques sur les pics de pollution |
| **BC03** | Modèles ML (XGBoost, Random Forest) pour prédire PM2.5/PM10 à J+1, feature engineering temporel |
| **BC04** | LSTM/Transformer pour séries temporelles multi-variées, comparaison avec modèles classiques |
| **BC05** | API FastAPI dockerisée, pipeline MLflow, déploiement cloud (GCP/AWS), alertes automatiques |
| **BC06** | Gestion projet Agile, documentation, présentation stakeholders, analyse ROI |

### Sources de données

- [data.gouv.fr — Qualité de l'air](https://www.data.gouv.fr/fr/datasets/?q=qualit%C3%A9+air)
- [Open-Meteo API](https://open-meteo.com/)
- [European Environment Agency](https://www.eea.europa.eu/data-and-maps)

---

## Sujet 2 : Système de détection de fraude sur transactions financières

### Contexte

Détecter les transactions frauduleuses sur un dataset bancaire en utilisant des techniques de machine learning et deep learning.

### Application par bloc

| Bloc | Application concrète |
|------|----------------------|
| **BC01** | Architecture Data Warehouse (schéma en étoile), ingestion streaming simulée avec Kafka, stockage PostgreSQL + Redis |
| **BC02** | Analyse du déséquilibre de classes, profiling des fraudeurs, statistiques descriptives, détection d'anomalies univariées |
| **BC03** | Modèles supervisés (Logistic Regression, Gradient Boosting), gestion du déséquilibre (SMOTE), optimisation seuil de décision |
| **BC04** | Autoencoders pour détection d'anomalies, réseaux de neurones sur embeddings de séquences |
| **BC05** | API temps réel, scoring en production, monitoring des drifts avec Evidently, conteneurisation |
| **BC06** | Gestion du projet, conformité RGPD, documentation technique, KPIs métier |

### Sources de données

- [Kaggle — Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
- [IEEE-CIS Fraud Detection](https://www.kaggle.com/c/ieee-fraud-detection)

---

## Sujet 3 : Analyse et classification automatique des offres d'emploi

### Contexte

Extraire, analyser et classifier automatiquement les offres d'emploi du marché français pour identifier les tendances et compétences recherchées.

### Application par bloc

| Bloc | Application concrète |
|------|----------------------|
| **BC01** | Scraping/API Pôle Emploi, Data Lake avec données brutes + transformées, ETL PySpark pour le volume |
| **BC02** | Analyse lexicale, distribution des salaires/compétences, cartographie géographique, tendances sectorielles |
| **BC03** | Classification multi-label des compétences requises, prédiction de fourchette salariale, clustering de métiers |
| **BC04** | NLP avec transformers (CamemBERT/FlauBERT), extraction d'entités nommées, embeddings de texte |
| **BC05** | API de matching CV/offres, pipeline CI/CD GitLab, déploiement Kubernetes |
| **BC06** | Roadmap produit, gestion des risques, livrables, présentation aux RH |

### Sources de données

- [API Pôle Emploi](https://pole-emploi.io/data/api)
- [data.gouv.fr — ROME](https://www.data.gouv.fr/fr/datasets/repertoire-operationnel-des-metiers-et-des-emplois-rome/)
- [Common Crawl](https://commoncrawl.org/)

---

## Sujet 4 : Diagnostic médical assisté par IA (imagerie)

### Contexte

Classifier des images médicales pour fournir une aide au diagnostic aux professionnels de santé.

### Application par bloc

| Bloc | Application concrète |
|------|----------------------|
| **BC01** | Pipeline d'ingestion d'images DICOM, stockage objet (MinIO/S3), métadonnées dans PostgreSQL, versioning DVC |
| **BC02** | Analyse exploratoire des distributions de pathologies, statistiques sur cohortes, visualisation des biais |
| **BC03** | Features extraites (texture, forme) + modèles ML classiques comme baseline |
| **BC04** | CNN (ResNet, EfficientNet), transfer learning, Grad-CAM pour explicabilité, data augmentation |
| **BC05** | API d'inférence, optimisation ONNX, déploiement sécurisé, monitoring des performances |
| **BC06** | Éthique IA médicale, gestion projet réglementé, documentation pour certification |

### Sources de données

- [NIH Chest X-rays](https://www.kaggle.com/datasets/nih-chest-xrays/data)
- [ISIC Skin Cancer](https://www.isic-archive.com/)
- [COVID-19 Radiography](https://www.kaggle.com/datasets/tawsifurrahman/covid19-radiography-database)

---

## Sujet 5 : Plateforme d'analyse du sentiment sur les réseaux sociaux

### Contexte

Analyser l'opinion publique sur des sujets d'actualité en temps réel à partir de données issues des réseaux sociaux.

### Application par bloc

| Bloc | Application concrète |
|------|----------------------|
| **BC01** | Collecte multi-sources (Reddit API, Mastodon, RSS news), stockage Elasticsearch, pipeline temps réel |
| **BC02** | Analyse de fréquence, tendances temporelles, cartographie des communautés, statistiques d'engagement |
| **BC03** | Classification de sentiment supervisée, détection de topics (LDA), clustering d'utilisateurs |
| **BC04** | Transformers multilingues (XLM-RoBERTa), fine-tuning sur données françaises, analyse d'émotions |
| **BC05** | Dashboard temps réel Streamlit/Grafana, alertes automatiques, API REST |
| **BC06** | Gestion projet, considérations éthiques (vie privée), présentation insights business |

### Sources de données

- [Reddit API](https://www.reddit.com/dev/api/)
- [Mastodon API](https://docs.joinmastodon.org/api/)
- [Sentiment140](https://www.kaggle.com/datasets/kazanova/sentiment140)
- [French Sentiment Datasets (Hugging Face)](https://huggingface.co/datasets?language=fr&task_categories=text-classification)

---

## Sujet 6 : Optimisation énergétique des bâtiments

### Contexte

Prédire et optimiser la consommation énergétique des bâtiments pour réduire l'empreinte carbone et les coûts.

### Application par bloc

| Bloc | Application concrète |
|------|----------------------|
| **BC01** | Intégration données ENEDIS/RTE, météo, calendrier, architecture Data Warehouse temporel |
| **BC02** | Profils de consommation, saisonnalité, corrélations multi-facteurs, benchmarking |
| **BC03** | Prédiction de charge (régression), classification des profils consommateurs, détection d'anomalies |
| **BC04** | LSTM/GRU pour prévision séries temporelles, modèles attention pour pics de demande |
| **BC05** | Système de recommandation automatisé, API pour smart building, intégration IoT simulée |
| **BC06** | Business case RSE, gestion projet, ROI environnemental |

### Sources de données

- [data.gouv.fr — Consommation électrique](https://www.data.gouv.fr/fr/datasets/?q=consommation+%C3%A9lectrique)
- [ENEDIS Open Data](https://data.enedis.fr/)
- [RTE eCO2mix](https://www.rte-france.com/eco2mix)
- [ASHRAE Energy Prediction](https://www.kaggle.com/c/ashrae-energy-prediction)

---

## Portails de données publiques

| Source | URL | Type de données |
|--------|-----|-----------------|
| data.gouv.fr | https://www.data.gouv.fr | Données françaises officielles |
| Kaggle | https://www.kaggle.com/datasets | Datasets ML prêts à l'emploi |
| UCI ML Repository | https://archive.ics.uci.edu | Datasets académiques classiques |
| Hugging Face | https://huggingface.co/datasets | NLP, vision, audio |
| Google Dataset Search | https://datasetsearch.research.google.com | Méta-moteur |
| EU Open Data | https://data.europa.eu | Données européennes |
| World Bank | https://data.worldbank.org | Données économiques mondiales |

---

## Livrables attendus par bloc (rappel)

### BC01 — Infrastructure de données
- Schéma d'architecture technique
- Scripts ETL documentés
- Base de données opérationnelle

### BC02 — Analyse exploratoire
- Notebook d'analyse exploratoire
- Rapport statistique
- Visualisations commentées

### BC03 — Machine Learning
- Pipeline de preprocessing
- Modèles entraînés et évalués
- Rapport de performance comparative

### BC04 — Deep Learning
- Architecture du réseau de neurones
- Modèle entraîné
- Analyse des résultats et explicabilité

### BC05 — Industrialisation
- API fonctionnelle
- Conteneur Docker
- Documentation de déploiement
- Monitoring en place

### BC06 — Gestion de projet
- Planning et suivi de projet
- Documentation technique complète
- Présentation de soutenance
- Analyse des risques et ROI
