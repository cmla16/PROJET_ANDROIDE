import matplotlib.pyplot as plt
import numpy as np
import os
import sys

multi_2_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../multi_2'))
sys.path.append(multi_2_path)

output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../output/img'))
os.makedirs(output_dir, exist_ok=True)

from multi23_lineaire import multi23_lineaire
from multi13_lineaire import multi13_lineaire
from multi12_lineaire import multi12_lineaire
from multi23_minmax import multi23_minmax
from multi13_minmax import multi13_minmax
from multi12_minmax import multi12_minmax

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


def pareto_2D_1_2(weights,name, fonction):
    results = []
    seen_objectives = set()

    for w in weight_sets:
        print(f"résolution avec w1={w[1]}, w2={w[2]}")
        if fonction == multi12_lineaire:
            z1, z2 = multi12_lineaire(
                "./../../data/voeux2024_v4.csv",
                "./../../data/EDT_M1S2_2024_v6_avec_ects.csv",
                "./../../data/ues_parcours.csv",
                "./../../data/nb_ue_hors_parcours.csv",
                "./../../data/ue_incompatibles.csv",
                w[1],
                w[2],
                0.98
            )
        elif fonction == multi12_minmax:
            z1, z2 = multi12_minmax(
                "./../../data/voeux2024_v4.csv",
                "./../../data/EDT_M1S2_2024_v6_avec_ects.csv",
                "./../../data/ues_parcours.csv",
                "./../../data/nb_ue_hors_parcours.csv",
                "./../../data/ue_incompatibles.csv",
                0.01,
                w[1],
                w[2],
                0.98
            )

        obj = (z1, z2)

        if obj not in seen_objectives:
            seen_objectives.add(obj)
            results.append({
                "weights": w,
                "objectives": obj
            })


    # --- Affichage graphique ---
    plt.figure(figsize=(10, 6))
    #ax = fig.add_subplot(111, projection='3d')

    for r in results:
        z1, z2 = r["objectives"]
        plt.scatter(z1, z2, label=f"w={r['weights']}")
        plt.text(z1, z2, f"{r['weights']}", size=8)

    plt.xlabel("z1 (nombre d'étudiants sans EDT préféré)")
    plt.ylabel("z2 (UE parcours manquantes)")
    plt.title("Solutions pondérées (minimisation)")
    plt.grid(True)

    plt.legend()
    plt.tight_layout()
    filepath = os.path.join(output_dir, name)
    plt.savefig(filepath)
    plt.show()


def pareto_2D_2_3(weights,name, fonction):
    results = []
    seen_objectives = set()

    for w in weight_sets:
        print(f"résolution avec w2={w[1]}, w3={w[2]}")
        if fonction == multi23_lineaire:
            z2, z3 = multi23_lineaire(
                "./../../data/voeux2024_v4.csv",
                "./../../data/EDT_M1S2_2024_v6_avec_ects.csv",
                "./../../data/ues_parcours.csv",
                "./../../data/nb_ue_hors_parcours.csv",
                "./../../data/ue_incompatibles.csv",
                w[1],
                w[2]
            )
        elif fonction == multi23_minmax:
            z2, z3 = multi23_minmax(
                "./../../data/voeux2024_v4.csv",
                "./../../data/EDT_M1S2_2024_v6_avec_ects.csv",
                "./../../data/ues_parcours.csv",
                "./../../data/nb_ue_hors_parcours.csv",
                "./../../data/ue_incompatibles.csv",
                0.01,
                w[1],
                w[2]
            )

        obj = (z2, z3)

        if obj not in seen_objectives:
            seen_objectives.add(obj)
            results.append({
                "weights": w,
                "objectives": obj
            })


    # --- Affichage graphique ---
    plt.figure(figsize=(10, 6))
    #ax = fig.add_subplot(111, projection='3d')

    for r in results:
        z2, z3 = r["objectives"]
        plt.scatter(z2, z3, label=f"w={r['weights']}")
        plt.text(z2, z3, f"{r['weights']}", size=8)

    plt.xlabel("z2 (UE parcours manquantes)")
    plt.ylabel("z3 (emplois du temps invalides)")
    plt.title("Solutions pondérées (minimisation)")
    plt.grid(True)

    plt.legend()
    plt.tight_layout()
    filepath = os.path.join(output_dir, name)
    plt.savefig(filepath)
    plt.show()
    

def pareto_2D_1_3(weights,name, fonction):
    results = []
    seen_objectives = set()

    for w in weight_sets:
        print(f"résolution avec w1={w[1]}, w3={w[2]}")
        if fonction == multi13_lineaire:
            z1, z3 = multi13_lineaire(
                "./../../data/voeux2024_v4.csv",
                "./../../data/EDT_M1S2_2024_v6_avec_ects.csv",
                "./../../data/ues_parcours.csv",
                "./../../data/nb_ue_hors_parcours.csv",
                "./../../data/ue_incompatibles.csv",
                w[1],
                w[2]
            )
        elif fonction == multi13_minmax:
            z1, z3 = multi13_minmax(
                "./../../data/voeux2024_v4.csv",
                "./../../data/EDT_M1S2_2024_v6_avec_ects.csv",
                "./../../data/ues_parcours.csv",
                "./../../data/nb_ue_hors_parcours.csv",
                "./../../data/ue_incompatibles.csv",
                0.01,
                w[1],
                w[2]
            )

        obj = (z1, z3)

        if obj not in seen_objectives:
            seen_objectives.add(obj)
            results.append({
                "weights": w,
                "objectives": obj
            })


    # --- Affichage graphique ---
    plt.figure(figsize=(10, 6))
    #ax = fig.add_subplot(111, projection='3d')

    for r in results:
        z1, z3 = r["objectives"]
        plt.scatter(z1, z3, label=f"w={r['weights']}")
        plt.text(z1, z3, f"{r['weights']}", size=8)

    plt.xlabel("z1 (nombre d'étudiants sans EDT préféré)")
    plt.ylabel("z3 (emplois du temps invalides)")
    plt.title("Solutions pondérées (minimisation)")
    plt.grid(True)

    plt.legend()
    plt.tight_layout()
    filepath = os.path.join(output_dir, name)
    plt.savefig(filepath)
    plt.show()


#==========================================================#


if __name__ == "__main__":

    #weight_sets = generate_weights()

    weight_sets = [
    (0.6, 0.3, 0.1),
    (0.5, 0.3, 0.2),
    (0.33, 0.33, 0.34),
    (0.2, 0.5, 0.3),
    (0.1, 0.6, 0.3),
    ]

    #TEST : COMPARAISON z1 et z2
    #pareto_2D_1_2(weight_sets,"Comparaison_lineaire_z1_&_z2.png", multi12_lineaire)
    #pareto_2D_1_2(weight_sets,"Comparaison_minmax_z1_&_z2.png", multi12_minmax)

    #TEST : COMPARAISON z2 et z3
    #pareto_2D_2_3(weight_sets,"Comparaison_lineaire_z2_&_z3.png", multi23_lineaire)
    #pareto_2D_2_3(weight_sets,"Comparaison_minmax_z2_&_z3.png", multi23_minmax)

    #TEST : COMPARAISON z1 et z3
    #pareto_2D_1_3(weight_sets,"Comparaison_lineaire_z1_&_z3.png", multi13_lineaire)
    #pareto_2D_1_3(weight_sets,"Comparaison_minmax_z1_&_z3.png", multi13_minmax)