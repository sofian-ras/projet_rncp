# BC06 — Gestion et pilotage du projet

**Objectif RNCP :** cadrer, planifier, documenter et fiabiliser un projet de science des données de
bout en bout — pas seulement écrire du code, mais aussi le rendre fiable, compréhensible et
transmissible.

Ce bloc est **autonome** : il fonctionne même si aucun des autres blocs n'a encore été exécuté (il
signale simplement quelles preuves manquent encore).

---

## Ce qui est implémenté

- Un **planning agile** sur 4 semaines, une itération par bloc de compétence.
- Une suite de **tests automatisés** (`tests/`, exécutée avec `pytest`) qui vérifie que le code fait
  bien ce qu'il est censé faire.
- Un **état des lieux automatisé** : pour chaque bloc, vérification que ses fichiers de preuve existent
  réellement sur disque.
- Une liste de **limites assumées**, plutôt que cachées — la marque d'une bonne gestion de projet.

## Où le voir dans le code

- `run.py`, fonction `executer_tests` (lance `pytest` en sous-processus et affiche le résultat).
- `run.py`, dictionnaire `PREUVES_PAR_BLOC` (mappe chaque bloc à ses fichiers de preuve attendus).
- `tests/test_acquisition.py`, `tests/conftest.py`.

## Démonstration

```bash
cd oiseaux_migrateurs_npdc
python blocs/bc06_gestion_projet/run.py
```

## Livrables produits

- Résultat des tests affiché en direct dans la console (6/6 tests passants).
- État des lieux des 5 autres blocs (preuves présentes ou manquantes).

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
