# Attribution multicritère d’UE en Master

## Contributeurs
- Camélia Bouali  
- Jules Mazlum  

## Description
Projet académique réalisé dans le cadre du **Master 1 ANDROIDE – Sorbonne Université**.

Ce projet propose une approche d’**optimisation multi-objectif** pour l’attribution des unités
d’enseignement (UE) et la génération d’emplois du temps en master, en prenant en compte
simultanément :
- les préférences des étudiants,
- les contraintes académiques (ECTS, parcours, incompatibilités horaires),
- les capacités des groupes de TD/TME.

## Approche
- Modélisation du problème en **programmation linéaire**
- Optimisation **multi-objectif**
- Agrégation des critères via une **fonction de Tchebycheff pondérée augmentée**
- Résolution à l’aide du solveur **Gurobi**

## Objectifs optimisés
1. Minimiser le nombre d’étudiants n’obtenant pas leur emploi du temps préféré  
2. Minimiser le nombre d’étudiants n’obtenant pas les UE de leur parcours  
3. Minimiser le nombre d’étudiants sans emploi du temps valide  

## Outils & technologies
- Python  
- Gurobi  
- Recherche opérationnelle  
- Optimisation combinatoire  
- Programmation linéaire multi-objectif  

## Résultats
- Exploration de compromis entre objectifs (solutions non dominées / front de Pareto)
- Étude de l’impact des pondérations des objectifs
- Analyse du relâchement des contraintes de capacité

## Exécution
```bash
cd src
python multi123_minmax_lineaire.py
