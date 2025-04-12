import json

import numpy as np
import pygad
from fastapi import APIRouter

router = APIRouter(prefix="/ag-genetic", tags=["Algo-Genetic"])

# Paramètres de l'algorithme génétique
POPULATION_SIZE = 50
MUTATION_RATE = 10  # Pourcentage des gènes mutés
MAX_GENERATIONS = 100


def load_weights():
    with open("data/weights.json", "r") as file:
        return np.array(json.load(file))


weights = load_weights()


def load_population():
    with open("data/top_50_candidates.json", "r") as file:
        data = json.load(file)

    # Limiter les valeurs à 95 lors du chargement
    population = np.array(
        [
            [min(candidate[f"criterion_{i+1}"], 95) for i in range(len(weights))]
            for candidate in data
        ]
    )
    names = [candidate["name"] for candidate in data]
    return names, population


names, population = load_population()


def fitness_function(ga_instance, solution, solution_idx):
    # Pénalité forte pour les valeurs > 95
    penalty = sum(max(0, value - 95) * 100 for value in solution)
    # Utiliser min(95, value) pour le calcul du score
    return sum(min(95, solution[i]) * weights[i] for i in range(len(weights))) - penalty


def mutation_function(offspring, ga_instance):
    # Mutation standard avec pourcentage de gènes mutés
    for chromosome_idx in range(offspring.shape[0]):
        # Sélectionner aléatoirement les gènes à muter
        genes_to_mutate = (
            np.random.random(size=offspring.shape[1]) < MUTATION_RATE / 100
        )

        # Appliquer une mutation aléatoire aux gènes sélectionnés
        random_values = np.random.uniform(-1, 1, size=offspring.shape[1])
        offspring[chromosome_idx, genes_to_mutate] += random_values[genes_to_mutate]

        # Limiter les valeurs entre 0 et 95
        offspring[chromosome_idx] = np.clip(offspring[chromosome_idx], 0, 95)

    return offspring


# Configuration de PyGAD
ga_instance = pygad.GA(
    num_generations=MAX_GENERATIONS,
    num_parents_mating=5,
    fitness_func=fitness_function,
    sol_per_pop=POPULATION_SIZE,
    num_genes=len(weights),
    mutation_num_genes=3,
    initial_population=population,
    mutation_type=mutation_function,  # Utiliser notre fonction de mutation personnalisée
    gene_space=[
        (0, 95) for _ in range(len(weights))
    ],  # Tous les gènes doivent être entre 0 et 95
)


def run_genetic_algorithm():
    ga_instance.run()

    # Récupérer la population finale
    final_population = ga_instance.population

    # Calculer la fitness de chaque individu (sans pénalité pour l'affichage)
    fitness_scores = [
        sum(min(95, sol[i]) * weights[i] for i in range(len(weights)))
        for sol in final_population
    ]

    # Trier par fitness décroissante
    sorted_indices = np.argsort(fitness_scores)[::-1]

    best_candidates = [
        {
            "name": names[sorted_indices[i]],
            "fitness": fitness_scores[sorted_indices[i]],
            "criteria": [
                min(95, value) for value in final_population[sorted_indices[i]].tolist()
            ],
        }
        for i in range(min(5, len(sorted_indices)))
    ]

    return best_candidates


@router.get("/best_candidates")
def get_best_candidates():
    best_candidates = run_genetic_algorithm()
    return {"best_candidates": best_candidates}
