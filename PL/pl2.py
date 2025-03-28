from gurobipy import Model, GRB
from data import *

parcours, rang, ue_obligatoires, ue_cons, ue_preferences, ue_parcours, ects, incompatibilites_cm, groupes_td, incompatibilites_td, incompatibilites_cm_td, capacite_td = data("./../data/voeux2024_v4.csv", "./../data/EDT_M1S2_2024_v6_avec_ects.csv", "./../data/ues_parcours.csv")



# Modèle
model = Model("Attribution en Master")

#------------------------------------- Variables de décision -------------------------------------#

x = {}
# Ajouter les variables pour les UE obligatoires
x.update({(e, u): model.addVar(vtype=GRB.BINARY, name=f"x_{e}_{u}")
          for e, _ in ue_obligatoires.items() for u in ue_obligatoires[e]})
# Ajouter les variables pour les préférences des étudiants
x.update({(e, u): model.addVar(vtype=GRB.BINARY, name=f"x_{e}_{u}")
          for e, _ in ue_preferences.items() for u in ue_preferences[e]})

y = {}
y.update({(e, u, g): model.addVar(vtype=GRB.BINARY, name=f"y_{e}_{u}_{g}")
            for e, _ in ue_obligatoires.items() for u in ue_obligatoires[e] if u in groupes_td for g in groupes_td[u]})
y.update({(e, u, g): model.addVar(vtype=GRB.BINARY, name=f"y_{e}_{u}_{g}")
            for e, _ in ue_preferences.items() for u in ue_preferences[e] if u in groupes_td for g in groupes_td[u]})

z = {}
z.update({e: model.addVar(vtype=GRB.INTEGER, name=f"z_{e}")
            for e in parcours})


"""
model.update()  # Si nécessaire, forcer la mise à jour du modèle
for (e, u, g), var in y.items():
    print(var.VarName)"""

#------------------------------------- Fonction objectif -------------------------------------#

model.setObjective(sum(z[e] for e in parcours), GRB.MINIMIZE)


#------------------------------------- Contraintes -------------------------------------#

# Contrainte sur z 
for e in parcours:
    nb = 0
    first = []

    for u in (ue_obligatoires[e] + ue_preferences[e]):
        if nb == sum(ects[ue] for ue in (ue_obligatoires[e]+ue_cons[e])):
            break
        elif u in ue_parcours[parcours[e]]:
            first.append(u)
        nb = nb+ects[u]

    print(first)

    model.addConstr(z[e]==len(first)-sum(x[e,u] for u in first), name=f"nb_ue_parcours_refusée_{e}")
    

# Contrainte: chaque étudiant doit avoir au plus 30 ECTS
for e in parcours:
    model.addConstr(sum(ects[u] * x[e, u] for u in (ue_obligatoires[e] + ue_preferences[e])) == sum(ects[ue] for ue in (ue_obligatoires[e]+ue_cons[e])), name=f"ects_{e}")

# Contrainte: UEs obligatoires
for e in parcours:
    for u in ue_obligatoires.get(e, []):
        model.addConstr(x[e, u] == 1, name=f"ue_obligatoire_{e}_{u}")

# Contrainte: incompatibilités CM
for e in parcours:
    for u1, u2 in incompatibilites_cm:
        if u1 in (ue_obligatoires[e] + ue_preferences[e]) and u2 in (ue_obligatoires[e] + ue_preferences[e]):
            model.addConstr(x[e, u1] + x[e, u2] <= 1, name=f"incompatibilite_cm_{e}_{u1}_{u2}")

# Contrainte: un seul groupe de TD par UE suivie
for e in parcours:
    for u in (ue_obligatoires[e] + ue_preferences[e]):
        if u in groupes_td:
            model.addConstr(sum(y[e, u, g] for g in groupes_td[u] if (e,u,g) in y) == x[e, u], name=f"td_choix_{e}_{u}")

# Contrainte: incompatibilités TD
for e in parcours:
    for u1, g1, u2, g2 in incompatibilites_td:
        if u1 in (ue_obligatoires[e] + ue_preferences[e]) and u2 in (ue_obligatoires[e] + ue_preferences[e]):
            if (e,u1,g1) in y and (e,u2,g2) in y:
                model.addConstr(y[e, u1, g1] + y[e, u2, g2] <= 1, name=f"incompatibilite_td_{e}_{u1}_{g1}_{u2}_{g2}")

# Contrainte: incompatibilités TD/CM
for e in parcours:
    for u1, _, u2, g2 in incompatibilites_cm_td:
        if u1 in (ue_obligatoires[e] + ue_preferences[e]) and u2 in (ue_obligatoires[e] + ue_preferences[e]):
            if (e,u1) in x and (e,u2,g2) in y:
                model.addConstr(x[e, u1] + y[e, u2, g2] <= 1, name=f"incompatibilite_td_cm_{e}_{u1}_cm_{u2}_{g2}")

# Contrainte: capacité des groupes de TD
for (u, g), cap in capacite_td.items():
    model.addConstr(sum(y[e, u, g] for e in parcours if u in (ue_obligatoires[e] + ue_preferences[e]) and (e,u,g) in y) <= cap, name=f"capacite_td_{u}_{g}")


#Contraintes/ parcours
# contrainte : au plus une ue hors parcours pour les étudiants en ANDROIDE
for e in parcours:
    if parcours[e] == "ANDROIDE":
        model.addConstr(
            sum(x[e, u] for u in ue_preferences[e] if u not in ue_parcours["ANDROIDE"]) <= 1,
            name=f"ue_hors_parcours_{e}"
        )



# Résolution
model.optimize()
model.write("model_debug.lp")

if model.status == GRB.INFEASIBLE:
    model.computeIIS()
    model.write("infeasible_model.ilp") 


# Affichage des résultats
if model.status == GRB.OPTIMAL:
    for e in parcours:
        print(f"Emploi du temps de {e} ({parcours[e]}) :")
        for u in (ue_obligatoires[e] + ue_preferences[e]):
            if(e,u) in x :
                if x[e, u].x > 0.5:
                    print(f"  - {u} ({ects[u]} ECTS)")
                    for g in groupes_td.get(u, []):
                        if(e, u, g) in y : 
                            if y[e, u, g].x > 0.5:
                                print(f"    -> Groupe {g}")


# Initialiser un dictionnaire pour compter le nombre d'étudiants par groupe de TD pour chaque UE
compte_groupes_td_ue = {(u, g): 0 for e in parcours for u in (ue_obligatoires[e] + ue_preferences[e]) if u in groupes_td for g in groupes_td[u]}

# Comptabiliser les étudiants dans chaque groupe de TD pour chaque UE
for e in parcours:
    for u in (ue_obligatoires[e] + ue_preferences[e]):
        if u in groupes_td:
            for g in groupes_td[u]:
                if (e, u, g) in y and y[e, u, g].x > 0.5:  # Si l'étudiant e est dans le groupe g pour l'UE u
                    compte_groupes_td_ue[(u, g)] += 1

# Afficher le nombre d'étudiants dans chaque groupe de TD pour chaque UE
for (u, g), count in compte_groupes_td_ue.items():
    print(f"UE {u} - Groupe {g} : {count} étudiant(s)")