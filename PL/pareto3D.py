import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from multi123_lineaire import multi123_lineaire  # adapte selon ton fichier

res = []

# génère des pondérations différentes
for w1 in range(0, 201, 50):
    for w2 in range(0, 201, 50):
        for w3 in range(0, 201, 50):
            if w1 == 0 and w2 == 0 and w3 == 0:
                continue  # évite le cas nul
            print(f"Test avec w1={w1}, w2={w2}, w3={w3}")
            try:
                z1, z2, z3 = multi123_lineaire(
                    "./../data/voeux2024_v4.csv",
                    "./../data/EDT_M1S2_2024_v6_avec_ects.csv",
                    "./../data/ues_parcours.csv",
                    "./../data/nb_ue_hors_parcours.csv",
                    "./../data/ue_incompatibles.csv",
                    w1, w2, w3
                )
                res.append((z1, z2, z3))
            except:
                print(f"⚠️ échec pour w1={w1}, w2={w2}, w3={w3}")

# nuage de points
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

x, y, z = zip(*res)
ax.scatter(x, y, z, c='blue', marker='o')

ax.set_xlabel('Nb etu sans 1er voeu (z1)')
ax.set_ylabel('Nb etu sans UE parcours (z2)')
ax.set_zlabel('Nb etu sans EDT (z3)')
ax.set_title('Frontière de Pareto')

plt.show()

def get_pareto_front(points):
    pareto = []
    for p in points:
        dominated = False
        for q in points:
            if all(qi <= pi for qi, pi in zip(q, p)) and any(qi < pi for qi, pi in zip(q, p)):
                dominated = True
                break
        if not dominated:
            pareto.append(p)
    return pareto

pareto_points = get_pareto_front(res)
print(pareto_points)

# affichage avec un nuage de points coloré
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

x, y, z = zip(*res)
ax.scatter(x, y, z, c='lightgray', label='toutes les solutions')

px, py, pz = zip(*pareto_points)
ax.scatter(px, py, pz, c='red', label='frontière de pareto')

ax.set_xlabel('z1')
ax.set_ylabel('z2')
ax.set_zlabel('z3')
ax.set_title('Frontière de Pareto')
ax.legend()

plt.show()

