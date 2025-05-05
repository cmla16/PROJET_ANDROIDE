import matplotlib.pyplot as plt
from multi23_lineaire import multi23_lineaire
from multi13_lineaire import multi13_lineaire
from multi12_lineaire import multi12_lineaire
import numpy as np

"===================MON CODE======================"

def generate_weights(step=0.1):
    weights = []
    for w1 in np.arange(0, 1 + step, step):
        for w2 in np.arange(0, 1 + step - w1, step):
            w3 = 1 - w1 - w2
            if w3 < 0 or w3 > 1 or w1 == 0 or w2 == 0 or w3 == 0:
                continue
            weights.append((round(w1, 2), round(w2, 2), round(w3, 2)))
    return weights
weight_sets = generate_weights()

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
