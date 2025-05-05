from gurobipy import Model, GRB
from data import data

def multi12_lineaire(path1, path2, path3, path4, path5, w1, w2,coverage):

    parcours, rang, ue_obligatoires, ue_cons, ue_preferences, ue_parcours, ects, incompatibilites_cm, groupes_td, incompatibilites_td, incompatibilites_cm_td, capacite_td, nb_ue_hors_parcours, ue_incompatibles = data(path1, path2, path3, path4, path5)

    # Modèle
    # Minimiser le nombre d'étudiant qui n'ont pas eu au moins un voeux
    model = Model("Attribution en Master")

    #------------------------------------- Variables de décision -------------------------------------#

    # Ajouter les variables pour les UE obligatoires et de préférences
    x = {(e, u): model.addVar(vtype=GRB.BINARY, name=f"x_{e}_{u}")
            for e in parcours for u in (ue_obligatoires[e] + ue_preferences[e])}

    y = {(e, u, g): model.addVar(vtype=GRB.BINARY, name=f"y_{e}_{u}_{g}")
            for e in parcours for u in (ue_obligatoires[e] + ue_preferences[e]) for g in groupes_td[u]}

    # variable binaire : 1 si l'étudiant n'a pas eu au moins une ue de ses voeux, 0 sinon
    z1 = {e: model.addVar(vtype=GRB.BINARY, name=f"z1_{e}") for e in parcours}

    # = 1 si etu n'obtient pas au moins une ue de parcours dans ses premiers choix
    z2 = {e: model.addVar(vtype=GRB.BINARY, name=f"z2_{e}")
            for e in parcours}

    respecte_ects = {e: model.addVar(vtype=GRB.BINARY, name=f"respecte_ects_{e}") for e in parcours}

    """
    model.update()  # Si nécessaire, forcer la mise à jour du modèle
    for (e, u, g), var in y.items():
        print(var.VarName)"""

    #------------------------------------- Fonction objectif -------------------------------------#

    model.setObjective(
        w1 * sum(z1[e] for e in parcours) +
        w2 * sum(z2[e] for e in parcours),
        GRB.MINIMIZE
    )


    #------------------------------------- Contraintes -------------------------------------#


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

    """#Contrainte strict (infaisable dans le cas z1  vs z2)
    for e in parcours:
        model.addConstr(sum(ects[u] * x[e, u] for u in (ue_obligatoires[e] + ue_preferences[e])) == sum(ects[ue] for ue in (ue_obligatoires[e] + ue_cons[e])) - (3 if parcours[e] == "IMA" else 0), name=f"ects_{e}")

    """

    
    
    #Contrainte relachée à coverage x 100 % d'étudiants
    nb_etudiants = len(parcours)
    M = 100  # assez grand pour désactiver la contrainte

    for e in parcours:
        total_ects = sum(ects[u] * x[e, u] for u in (ue_obligatoires[e] + ue_preferences[e]))
        target_ects = sum(ects[ue] for ue in (ue_obligatoires[e] + ue_cons[e])) - (3 if parcours[e] == "IMA" else 0)

        # Formulation d'une contrainte relâchable avec big-M
        model.addConstr(target_ects - total_ects <= (1-respecte_ects[e]) * M, name=f"ects_sup_{e}")
        model.addConstr(target_ects - total_ects >= (1-respecte_ects[e]) * -M, name=f"ects_sup_{e}")
        model.addConstr(target_ects - total_ects >= 0.01 - respecte_ects[e], name=f"ects_sup_{e}")
        #model.addConstr(total_ects - target_ects >= respecte_ects[e] * M, name=f"ects_inf_{e}")

    # Contrainte globale : au moins 90 % des étudiants doivent respecter l'égalité
    model.addConstr(sum(respecte_ects[e] for e in parcours) >= coverage * nb_etudiants, name="min_90_percent_ects")




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
        print("Modèle infaisable !!!")
        return


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


        """
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
        """
        
        #Affiche le nombre d'étudiant qui n'ont pas eu au moins un voeux
        nb_etu = 0
        for e in parcours:
            if z1[e].x > 0.5:
                nb_etu += 1
                print(f"L'étudiant {e} n'a pas eu au moins une UE dans ses premiers choix.")
        
        print(f"Valeur de la fonction objectif 1 : {nb_etu}")

        #Affiche nb ue du parcours refusé 
        count_etu=0

        for e in parcours:
            if z2[e].x>0.5:
                count_etu+=1
                print(f"L'étudiant {e} n'a pas eu au moins une ue de parcours dans ses premiers voeux")

        print(f"Valeur de la fonction objectif 2 : {count_etu}")

        nb_z1 = sum(1 for e in parcours if z1[e].x > 0.5)
        nb_z2 = sum(1 for e in parcours if z2[e].x > 0.5)

    

        return nb_z1, nb_z2

if __name__ == "__main__":
    multi12_lineaire(
        "./../data/voeux2024_v4.csv",
        "./../data/EDT_M1S2_2024_v6_avec_ects.csv",
        "./../data/ues_parcours.csv",
        "./../data/nb_ue_hors_parcours.csv",
        "./../data/ue_incompatibles.csv",
        100,
        50,
        0.98
    )