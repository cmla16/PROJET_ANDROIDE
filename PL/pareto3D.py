import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from multi123_lineaire import multi123_lineaire  # adapte selon ton fichier
from multi123_minmax_lineaire import multi123_minmax_lineaire
import numpy as np


"""========================== MON CODE ============================"""
"""
# Liste des poids
weight_sets = [
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
    (0.6, 0.3, 0.1),
    (0.5, 0.3, 0.2),
    (0.33, 0.33, 0.34),
    (0.2, 0.5, 0.3),
    (0.1, 0.6, 0.3),
    (0.0, 0.3, 0.6),
    (0.0, 0.2, 0.8),
    (0.0, 0.1, 0.9),
]

def pareto_3D(weights, name):
    results = []

    for w in weights:
        print(f"résolution avec w1={w[0]}, w2={w[1]}, w3={w[2]}")
        z1, z2, z3 = multi123_lineaire(
            "./../data/voeux2024_v4.csv",
            "./../data/EDT_M1S2_2024_v6_avec_ects.csv",
            "./../data/ues_parcours.csv",
            "./../data/nb_ue_hors_parcours.csv",
            "./../data/ue_incompatibles.csv",
            w[0],
            w[1],
            w[2]
        )

        results.append({
            "weights": w,
            "z1": z1,
            "z2": z2,
            "z3": z3
        })

    # --- Affichage graphique 3D ---
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    for r in results:
        ax.scatter(r["z1"], r["z2"], r["z3"], label=f"w={r['weights']}")
        ax.text(r["z1"], r["z2"], r["z3"], f"{r['weights']}", size=8)

    ax.set_xlabel("z1 (nombre d'étudiants sans EDT préféré)")
    ax.set_ylabel("z2 (nombre d'étudiants qui n'ont pas au moins une UE de parcours)")
    ax.set_zlabel("z3 (nombre d'étudiants sans EDT valide)")
    ax.set_title("Solutions pondérées (minimisation en 3D)")

    plt.legend()
    plt.tight_layout()
    plt.savefig(name)
    plt.show()

# Appel
pareto_3D(weight_sets, "Front_pareto_3D_z1_z2_z3.png")
"""


# Jeu de poids à tester
weight_sets = [
    
    (0.6, 0.3, 0.1),
    (0.5, 0.3, 0.2),
    (0.33, 0.33, 0.34),
    (0.2, 0.5, 0.3),
    (0.1, 0.6, 0.3),
    (0.1, 0.3, 0.6),
    (0.1, 0.2, 0.7),
    (0.8, 0.1, 0.1),
]

# Fonction pour identifier les solutions non dominées
def get_pareto_front(solutions):
    pareto_front = []
    for i, s in enumerate(solutions):
        dominated = False
        for j, other in enumerate(solutions):
            if i != j and all(o <= si for o, si in zip(other["objectives"], s["objectives"])) and any(o < si for o, si in zip(other["objectives"], s["objectives"])):
                dominated = True
                break
        if not dominated:
            pareto_front.append(s)
    return pareto_front


"""============================= FONCTION LINEAIRE ==========================="""


# Fonction principale : 3D avec front de Pareto
def pareto_3D_lineaire(weights, name):
    results = []

    for w in weights:
        print(f"Résolution avec w1={w[0]}, w2={w[1]}, w3={w[2]}")
        z1, z2, z3 = multi123_lineaire(
            "./../data/voeux2024_v4.csv",
            "./../data/EDT_M1S2_2024_v6_avec_ects.csv",
            "./../data/ues_parcours.csv",
            "./../data/nb_ue_hors_parcours.csv",
            "./../data/ue_incompatibles.csv",
            w[0],
            w[1],
            w[2]
        )
        results.append({
            "weights": w,
            "objectives": (z1, z2, z3)
        })

    pareto = get_pareto_front(results)



    # Préparation des points
    X_all = [r["objectives"][0] for r in results]
    Y_all = [r["objectives"][1] for r in results]
    Z_all = [r["objectives"][2] for r in results]

    X_pareto = [r["objectives"][0] for r in pareto]
    Y_pareto = [r["objectives"][1] for r in pareto]
    Z_pareto = [r["objectives"][2] for r in pareto]

    # Tracé 3D
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    for r in results:
        ax.scatter(r["objectives"][0], r["objectives"][1], r["objectives"][2], label=f"w={r['weights']}")
        ax.text(r["objectives"][0], r["objectives"][1], r["objectives"][2], f"{r['weights']}", size=8)


    #ax.scatter(X_all, Y_all, Z_all, c='skyblue', label='Toutes les solutions')
    ax.scatter(X_pareto, Y_pareto, Z_pareto, c='crimson', label='Front de Pareto', s=40)

    front=np.array([X_pareto,Y_pareto,Z_pareto])
    print("Solutions appartenant au front de Pareto : ",front)

    #Poids associés au solutions dans le front de Pareto
    w=[]
    for r in pareto:

        w.append(r["weights"])

    print("Poids associés : ",w)

    ax.set_xlabel("z1 (étudiants sans EDT préféré)")
    ax.set_ylabel("z2 (étudiants sans UE de parcours)")
    ax.set_zlabel("z3 (étudiants sans contrat valide)")

    ax.set_title("Front de Pareto - Optimisation 3 objectifs")
    ax.legend()
    plt.tight_layout()
    plt.savefig(name)
    plt.show()


# Appel à la fonction
#pareto_3D_lineaire(weight_sets, "../img/front_pareto_3D_lineaire.png")


"""============================= FONCTION MINMAX ==========================="""

def pareto_3D_minmax(weights, name):
    results = []

    for w in weights:
        print(f"Résolution avec w1={w[0]}, w2={w[1]}, w3={w[2]}")
        z1, z2, z3 = multi123_minmax_lineaire(
            "./../data/voeux2024_v4.csv",
            "./../data/EDT_M1S2_2024_v6_avec_ects.csv",
            "./../data/ues_parcours.csv",
            "./../data/nb_ue_hors_parcours.csv",
            "./../data/ue_incompatibles.csv",
            0.01,
            w[0],
            w[1],
            w[2]
        )
        results.append({
            "weights": w,
            "objectives": (z1, z2, z3)
        })

    pareto = get_pareto_front(results)



    # Préparation des points
    X_all = [r["objectives"][0] for r in results]
    Y_all = [r["objectives"][1] for r in results]
    Z_all = [r["objectives"][2] for r in results]

    X_pareto = [r["objectives"][0] for r in pareto]
    Y_pareto = [r["objectives"][1] for r in pareto]
    Z_pareto = [r["objectives"][2] for r in pareto]

    # Tracé 3D
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    for r in results:
        ax.scatter(r["objectives"][0], r["objectives"][1], r["objectives"][2], label=f"w={r['weights']}")
        ax.text(r["objectives"][0], r["objectives"][1], r["objectives"][2], f"{r['weights']}", size=8)


    #ax.scatter(X_all, Y_all, Z_all, c='skyblue', label='Toutes les solutions')
    ax.scatter(X_pareto, Y_pareto, Z_pareto, c='crimson', label='Front de Pareto', s=40)

    front=np.array([X_pareto,Y_pareto,Z_pareto])
    print("Solutions appartenant au front de Pareto : ",front)

    #Poids associés au solutions dans le front de Pareto
    w=[]
    for r in pareto:

        w.append(r["weights"])

    print("Poids associés : ",w)

    ax.set_xlabel("z1 (étudiants sans EDT préféré)")
    ax.set_ylabel("z2 (étudiants sans UE de parcours)")
    ax.set_zlabel("z3 (étudiants sans contrat valide)")

    ax.set_title("Front de Pareto - Optimisation 3 objectifs")
    ax.legend()
    plt.tight_layout()
    plt.savefig(name)
    plt.show()



#Test 

pareto_3D_minmax(weight_sets, "../img/front_pareto_3D_minmax.png")
    