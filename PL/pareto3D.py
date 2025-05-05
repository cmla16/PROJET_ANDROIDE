import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from multi123_lineaire import multi123_lineaire  # adapte selon ton fichier
from multi123_minmax_lineaire import multi123_minmax_lineaire
import numpy as np


"""========================== MON CODE ============================"""

def generate_weights(step=0.1):
    weights = []
    for w1 in np.arange(0, 1 + step, step):
        for w2 in np.arange(0, 1 + step - w1, step):
            w3 = 1 - w1 - w2
            if w3 < 0 or w3 > 1 or w1 == 0 or w2 == 0 or w3 == 0:
                continue
            weights.append((round(w1, 2), round(w2, 2), round(w3, 2)))
    return weights


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



def pareto_3D(weights, name, fonction):
    results = []
    seen_objectives = set()

    for w in weights:
        print(f"Résolution avec w1={w[0]}, w2={w[1]}, w3={w[2]}")
        if fonction == multi123_lineaire :
            z1, z2, z3 = fonction(
                "./../data/voeux2024_v4.csv",
                "./../data/EDT_M1S2_2024_v6_avec_ects.csv",
                "./../data/ues_parcours.csv",
                "./../data/nb_ue_hors_parcours.csv",
                "./../data/ue_incompatibles.csv",
                w[0],
                w[1],
                w[2]
            )
        elif fonction == multi123_minmax_lineaire :
            z1, z2, z3 = fonction(
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

        obj = (z1, z2, z3)

        if obj not in seen_objectives:
            seen_objectives.add(obj)
            results.append({
                "weights": w,
                "objectives": obj
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
#weight_sets = generate_weights()
#pareto_3D(weight_sets, "../img/front_pareto_3D_minmax.png", multi123_minmax_lineaire)
#pareto_3D(weight_sets, "../img/front_pareto_3D_minmax.png", multi123_lineaire)
    