# BC06 — Cadrage, équipe, rétroplanning, risques et ROI

> **Convention.** Le projet a été réalisé **seul, dans un cadre de formation**. Ce document le
> cadre comme s'il était mené **pour un commanditaire réel** : l'équipe, le budget et le ROI sont
> une **hypothèse de dimensionnement**, avec des chiffres estimés et assumés comme tels (pas
> mesurés). Le reste (problématique, planning, risques, RGPD) décrit le projet effectivement livré.

## 1. Problématique métier traduite en problématique data

| Enjeu métier | Traduction data |
|---|---|
| Savoir *quand* les oiseaux migrateurs arrivent dans le Nord-Pas-de-Calais | Problème de **classification binaire** : présence / absence d'une espèce, par semaine et par maille géographique |
| Comprendre si la météo explique ces arrivées | **Analyse de corrélation** + **importance des variables** d'un modèle supervisé |
| Rendre la prévision utilisable par un non-technicien | **API** + **tableau de bord** exposant la probabilité de présence |

**Problématique scientifique retenue :** peut-on modéliser l'arrivée des migrations à partir de
variables climatiques et de la position géographique ?

## 2. Commanditaire et parties prenantes *(hypothèse)*

**Commanditaire supposé :** une **association régionale de protection des oiseaux** (type LPO
Hauts-de-France), en partenariat avec un Parc naturel régional. Elle anime un réseau d'une
quarantaine de bénévoles qui réalisent des **comptages de terrain** pendant les migrations.

**Besoin exprimé :** *« On a un nombre limité de sorties bénévoles ; on aimerait les concentrer
sur les semaines et les zones où la probabilité d'observer les espèces cibles est la plus forte. »*

| Partie prenante | Ce qu'elle attend | Implication |
|---|---|---|
| Direction de l'association (**sponsor**) | Outil fiable, coût maîtrisé, valorisable auprès des financeurs | Valide le budget et les jalons |
| Coordinateur des bénévoles | Une prévision **par semaine et par zone** pour planifier les sorties | Utilisateur principal du dashboard |
| Bénévoles observateurs (~40) | Un outil **simple**, non technique | Utilisateurs finaux ; fournissent le retour terrain |
| Prestataire / bénévole IT | Code **documenté et dockerisé**, reprenable | Maintenance après livraison |
| Référent RGPD de l'association | **Aucune donnée personnelle** traitée | Consulté au cadrage (cf. §8) |

**Périmètre.** Dans le périmètre : 4 espèces, région Nord-Pas-de-Calais, prévision hebdomadaire,
API + dashboard. Hors périmètre : application mobile, temps réel, autres régions, autres taxons.

## 3. Équipe projet et RACI *(hypothèse)*

Équipe **resserrée de 3 profils + un chef de projet à temps partiel**, sur **~6 semaines
calendaires** (le découpage fonctionnel reste en 4 itérations, cf. §4 — les 2 semaines
supplémentaires couvrent réunions, recette et aléas).

| Rôle | Mission | Blocs portés | Charge |
|---|---|---|---|
| Chef de projet / PO | Cadrage, backlog, comités, recette, soutenance | BC06 | 0,25 ETP |
| Data Engineer | Acquisition, ETL, stockage objet, Docker | BC01, BC05 | 1,0 ETP |
| Data Scientist | EDA, modèles ML, CNN images | BC02, BC03, BC04 | 1,0 ETP |
| Dev / MLOps | API, dashboard, tests automatisés, CI | BC05, BC06 | 0,5 ETP |

**Matrice RACI** — *R* réalise, *A* approuve (responsable), *C* consulté, *I* informé :

| Livrable | Chef de projet | Data Engineer | Data Scientist | Dev / MLOps | Sponsor |
|---|:--:|:--:|:--:|:--:|:--:|
| BC01 — infrastructure & ETL | A | R | C | I | I |
| BC02 — analyse exploratoire | A | C | R | I | I |
| BC03 — machine learning | A | I | R | C | I |
| BC04 — deep learning (images) | A | I | R | C | I |
| BC05 — API / dashboard / Docker | A | C | C | R | I |
| BC06 — pilotage, tests, doc | R / A | C | C | C | C |
| Recette & soutenance | R | C | C | C | A |

## 4. Rétroplanning (méthode agile, 4 itérations)

Planification **à rebours** depuis la soutenance. Dates données pour la session de septembre 2026,
à adapter pour une autre session.

| Itération | Dates | Bloc(s) | Livrable vérifiable | Dépend de |
|---|---|---|---|---|
| S1 | 11–15 août 2026 | BC01 | Acquisition GBIF + Open-Meteo, ETL, grille présence/absence | — |
| S2 | 18–22 août 2026 | BC02 | Saisonnalité, distributions univariées, corrélations, test χ² | BC01 |
| S3 | 25–29 août 2026 | BC03 + BC04 | 3 modèles ML comparés + validation croisée + segmentation ; CNN transfer learning (Grad-CAM) | BC01 |
| S4 | 1–5 sept. 2026 | BC05 + BC06 | API FastAPI, dashboard Streamlit, Docker ; tests, documentation, cette note | BC03 (+ BC04) |
| Soutenance | semaine du 8 sept. 2026 | — | Support oral (10 min) + démo live | tous |

**Jalons :**
- **J1** (fin S1) : `grille_presence_hebdo.parquet` produite → feu vert pour BC02/BC03.
- **J2** (fin S3) : modèle de production figé (`pipeline_ml.pkl`) → feu vert pour BC05.
- **J3** (mi-S4) : API + dashboard fonctionnels en local → répétition de la démo.

**Mini-Gantt** (■ = travail principal, · = appoint) :

```
                 S1     S2     S3     S4
BC01 infra      ■■■■   ·      ·      ·
BC02 EDA         ·     ■■■■   ·      ·
BC03 ML          ·      ·     ■■■■   ·
BC04 CNN         ·      ·     ■■     ·
BC05 API/Docker  ·      ·      ·     ■■■■
BC06 pilotage   ····   ····   ····   ■■■■
jalons                 J1            J2   J3
```

**Marge :** une demi-journée tampon par itération (imprévus API, ré-entraînements). Les parquets de
`donnees/traitees/` et le modèle de production sont versionnés dans le dépôt : un retard sur BC01
ne bloque pas le travail sur les blocs suivants, qui partent de la dernière version figée.

## 5. Analyse des risques

| Risque | Prob. | Impact | Mitigation | Statut |
|---|---|---|---|---|
| API GBIF indisponible (5xx transitoires) | Élevée | Moyen | `get_avec_retry` (backoff exponentiel) + `donnees/traitees/` versionnées dans le dépôt | **Traité** |
| Fort déséquilibre des classes (~97,7 % d'absences) | Certaine | Élevé | Métriques adaptées (F1, AUC-ROC, matrice de confusion) plutôt que l'accuracy ; période bornée à 2019-2024 pour ne pas ajouter d'absences fictives ; SMOTE identifié comme prochaine itération | **Traité (partiel)** |
| Sur-apprentissage du modèle retenu | Moyenne | Moyen | Validation croisée stratifiée 5-fold + écart train/test contrôlé (< 0,05) | **Traité** |
| Météo passée seule, peu prédictive de la présence | Moyenne | Moyen | Limite assumée et documentée ; piste : intégrer des prévisions météo | **Accepté** |
| Biais d'effort d'observation dans les données GBIF | Certaine | Moyen | Signalé explicitement (science citoyenne) ; interprétation prudente des résultats | **Accepté** |
| Déploiement cloud non réalisé (pas d'URL publique) | Certaine | Moyen | Fichiers de déploiement prêts (`Procfile`, `render.yaml`) + procédure documentée dans BC05 | **Ouvert** |
| Indisponibilité d'un profil clé (Data Scientist) | Faible | Élevé | Code + notebooks pédagogiques par bloc ; artefacts figés et versionnés → reprise possible par un autre profil | **Traité** |
| Incompatibilité de versions au `pip install` (numpy/pandas/mlflow/xgboost) | Faible | Faible | `requirements.txt` épinglé ; suivi MLflow optionnel (dégradation propre si absent) ; validation croisée BC03 réécrite en boucle explicite pour rester insensible aux versions de scikit-learn/xgboost | **Traité** |

## 6. Charge et budget *(hypothèse)*

**Méthode.** Pour chaque rôle : `charge (jours-homme) = ETP × durée (30 jours ouvrés)`, puis
`coût = charge × TJM`. Les TJM sont des ordres de grandeur **prestation, profils junior /
confirmé**. Ces calculs sont reproduits dans `notebook_bc06.ipynb` (cellule `budget`).

| Rôle | Charge (j-h) | TJM | Coût |
|---|--:|--:|--:|
| Chef de projet | 7,5 | 650 € | 4 875 € |
| Data Engineer | 30 | 550 € | 16 500 € |
| Data Scientist | 30 | 600 € | 18 000 € |
| Dev / MLOps | 15 | 500 € | 7 500 € |
| **Total RH** | **82,5** | | **46 875 €** |

| Poste | Montant |
|---|--:|
| Coût RH | 46 875 € |
| Infra phase projet (GPU cloud ponctuel pour le CNN, hébergement de test) | ~100 € |
| Contingence (10 %) | ~4 688 € |
| **Budget projet** | **~52 000 €** |

Répartition indicative de la charge par bloc : BC01 ~22 j-h, BC02 ~10 j-h, BC03 ~18 j-h,
BC04 ~13 j-h, BC05 ~13 j-h, BC06 / pilotage transverse ~7 j-h.

## 7. Coûts récurrents et ROI *(hypothèse)*

**Coût récurrent** après mise en production :

- Hébergement API + dashboard, stockage objet + base, domaine/TLS : **~40 €/mois** (~480 €/an).
- Maintenance corrective et ré-entraînement : **~1 jour-homme/mois** (Dev / MLOps à 550 €) →
  ~6 600 €/an.
- **Total : ~7 100 €/an.**

**Bénéfice attendu**, exprimé en temps bénévole **mieux employé** (et non « économisé ») :
l'outil évite des sorties de comptage à faible probabilité et redirige cet effort vers des zones
utiles.

- 40 bénévoles × 1,5 sortie redirigée/mois × 6 mois de migration × 3 h × 15 €/h (barème du
  bénévolat) = **~16 200 €/an** de temps redéployé.
- Temps de coordination aujourd'hui manuel, en partie automatisé : ~0,1 ETP × 220 j × 250 €/j =
  **~5 500 €/an**.
- **Bénéfice total : ~21 700 €/an.**

**Gain net : ~14 600 €/an.** Retour sur investissement (budget / gain net) : **~3,5 ans**.

**Lecture.** Le retour purement financier se compte en quelques années : pour une association,
l'investissement se justifie **autant par les bénéfices qualitatifs** — données naturalistes plus
exploitables, meilleure couverture des zones à enjeu, fidélisation des bénévoles (moins de sorties
infructueuses) — que par le gain chiffré. Conclusion assumée, pas maquillée.

**Autres bénéfices non chiffrés.** Réutilisabilité : la chaîne (acquisition → ETL → grille →
modèle → API) est générique ; changer d'espèces ou de région ne demande que d'ajuster
`commun/config.py`.

## 8. Gouvernance des données et RGPD

- **RGPD** : le projet ne traite **aucune donnée à caractère personnel** (occurrences d'espèces,
  mesures météo). Détail des sources, licences et minimisation dans le document d'architecture de
  BC01 (`bc01_infrastructure_donnees/docs/architecture.md`).
- **Traçabilité** : les URL des API sources sont dans le code (`acquisition.py`) ; les jeux de
  données intermédiaires (`donnees/traitees/`) et le modèle de production (`modeles/pipeline_ml.pkl`)
  sont figés et versionnés à la racine du projet.
- **Reproductibilité** : graines aléatoires fixées (`RANDOM_STATE`), hyperparamètres dans
  `commun/config.py`, suivi des entraînements dans MLflow (`mlruns/` à la racine).
