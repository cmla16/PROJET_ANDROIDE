import pandas as pd
import csv
from collections import defaultdict
import os

def data(path1, path2, path3, path4, path5, verbose=False):
    # datasets
    df = pd.read_csv(path1)
    df2 = pd.read_csv(path2)
    df3 = pd.read_csv(path3)
    df4 = pd.read_csv(path4)
    df5 = pd.read_csv(path5)

    # fonction d'affichage verbose
    def log(msg):
        if verbose:
            print(f"{msg}")

    #----------------------------------------- Données étudiant -------------------------------------------------#

    #------------------------------------------------------------------------------------------------------------#
    # dictionnaire étudiant : son parcours
    # etu: parcours
    parcours = {num: parcours for num, parcours in zip(df["num"], df["parcours"])}
    log("\n\nparcours:\n")
    log(parcours)


    #------------------------------------------------------------------------------------------------------------#
    # dictionnaire des préférences des étudiants
    # etu, ue : rang
    cons_columns = ["cons1", "cons2", "cons3", "cons4", "cons5", "equiv1", "equiv2", "equiv3", "equiv4", "equiv5"]
    rang = {}

    # boucle sur chaque ligne (chaque étudiant)
    for _, row in df.iterrows():
        student_id = row['num']  # format étudiant "E1", "E2", ...
        
        # récupérer les UEs choisies dans l'ordre
        ue_choices = [row[col] for col in cons_columns if pd.notna(row[col]) and row[col] != ""]
        
        # ajouter au dictionnaire avec le rang correspondant
        for rank, ue in enumerate(ue_choices, start=1):
            rang[(student_id, ue)] = rank
    log("\n\nrang:\n")
    log(rang)


    #------------------------------------------------------------------------------------------------------------#
    # dictionnaire des ue obligatoire pour chaque étudiant
    # etu: ue_obligatoire
    ue_obligatoires = {
        row['num']: [ue for ue in [row['oblig1'], row['oblig2'], row['oblig3'], row['oblig4']] if pd.notna(ue)]
        for _, row in df.iterrows()
    }
    log("\n\nue_obligatoires:\n")
    log(ue_obligatoires)


    #------------------------------------------------------------------------------------------------------------#
    # dictionnaire des premiers choixe pour chaque étudiant
    # etu: ue_cons
    ue_cons = {
        row['num']: [ue for i in range(1, 6) 
                    for ue in ([row[f'cons{i}']] if isinstance(row[f'cons{i}'], str) else [])]
        for _, row in df.iterrows()
    }
    log("\n\nue_cons:\n")
    log(ue_cons)


    #------------------------------------------------------------------------------------------------------------#
    # dictionnaire des premiers et dernier voeux
    # etu: preferences
    ue_preferences = {
        row['num']: [row[f'cons{i}'] for i in range(1, 6) if pd.notna(row[f'cons{i}'])] +
                    [row[f'equiv{i}'] for i in range(1, 6) if pd.notna(row[f'equiv{i}'])]
        for _, row in df.iterrows()
    }
    log("\n\nue_preferences:\n")
    log(ue_preferences)

    #------------------------------------- Données parcours -----------------------------------------------------#

    #------------------------------------------------------------------------------------------------------------#
    # dictionnaire des ue de parcours
    # parcours: ue_de_parcours
    ue_parcours = {
        row["parcours"]: [ue for ue in row[1:].dropna().tolist()]
        for _, row in df3.iterrows()
    }
    log("\n\nue_parcours:\n")
    log(ue_parcours)


    #------------------------------------------------------------------------------------------------------------#
    # dictionnaire des ects pour chaque ue
    # ue: ects
    ects = {ue: ects for ue, ects in zip(df2["intitule"], df2["ects"])}
    log("\n\nects:\n")
    log(ects)


    #------------------------------------------------------------------------------------------------------------#
    # dictionnaire d'incompatibilité entre CM
    # [(CM1, CM2),...]
    incompatibilites_cm = []

    # Parcours des UEs dans df2
    for i, row_i in df2.iterrows():
        for j, row_j in df2.iterrows():
            # Si i et j sont différents (éviter les comparaisons d'une UE avec elle-même)
            if i < j:
                # Récupérer les cours de chaque UE
                ue_i = row_i["intitule"]
                ue_j = row_j["intitule"]
                cours_i = {row_i["cours1"], row_i["cours2"]}
                cours_j = {row_j["cours1"], row_j["cours2"]}
                
                if 0 not in cours_i and 0 not in cours_j:
                    # Si les cours sont les mêmes, c'est une incompatibilité
                    if not cours_i.isdisjoint(cours_j):  # les sets ont au moins un cours en commun
                        incompatibilites_cm.append((ue_i, ue_j))
    log("\n\nincompatibilites_cm:\n")
    log(incompatibilites_cm)

    #------------------------------------------------------------------------------------------------------------#
    # dictionnaire des ue incompatibles (ex: ml, mll)
    # [(ml, mll),...]
    ue_incompatibles = [
        (row['ue1'], row['ue2'])
        for _, row in df5.iterrows()
    ]
    log("\n\nue_incompatibles:\n")
    log(ue_incompatibles)

    #------------------------------------------------------------------------------------------------------------#
    # dictionnaire de tous les groupes de td par ue
    # [ue: [td1, td2],...]
    groupes_td = {}

    # Parcours des lignes dans df2 pour remplir le dictionnaire
    for _, row in df2.iterrows():
        ue = row["intitule"]  # Nom de l'UE
        
        # Liste pour les TDs associés à cette UE
        td_list = []
        
        # Vérification des TDs de td1 à td5
        for td_num in range(1, 6):  # td1, td2, td3, td4, td5
            td_col = f"td{td_num}"
            if pd.notna(row[td_col]) and row[td_col] != "":  # Si le TD n'est pas vide
                td_list.append(td_col)  # Ajouter le TD à la liste
        
        # Ajouter l'UE et ses TDs au dictionnaire
        groupes_td[ue] = td_list
    log("\n\ngroupes_td:\n")
    log(groupes_td)


    #------------------------------------------------------------------------------------------------------------#
    # dictionnaire incompatibilité entre TD/TME
    # [(ue1,td1,ue2,td1),...]
    incompatibilites_td = []

    # Parcours des UEs pour comparer chaque UE avec toutes les autres
    for i, row_i in df2.iterrows():
        ue_i = row_i["intitule"]
        td_i_list = [row_i[f"td{num}"] for num in range(1, 6) if pd.notna(row_i[f"td{num}"])]
        
        if 0 not in td_i_list:
            for j, row_j in df2.iterrows():
                if i < j:  # éviter les doublons
                    ue_j = row_j["intitule"]
                    td_j_list = [row_j[f"td{num}"] for num in range(1, 6) if pd.notna(row_j[f"td{num}"])]
                    tme_j_list = [row_j[f"tme{num}"] for num in range(1, 6) if pd.notna(row_j[f"tme{num}"])]
                    
                    for td_i_num in range(1, 6):
                        td_i_value = row_i.get(f"td{td_i_num}", None)
                        if pd.notna(td_i_value) and td_i_value in td_j_list + tme_j_list:
                            td_j_num = next((num for num in range(1, 6) if row_j.get(f"td{num}", None) == td_i_value), None)
                            if td_j_num:
                                incompatibilites_td.append((ue_i, f"td{td_i_num}", ue_j, f"td{td_j_num}"))
    log("\n\nincompatibilites_td:\n")
    log(incompatibilites_td)


    #------------------------------------------------------------------------------------------------------------#
    # dictionnaire incompatibilité entre CM/TD/TME
    # [(ue1,CM,ue2,td1),...]
    incompatibilites_cm_td = []

    # parcourir les ues pour comparer chaque ue avec toutes les autres
    for i, row_i in df2.iterrows():
        ue_i = row_i["intitule"]
        cm_i_list = [row_i[f"cours{num}"] for num in range(1, 3) if pd.notna(row_i[f"cours{num}"])]

        if 0 not in cm_i_list:
            for j, row_j in df2.iterrows():
                if i != j:  # éviter les comparaisons d'une ue avec elle-même
                    ue_j = row_j["intitule"]
                    
                    # vérifier chaque cm contre les td/tme
                    for cm in cm_i_list:
                        for td_num in range(1, 6):  # on boucle sur les td et tme
                            td_value = row_j.get(f"td{td_num}", None)
                            tme_value = row_j.get(f"tme{td_num}", None)

                            if pd.notna(td_value) and cm == td_value:
                                incompatibilites_cm_td.append((ue_i, "cm", ue_j, f"td{td_num}"))

                            if pd.notna(tme_value) and cm == tme_value:
                                incompatibilites_cm_td.append((ue_i, "cm", ue_j, f"tme{td_num}"))
    log("\n\nincompatibilites_cm_td:\n")
    log(incompatibilites_cm_td)


    #------------------------------------------------------------------------------------------------------------#
    # dictionnaire capacité des td pour chaque ue
    # (ue, td) : cap
    capacite_td = {}

    # Parcours des lignes dans df2 pour remplir le dictionnaire
    for _, row in df2.iterrows():
        ue = row["intitule"]  # Nom de l'UE
        
        # Parcours des capacités pour chaque TD (capac1 à capac5)
        for td_num in range(1, 6):  # capac1, capac2, capac3, capac4, capac5
            capac_col = f"capac{td_num}"  # Le nom de la colonne de capacité
            td_name = f"td{td_num}"  # Le nom du TD
            
            capacite = row[capac_col]
            
            # Vérifier si la capacité est non vide (on ne veut pas ajouter des entrées vides)
            if pd.notna(capacite) and capacite != "":
                capacite_td[(ue, td_name)] = capacite  # Ajouter au dictionnaire
    log("\n\ncapacite_td:\n")
    log(capacite_td)

    #------------------------------------------------------------------------------------------------------------#
    # dictionnaire nombre d'ue hors parcour autorisé
    # parcours : nb
    nb_ue_hors_parcours = {
        row['parcours']: row['nb_ue_hors_parcours']
        for _, row in df4.dropna(subset=['nb_ue_hors_parcours']).iterrows()
    }
    log(nb_ue_hors_parcours)

    return parcours, rang, ue_obligatoires, ue_cons, ue_preferences, ue_parcours, ects, incompatibilites_cm, groupes_td, incompatibilites_td, incompatibilites_cm_td, capacite_td, nb_ue_hors_parcours, ue_incompatibles


def attributions(nom, x, y, parcours, ue_obligatoires, ue_preferences, groupes_td):
    output_dir = f"../../output/attributions/{nom}"
    os.makedirs(output_dir, exist_ok=True)

    lignes_parcours = defaultdict(list)

    for i, e in enumerate(parcours, start=1):
        ues_attribuees = []
        choix_retenus = []

        place = 0
        for u in (ue_obligatoires[e] + ue_preferences[e]):
            place += 1
            if (e, u) in x and x[e, u].x > 0.5:
                groupe = ""
                for g in groupes_td.get(u, []):
                    if (e, u, g) in y and y[e, u, g].x > 0.5:
                        groupe = str(g)
                        break
                ue_avec_groupe = u + "_" + groupe
                ues_attribuees.append(ue_avec_groupe)

                choix_retenus.append(str(place))

        while len(ues_attribuees) < 8:
            ues_attribuees.append("")

        ligne = [parcours[e], i, " ".join(choix_retenus)] + ues_attribuees
        lignes_parcours[parcours[e]].append(ligne)

    for p, lignes in lignes_parcours.items():
        with open(os.path.join(output_dir, f"{p}_{nom}.csv"), "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["parcours", "num", "choix retenus", "UE1", "UE2", "UE3", "UE4", "UE5", "UE6", "UE7", "UE8"])
            for ligne in lignes:
                writer.writerow(ligne)

def stats(nom, parcours, z1, z2, z3):
    output_dir = f"../../output/statistiques"
    os.makedirs(output_dir, exist_ok=True)

    stats = defaultdict(lambda: {"z1": 0, "z2": 0, "z3": 0})

    for e in parcours:
        p = parcours[e]
        if z1!= None and z1[e].x > 0.5:
            stats[p]["z1"] += 1
        elif z1 == None:
            stats[p]["z1"] = 'NaN'
        if z2!= None and z2[e].x > 0.5:
            stats[p]["z2"] += 1
        elif z2 == None:
            stats[p]["z2"] = 'NaN'
        if z3!= None and z3[e].x > 0.5:
            stats[p]["z3"] += 1
        elif z3 == None:
            stats[p]["z3"] = 'NaN'

    with open(os.path.join(output_dir, f"{nom}.csv"), "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["parcours", "étudiant qui n'ont pas eu au moins un voeux", "ue du parcours refusé", "étudiant sans edt"])
        for p in stats:
            writer.writerow([p, stats[p]["z1"], stats[p]["z2"], stats[p]["z3"]])


if __name__ == "__main__":
    data(
        "./../data/voeux2024_v4.csv",
        "./../data/EDT_M1S2_2024_v6_avec_ects.csv",
        "./../data/ues_parcours.csv",
        "./../data/nb_ue_hors_parcours.csv",
        "./../data/ue_incompatibles.csv",
        verbose=True
    )