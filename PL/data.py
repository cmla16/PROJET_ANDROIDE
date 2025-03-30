import pandas as pd

def data(path1, path2, path3):
    #datasets
    df = pd.read_csv(path1)
    df2 = pd.read_csv(path2)
    df3 = pd.read_csv(path3)

    # etu: parcours
    parcours = {num: parcours for num, parcours in zip(df["num"], df["parcours"])}
    print("\n\nParcours des étudiants.\nparcours:\n", parcours)


    # etu, ue : rang
    # dictionnaire des préférences
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

    print("\n\nRand des des étudiants pour les ues.\nrang:\n", rang)


    # etu: ue_obligatoire
    ue_obligatoires = {
        row['num']: [ue for ue in [row['oblig1'], row['oblig2'], row['oblig3'], row['oblig4']] if pd.notna(ue)]
        for _, row in df.iterrows()
    }
    print("\n\nUE obligatoires pour chaque étudiants.\nue_obligatoires:\n", ue_obligatoires)

    ue_cons = {
        row['num']: [ue for i in range(1, 6) 
                    for ue in ([row[f'cons{i}']] if isinstance(row[f'cons{i}'], str) else [])]
        for _, row in df.iterrows()
    }
    print("\n\nUE cons pour chaque étudiants.\nue_cons:\n", ue_cons)


    # etu: preferences
    ue_preferences = {
        row['num']: [row[f'cons{i}'] for i in range(1, 6) if pd.notna(row[f'cons{i}'])] +
                    [row[f'equiv{i}'] for i in range(1, 6) if pd.notna(row[f'equiv{i}'])]
        for _, row in df.iterrows()
    }
    print("\n\nUE de préférences pour chaque étudiants.\nue_preferences:\n", ue_preferences)







    #---------------------- Ue de parcours -----------------------#

    # parcours: ue_de_parcours
    ue_parcours = {
        row["parcours"]: [ue for ue in row[1:].dropna().tolist()]
        for _, row in df3.iterrows()
    }
    print("\n\nUE de parcours pour chaque parcours.\nue_parcours:\n",ue_parcours)







    #---------------------- Planning/ capacité/ ects -----------------------#

    # ue: ects
    ects = {ue: ects for ue, ects in zip(df2["intitule"], df2["ects"])}
    print("\n\nECTS de chaque UE.\nects:\n", ects)

    # Initialisation de la liste d'incompatibilités
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

    print("\n\nincompatibilites_cm:\n", incompatibilites_cm)


    # Initialisation du dictionnaire des groupes TD
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

    # Afficher le résultat
    print("\n\ngroupes_td:\n", groupes_td)


    # Initialisation de la liste des incompatibilités TD
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

    # Affichage des incompatibilités trouvées
    print("\n\nincompatibilites_td:\n", incompatibilites_td)

    # liste pour stocker les incompatibilités cm/td
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

    # affichage des incompatibilités trouvées
    print("\n\nincompatibilites_cm_td:\n", incompatibilites_cm_td)

    # Initialisation du dictionnaire des capacités des TDs
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

    # Afficher le résultat
    print("\n\ncapacite_td:\n", capacite_td)

    return parcours, rang, ue_obligatoires, ue_cons, ue_preferences, ue_parcours, ects, incompatibilites_cm, groupes_td, incompatibilites_td, incompatibilites_cm_td, capacite_td


data("./../data/voeux2024_v5.csv", "./../data/EDT_M1S2_2024_v6_avec_ects.csv", "./../data/ues_parcours.csv")