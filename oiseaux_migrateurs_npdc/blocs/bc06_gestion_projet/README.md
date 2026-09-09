# BC06 — Direction de projet

**Dépôt GitHub (tout le code du projet) :** https://github.com/sofian-ras/projet_rncp

**Objectif RNCP :** cadrer, dimensionner, planifier, documenter et fiabiliser un projet de science
des données de bout en bout — pas seulement écrire du code, mais aussi le rendre fiable,
compréhensible et transmissible.

Ce bloc **pilote** le projet : il exécute la suite de tests automatisés et rassemble le cadrage
(commanditaire, équipe, planning, budget, risques, ROI, gouvernance). Ses tests portent sur le
**vrai** module d'acquisition de BC01 (`blocs/bc01_infrastructure_donnees/acquisition.py`), rendu
importable par `tests/conftest.py`.

> **Convention.** Le projet a été réalisé **seul, en formation**. Le bloc « direction de projet »
> attendant un vrai dimensionnement, l'**équipe, le budget et le ROI sont une hypothèse** : *si ce
> POC était mené pour un commanditaire réel, voici ce qu'on proposerait.* Les chiffres (effectifs,
> TJM, gains) sont estimés et assumés comme tels. Le reste (problématique, planning, risques,
> RGPD) décrit le projet effectivement livré.

---

## Ce qui est implémenté

- Un **cadrage commanditaire** : parties prenantes, périmètre, besoin métier traduit en
  problématique data.
- Une **équipe projet** (3 profils + chef de projet à temps partiel) avec une **matrice RACI**
  par bloc.
- Un **planning agile** en 4 itérations (une par bloc technique), avec **jalons** J1/J2/J3,
  dépendances et mini-Gantt.
- Un **budget chiffré** : charge en jours-homme × TJM par profil + infra + contingence
  (~52 k€ projet), et un **ROI** (coût récurrent ~7,1 k€/an, bénéfice ~21,7 k€/an, retour ~3,5 ans)
  — calculs reproduits dans le notebook.
- L'**analyse des risques** (probabilité / impact / mitigation / statut) et la gouvernance des
  données (RGPD, traçabilité, reproductibilité), dans [`docs/gestion_projet.md`](docs/gestion_projet.md).
- Une suite de **tests automatisés** (`tests/`, exécutée avec `pytest`) qui vérifie le module
  d'acquisition de BC01 (bbox WKT, extraction des colonnes GBIF, cohérence de la config).
- Une liste de **limites assumées**, plutôt que cachées — la marque d'une bonne direction de projet.

## Où le voir dans le code

- `notebook_bc06.ipynb` : le pilotage déroulé **de haut en bas, façon cours** (problématique métier
  → data → commanditaire & parties prenantes → équipe & RACI → rétroplanning → **budget et ROI
  calculés en Python** → risques → tests exécutés en direct → documentation par bloc → RGPD).
  Version commentée de `docs/gestion_projet.md`, avec les tests réellement rejoués.
- `run.py` : `executer_tests` (lance `pytest` et affiche le résultat), `afficher_planning` et
  `afficher_equipe_et_budget` (rappellent le planning, l'équipe, le budget et le ROI en console).
- `tests/test_acquisition.py` : les tests eux-mêmes.
- `tests/conftest.py` : rend importables `commun` (racine) et `acquisition` (code de BC01).

## Démonstration

```bash
# venv activé (cf. README racine) ; ou notebook_bc06.ipynb pour la version expliquée
python blocs/bc06_gestion_projet/run.py
```

## Livrables produits

- Résultat des tests affiché en direct dans la console (6/6 tests passants).
- Planning, équipe, budget (~52 k€), ROI (~3,5 ans) et limites assumées affichés en console.
- Document de cadrage complet : [`docs/gestion_projet.md`](docs/gestion_projet.md).

## Statut

**Complet.** Les tests passent, la documentation par bloc existe (un `README.md` par dossier
`blocs/bc0X_.../`), et les limites sont explicitement formulées plutôt que passées sous silence.

## Limites globales du projet, assumées

- Le modèle de BC03, bien que le meilleur des trois testés, rate encore une majorité des présences
  réelles (fort déséquilibre des classes).
- Les données GBIF reflètent l'effort d'observation humain autant que la présence réelle des oiseaux
  (biais classique des données de science citoyenne).
- Le projet est validé sur une seule région ; sa capacité à se généraliser ailleurs n'a pas été testée.
- Le déploiement cloud (API/dashboard accessibles publiquement) est documenté mais non réalisé.

## Perspectives

- Rééquilibrer les classes (SMOTE, déjà dans les dépendances) pour améliorer la détection des présences.
- Intégrer des prévisions météo (et non plus seulement de la météo passée) pour une vraie anticipation.
- Étendre le nombre d'espèces et de régions couvertes.
- Réentraîner périodiquement le modèle à mesure que de nouvelles observations GBIF sont publiées.
