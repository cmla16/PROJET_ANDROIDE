import matplotlib.pyplot as plt
from multi23_lineaire import multi23_lineaire
from multi13_lineaire import multi13_lineaire
from multi12_lineaire import multi12_lineaire

"""w2_list = [1, 10, 50, 100, 300, 500, 800, 1000]
w3_list = [1000, 800, 500, 300, 100, 50, 10, 1]

solutions = []

for w2 in w2_list:
    for w3 in w3_list:
        print(f"résolution avec w2={w2}, w3={w3}")
        nb_z2, nb_z3 = multi13_lineaire(
            "./../data/voeux2024_v4.csv",
            "./../data/EDT_M1S2_2024_v6_avec_ects.csv",
            "./../data/ues_parcours.csv",
            "./../data/nb_ue_hors_parcours.csv",
            "./../data/ue_incompatibles.csv",
            w2,
            w3
        )
        solutions.append((nb_z2, nb_z3))


# plot 2D
x_vals = [s[0] for s in solutions]
y_vals = [s[1] for s in solutions]

plt.figure(figsize=(8,6))
plt.scatter(x_vals, y_vals, color='dodgerblue', label='solutions')
plt.xlabel("nb étudiants sans voeux parcours (z2)")
plt.ylabel("nb étudiants sans contrat valide (z3)")
plt.title("Front de Pareto - Affectation des UE")
plt.grid(True)
plt.legend()
plt.show()"""

"===================MON CODE======================"

# Liste de poids à tester (tu peux raffiner)
weight_sets = [
    (1.0,0.0,0.0),
    (0.0,1.0,0.0),
    (0.0,0.0,1.0),
    (0.6, 0.3, 0.1),
    (0.5, 0.3, 0.2),
    (0.33, 0.33, 0.34),
    (0.2, 0.5, 0.3),
    (0.1, 0.6, 0.3),
    (0.0, 0.3, 0.6),
    (0.0, 0.2, 0.8),
    (0.0, 0.1, 0.9),
]


def pareto_2D_2_3(weights,name):


    results = []

    for w in weight_sets:
        print(f"résolution avec w2={w[1]}, w3={w[2]}")
        z2, z3 = multi23_lineaire(
            "./../data/voeux2024_v4.csv",
            "./../data/EDT_M1S2_2024_v6_avec_ects.csv",
            "./../data/ues_parcours.csv",
            "./../data/nb_ue_hors_parcours.csv",
            "./../data/ue_incompatibles.csv",
            w[1],
            w[2]
        )

        results.append({
            "weights": w,
            "z2": z2,
            "z3": z3,
        })


    # --- Affichage graphique ---
    plt.figure(figsize=(10, 6))
    #ax = fig.add_subplot(111, projection='3d')

    for r in results:
        plt.scatter( r["z2"], r["z3"], label=f"w={r['weights']}")
        plt.text(r["z2"], r["z3"], f"{r['weights']}", size=8)

    plt.xlabel("z2 (UE parcours manquantes)")
    plt.ylabel("z3 (emplois du temps invalides)")
    plt.title("Solutions pondérées (minimisation)")
    plt.grid(True)

    plt.legend()
    plt.tight_layout()
    plt.savefig(name)
    plt.show()


#TEST : COMPARAISON z2 et z3

#pareto_2D_2_3(weight_sets,"Comparaison_strict_z2_&_z3.png")


#==========================================================#
    

def pareto_2D_1_3(weights,name):


    results = []

    for w in weight_sets:
        print(f"résolution avec w1={w[0]}, w3={w[2]}")
        z1, z3 = multi13_lineaire(
            "./../data/voeux2024_v4.csv",
            "./../data/EDT_M1S2_2024_v6_avec_ects.csv",
            "./../data/ues_parcours.csv",
            "./../data/nb_ue_hors_parcours.csv",
            "./../data/ue_incompatibles.csv",
            w[0],
            w[2]
        )

        results.append({
            "weights": w,
            "z1": z1,
            "z3": z3,
        })


    # --- Affichage graphique ---
    plt.figure(figsize=(10, 6))
    #ax = fig.add_subplot(111, projection='3d')

    for r in results:
        plt.scatter( r["z1"], r["z3"], label=f"w={r['weights']}")
        plt.text(r["z1"], r["z3"], f"{r['weights']}", size=8)

    plt.xlabel("z1 (nombre d'étudiants sans EDT préféré)")
    plt.ylabel("z3 (nombre d'étudiants sans EDT)")
    plt.title("Solutions pondérées (minimisation)")
    plt.grid(True)

    plt.legend()
    plt.tight_layout()
    plt.savefig(name)
    plt.show()


#TEST : COMPARAISON z1 et z3

#pareto_2D_1_3(weight_sets,"Comparaison_strict_z1_&_z3.png")


#==========================================================#

#Récupère l'ensemble des points non-dominés au sens de Pareto
def get_pareto_front_2D_1_2(points):
    pareto = []
    for i, p in enumerate(points):
        dominated = False
        for j, q in enumerate(points):
            if i != j and q["z1"] <= p["z1"] and q["z2"] <= p["z2"] and (q["z1"] < p["z1"] or q["z2"] < p["z2"]):
                dominated = True
                break
        if not dominated:
            pareto.append(p)
    return pareto


def pareto_2D_1_2(weights,name):


    results = []

    for w in weight_sets:
        print(f"résolution avec w1={w[0]}, w2={w[1]}")
        z1, z2 = multi12_lineaire(
            "./../data/voeux2024_v4.csv",
            "./../data/EDT_M1S2_2024_v6_avec_ects.csv",
            "./../data/ues_parcours.csv",
            "./../data/nb_ue_hors_parcours.csv",
            "./../data/ue_incompatibles.csv",
            w[0],
            w[1],
            0.98
        )

        results.append({
            "weights": w,
            "z1": z1,
            "z2": z2,
        })

     # --- Calcul du front de Pareto ---
    pareto = get_pareto_front_2D_1_2(results)
    pareto_sorted = sorted(pareto, key=lambda r: r["z1"])  # ou z2 selon orientation souhaitée

    # --- Affichage graphique ---
    plt.figure(figsize=(10, 6))
    #ax = fig.add_subplot(111, projection='3d')

    for r in results:
        plt.scatter( r["z1"], r["z2"], label=f"w={r['weights']}")
        plt.text(r["z1"], r["z2"], f"{r['weights']}", size=8)

    
    # Tracé du front de Pareto
    z1_pareto = [r["z1"] for r in pareto_sorted]
    z2_pareto = [r["z2"] for r in pareto_sorted]
    plt.plot(z1_pareto, z2_pareto, color='crimson', linewidth=2, label='Front de Pareto')

    plt.xlabel("z1 (nombre d'étudiants sans EDT préféré)")
    plt.ylabel("z2 (nombre d'étudiants qui n'ont pas au moins une UE de parcours)")
    plt.title("Solutions pondérées (minimisation)")
    plt.grid(True)

    plt.legend()
    plt.tight_layout()
    plt.savefig(name)
    plt.show()


#TEST : COMPARAISON z1 et z2

pareto_2D_1_2(weight_sets,"Comparaison_strict_z1_&_z2.png")
