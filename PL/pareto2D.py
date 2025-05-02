import matplotlib.pyplot as plt
from multi23_lineaire import multi23_lineaire
from multi13_lineaire import multi13_lineaire
from multi12_lineaire import multi12_lineaire

w2_list = [1, 10, 50, 100, 300, 500, 800, 1000]
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
plt.show()
