# Attribution Multicritère d'UE en Master

## Contributeurs
- Camélia Bouali  
- Jules Mazlum  

## Description
Ce projet vise à développer un algorithme d'optimisation multicritère pour l'attribution des emplois du temps des étudiants en master. L'objectif est de concilier les préférences des étudiants, les contraintes académiques et les ressources disponibles.

## Objectifs
- Minimiser le nombre d'étudiants sans emploi du temps valide.
- Minimiser le nombre d'étudiants n'obtenant pas les UE de leur parcours.
- Maximiser la satisfaction des choix des étudiants.

## Outils
- **Solveur** : Gurobi  
- **Langage** : Python  
- **Données** : Documents contenant les choix étudiants, les UE et les spécificités des parcours  

## Étapes du projet
1. Prétraitement et extraction des données.  
2. Modélisation du problème sous forme de programme linéaire.  
3. Résolution avec Gurobi et analyse des solutions.  
4. *(Optionnel)* Interface de visualisation des résultats.  
