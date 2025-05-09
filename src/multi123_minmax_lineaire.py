from gurobipy import Model, GRB
import os
import sys

utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './utils'))
sys.path.append(utils_path)

mono_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './mono'))
sys.path.append(mono_path)

from data import data, attributions, stats
from mono1_nbEtu_voeux_insatisfaits import mono1_nbEtu_voeux_insatisfaits
from mono2_nbEtu_refus_parcours import mono2_nbEtu_refus_parcours
from mono3_nbEtu_sans_edt import mono3_nbEtu_sans_edt


#Variable globale pour stocker les groupes de TD/TME qui sont complets
groupes_complets=[]
compte_groupes_td_ue={}
opt = 0

def multi123_minmax_lineaire(path1, path2, path3, path4, path5, 
                            epsilon, lambda1, lambda2, lambda3,
                            relax_obj=None, mode=None, gap=0,
                            capacity=False,delta=0):

    global opt
    global groupes_complets
    global compte_groupes_td_ue

    parcours, rang, ue_obligatoires, ue_cons, ue_preferences, ue_parcours, ects, incompatibilites_cm, groupes_td, incompatibilites_td, incompatibilites_cm_td, capacite_td, nb_ue_hors_parcours, ue_incompatibles = data(path1, path2, path3, path4, path5)

    OPT1 = mono1_nbEtu_voeux_insatisfaits(path1, path2, path3, path4, path5,0.98)
    OPT2 = mono2_nbEtu_refus_parcours(path1, path2, path3, path4, path5,0.98)
    OPT3 = mono3_nbEtu_sans_edt(path1, path2, path3, path4, path5)

    # Modèle
    # Minimiser le nombre d'étudiant qui n'ont pas eu au moins un voeux
    model = Model("Attribution en Master")

    #------------------------------------- Variables de décision -------------------------------------#

    # Ajouter les variables pour les UE obligatoires et de préférences
    x = {(e, u): model.addVar(vtype=GRB.BINARY, name=f"x_{e}_{u}")
            for e in parcours for u in (ue_obligatoires[e] + ue_preferences[e])}

    y = {(e, u, g): model.addVar(vtype=GRB.BINARY, name=f"y_{e}_{u}_{g}")
            for e in parcours for u in (ue_obligatoires[e] + ue_preferences[e]) for g in groupes_td[u]}

    # variable pour linéariser
    z = model.addVar(vtype=GRB.INTEGER, name=f"z")

    # variable binaire : 1 si l'étudiant n'a pas eu au moins une ue de ses voeux, 0 sinon
    z1 = {e: model.addVar(vtype=GRB.BINARY, name=f"z1_{e}") for e in parcours}

    # = 1 si etu n'obtient pas au moins une ue de parcours dans ses premiers choix
    z2 = {e: model.addVar(vtype=GRB.BINARY, name=f"z2_{e}")
            for e in parcours}

    # nombre d'étudiant sans edt
    z3 = {e: model.addVar(vtype=GRB.BINARY, name=f"z3_{e}")
            for e in parcours}

    # nombre d'ects manquants pour avoir un contrat valide
    ec = {e: model.addVar(vtype=GRB.INTEGER, name=f"ec_{e}")
            for e in parcours}

    #------------------------------------- Fonction objectif -------------------------------------#

    e1 = (sum(z1[e] for e in parcours) - OPT1) / max(OPT1, 1)
    e2 = (sum(z2[e] for e in parcours) - OPT2) / max(OPT2, 1)
    e3 = (sum(z3[e] for e in parcours) - OPT3) / max(OPT3, 1)

    model.setObjective(z + epsilon * (lambda1 * e1 + lambda2 * e2 + lambda3 * e3), GRB.MINIMIZE)


    #------------------------------------- Contraintes -------------------------------------#

    # Linéariser
    model.addConstr(z >= lambda1 * e1, name=f"linéariser_z1")
    model.addConstr(z >= lambda2 * e2, name=f"linéariser_z2")
    model.addConstr(z >= lambda3 * e3, name=f"linéariser_z3")

    # Relacher 
    if relax_obj is not None:
        if mode == "relax" : 
            if relax_obj == "z1":
                model.addConstr(e1 <= opt - gap, name=f"relacher_z1")
            elif relax_obj == "z2":
                model.addConstr(e2 <= opt - gap, name=f"relacher_z2")
            elif relax_obj == "z3":
                model.addConstr(e3 <= opt - gap, name=f"relacher_z3")


    # contrainte pour définir z1_e
    for e in parcours:
        if ue_cons[e]:  # éviter les cas où ue_cons[e] est vide
            model.addConstr(z1[e] >= 1 - sum(x[e, u] for u in ue_cons[e]) / len(ue_cons[e]), name=f"z1_def_{e}")

    # Contrainte sur z2 
    for e in parcours:
        nb = 0
        first = []

        for u in (ue_obligatoires[e] + ue_preferences[e]):
            if nb == sum(ects[ue] for ue in (ue_obligatoires[e]+ue_cons[e])):
                break
            elif u in ue_parcours[parcours[e]]:
                first.append(u)
            nb = nb+ects[u]

        if len(first) > 0:
            model.addConstr(
            z2[e] >= 1 - (1 / len(first)) * sum(x[e, u] for u in first),name=f"nb_etu_parcours_refusée_{e}")

        else:
            model.addConstr(
                z2[e] == 0,
                name=f"nb_ue_parcours_refusée_{e}_empty"
            )

    # Contrainte: chaque étudiant doit avoir au plus 30 ECTS (parcours classique) (z3)
    for e in parcours:
        model.addConstr(sum(ects[u] * x[e, u] for u in (ue_obligatoires[e] + ue_preferences[e])) + ec[e] == sum(ects[ue] for ue in (ue_obligatoires[e] + ue_cons[e])) - (3 if parcours[e] == "IMA" else 0), name=f"ects_{e}")

    # Contarintes sur z3: 
    for e in parcours:
        model.addConstr(ec[e] <= 30 * z3[e], name=f"variable_d_ecart_e_{e}_<=_M_z3_{e}")

    # Contrainte: UEs obligatoires
    for e in parcours:
        for u in ue_obligatoires.get(e, []):
            model.addConstr(x[e, u] == 1, name=f"ue_obligatoire_{e}_{u}")

    # Contrainte: incompatibilités CM
    for e in parcours:
        for u1, u2 in incompatibilites_cm:
            if u1 in (ue_obligatoires[e] + ue_preferences[e]) and u2 in (ue_obligatoires[e] + ue_preferences[e]):
                model.addConstr(x[e, u1] + x[e, u2] <= 1, name=f"incompatibilite_cm_{e}_{u1}_{u2}")

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

    # Contrainte: un seul groupe de TD par UE suivie
    for e in parcours:
        for u in (ue_obligatoires[e] + ue_preferences[e]):
            if u in groupes_td:
                model.addConstr(sum(y[e, u, g] for g in groupes_td[u] if (e,u,g) in y) == x[e, u], name=f"td_choix_{e}_{u}")

    if capacity: #si TRUE on peut relacher la contrainte ---> augmenter de delta tous les groupes complets
        for (u, g), cap in capacite_td.items():

            if (u,g) in compte_groupes_td_ue and compte_groupes_td_ue[u,g]==cap: #Si le groupe est complet
                model.addConstr(sum(y[e, u, g] for e in parcours if u in (ue_obligatoires[e] + ue_preferences[e]) and (e,u,g) in y) <= cap+delta, name=f"capacite_td_plus_{u}_{g}")
            
            else:
                model.addConstr(sum(y[e, u, g] for e in parcours if u in (ue_obligatoires[e] + ue_preferences[e]) and (e,u,g) in y) <= cap, name=f"capacite_td_{u}_{g}")


    else: #si on ne relache pas la contrainte de capacité

        # Contrainte: capacité des groupes de TD
        for (u, g), cap in capacite_td.items():
            model.addConstr(sum(y[e, u, g] for e in parcours if u in (ue_obligatoires[e] + ue_preferences[e]) and (e,u,g) in y) <= cap, name=f"capacite_td_{u}_{g}")



    # Contraintes : UE hors parcours autorisée
    for e in parcours:
        if parcours[e] in nb_ue_hors_parcours:
            model.addConstr(
                    sum(x[e, u] for u in ue_preferences[e] if u not in ue_parcours[parcours[e]]) <= nb_ue_hors_parcours[parcours[e]],
                    name=f"ue_hors_parcours_{e}"
                )

    # Contraintes : UE incompatibles
    for e in parcours:
        for u1, u2 in ue_incompatibles:
            if u1 in (ue_obligatoires[e] + ue_preferences[e]) and u2 in (ue_obligatoires[e] + ue_preferences[e]):
                model.addConstr(x[e, u1] + x[e, u2] <= 1, name=f"incompatibilite_ue_{e}_{u1}_{u2}")


    # Résolution
    model.optimize()
    model.write("model_debug.lp")

    if model.status == GRB.INFEASIBLE:
        model.computeIIS()
        model.write("infeasible_model.ilp")
        print("modèle infaisable")
        return 


    # Affichage des résultats
    if model.status == GRB.OPTIMAL:
        if capacity:
            attributions("multi123_minmax_lineaire_capacity", x, y, parcours, ue_obligatoires, ue_preferences, groupes_td, multi_general=True)
            stats("multi123_minmax_lineaire_capacity", parcours, z1, z2, z3, multi_general=True)
        elif mode == "relax":
            attributions("multi123_minmax_lineaire_2", x, y, parcours, ue_obligatoires, ue_preferences, groupes_td, multi_general=True)
            stats("multi123_minmax_lineaire_2", parcours, z1, z2, z3, multi_general=True)
        else:
            attributions("multi123_minmax_lineaire", x, y, parcours, ue_obligatoires, ue_preferences, groupes_td, multi_general=True)
            stats("multi123_minmax_lineaire", parcours, z1, z2, z3, multi_general=True)

        if relax_obj is not None:
            if mode == "collect":
                if relax_obj == "z1":
                    opt = (sum(z1[e].x for e in parcours) - OPT1) / max(OPT1, 1)
                elif relax_obj == "z2":
                    opt = (sum(z2[e].x for e in parcours) - OPT2) / max(OPT2, 1)
                elif relax_obj == "z3":
                    opt = (sum(z3[e].X for e in parcours) - OPT3) / max(OPT3, 1)
        
        # Initialiser un dictionnaire pour compter le nombre d'étudiants par groupe de TD pour chaque UE
        #compte_groupes_td_ue = {(u, g): 0 for e in parcours for u in (ue_obligatoires[e] + ue_preferences[e]) if u in groupes_td for g in groupes_td[u]}
        if not capacity :
            # Comptabiliser les étudiants dans chaque groupe de TD pour chaque UE
            for e in parcours:
                for u in (ue_obligatoires[e] + ue_preferences[e]):
                    if u in groupes_td:
                        for g in groupes_td[u]:
                            if (e, u, g) in y and y[e, u, g].x > 0.5:  # Si l'étudiant e est dans le groupe g pour l'UE u
                                if (u,g) not in compte_groupes_td_ue:
                                    compte_groupes_td_ue[(u, g)] = 1
                                else:
                                    compte_groupes_td_ue[(u, g)] += 1

        print(sum(z1[e].x for e in parcours), sum(z2[e].x for e in parcours), sum(z3[e].x for e in parcours), z.x)

        return sum(z1[e].x for e in parcours), sum(z2[e].x for e in parcours), sum(z3[e].x for e in parcours)

if __name__ == "__main__":

    """
    #normal
    multi123_minmax_lineaire(
        "./../data/voeux2024_v4.csv",
        "./../data/EDT_M1S2_2024_v6_avec_ects.csv",
        "./../data/ues_parcours.csv",
        "./../data/nb_ue_hors_parcours.csv",
        "./../data/ue_incompatibles.csv",
        1e-6,
        50,
        100,
        500
    )
    """

    """
    # relachement n2
    multi123_minmax_lineaire(
        "./../data/voeux2024_v4.csv",
        "./../data/EDT_M1S2_2024_v6_avec_ects.csv",
        "./../data/ues_parcours.csv",
        "./../data/nb_ue_hors_parcours.csv",
        "./../data/ue_incompatibles.csv",
        1e-6,
        50,
        100,
        500,
        relax_obj="z1",
        mode="collect",
        gap=0
    )

    multi123_minmax_lineaire(
        "./../data/voeux2024_v4.csv",
        "./../data/EDT_M1S2_2024_v6_avec_ects.csv",
        "./../data/ues_parcours.csv",
        "./../data/nb_ue_hors_parcours.csv",
        "./../data/ue_incompatibles.csv",
        1e-6,
        50,
        100,
        500,
        relax_obj="z1",
        mode="relax",
        gap=0.05
    )
    """

    
    # relachement capacité
    multi123_minmax_lineaire(
        "./../data/voeux2024_v4.csv",
        "./../data/EDT_M1S2_2024_v6_avec_ects.csv",
        "./../data/ues_parcours.csv",
        "./../data/nb_ue_hors_parcours.csv",
        "./../data/ue_incompatibles.csv",
        1e-6,
        50,
        100,
        500,
        capacity = False,
        delta = 5
    )

    multi123_minmax_lineaire(
        "./../data/voeux2024_v4.csv",
        "./../data/EDT_M1S2_2024_v6_avec_ects.csv",
        "./../data/ues_parcours.csv",
        "./../data/nb_ue_hors_parcours.csv",
        "./../data/ue_incompatibles.csv",
        1e-6,
        50,
        100,
        500,
        capacity = True,
        delta = 5
    )
    