import json
from fastapi import APIRouter
import numpy as np
import pygad
from typing import List, Dict

router = APIRouter(prefix="/ag-genetic-team", tags=["Algo-Genetic-Team"])

# Paramètres de l'algorithme génétique
POPULATION_SIZE = 50
MUTATION_RATE = 10  # Pourcentage des gènes mutés
MAX_GENERATIONS = 100
TEAM_SIZE = 5  # Taille de l'équipe à sélectionner

def convert_numpy_types(obj):
    """Convertit les types numpy en types natifs Python pour la sérialisation JSON"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def load_weights():
    with open("data/weights.json", "r") as file:
        weights = json.load(file)
    return np.array(weights)
    
weights = load_weights()

def load_population():
    with open("data/top_50_candidates.json", "r") as file:
        data = json.load(file)
    
    population = np.array([[min(candidate[f"criterion_{i+1}"], 95) for i in range(len(weights))] for candidate in data])
    names = [candidate["name"] for candidate in data]
    return names, population

names, population = load_population()

def fitness_function(ga_instance, solution, solution_idx):
    # Calcul du score global de l'équipe
    team_score = sum(min(95, solution[i]) * weights[i % len(weights)] for i in range(len(solution)))
    
    # Pénalités
    penalty = 0
    
    # 1. Pénalité pour les valeurs > 95
    penalty += sum(max(0, value - 95) * 100 for value in solution)
    
    # 2. Pénalité pour les doublons
    team_indices = [i // len(weights) for i in range(len(solution))]
    unique_indices = set(team_indices)
    if len(unique_indices) < TEAM_SIZE:
        penalty += 1000 * (TEAM_SIZE - len(unique_indices))
    
    return team_score - penalty

def mutation_function(offspring, ga_instance):
    for chromosome_idx in range(offspring.shape[0]):
        for gene_idx in range(offspring.shape[1]):
            if np.random.random() < MUTATION_RATE/100:
                offspring[chromosome_idx, gene_idx] += np.random.uniform(-5, 5)
        
        offspring[chromosome_idx] = np.clip(offspring[chromosome_idx], 0, 95)
    
    return offspring

def create_initial_team_population():
    fitness_scores = [sum(min(95, sol[i]) * weights[i] for i in range(len(weights))) for sol in population]
    sorted_indices = np.argsort(fitness_scores)[::-1]
    
    initial_teams = []
    for _ in range(POPULATION_SIZE):
        selected_indices = np.random.choice(sorted_indices[:20], size=TEAM_SIZE, replace=False)
        team = []
        for idx in selected_indices:
            team.extend(population[idx])
        initial_teams.append(team)
    
    return np.array(initial_teams)

ga_team_instance = pygad.GA(
    num_generations=MAX_GENERATIONS,
    num_parents_mating=5,
    fitness_func=fitness_function,
    sol_per_pop=POPULATION_SIZE,
    num_genes=TEAM_SIZE * len(weights),
    initial_population=create_initial_team_population(),
    mutation_type=mutation_function,
    gene_space=[(0, 95) for _ in range(TEAM_SIZE * len(weights))],
    crossover_type="single_point"
)

def analyze_improvements(original_team, optimized_team):
    improvements = []
    for i in range(TEAM_SIZE):
        original_start = i * len(weights)
        original_end = (i+1) * len(weights)
        original_criteria = original_team[original_start:original_end]
        optimized_criteria = optimized_team[original_start:original_end]
        
        criteria_improvements = []
        for j in range(len(weights)):
            improvement = optimized_criteria[j] - original_criteria[j]
            if improvement > 0:
                criteria_improvements.append({
                    "criterion": j+1,
                    "improvement": round(float(improvement), 2),
                    "original_value": round(float(original_criteria[j]), 2),
                    "optimized_value": round(float(optimized_criteria[j]), 2)
                })
        
        improvements.append({
            "name": names[i],
            "total_improvement": round(float(sum(opt - orig for orig, opt in zip(original_criteria, optimized_criteria))), 2),
            "criteria_improvements": criteria_improvements
        })
    return improvements

def run_team_genetic_algorithm():
    ga_team_instance.run()

    best_solution, best_fitness, _ = ga_team_instance.best_solution()
    best_team = best_solution
    
    team_candidates = []
    for i in range(TEAM_SIZE):
        start_idx = i * len(weights)
        end_idx = (i+1) * len(weights)
        candidate_criteria = best_team[start_idx:end_idx]
        
        distances = [np.linalg.norm(candidate_criteria - candidate) for candidate in population]
        closest_idx = np.argmin(distances)
        
        team_candidates.append({
            "name": names[closest_idx],
            "fitness": round(float(sum(min(95, value) * weights[j] for j, value in enumerate(candidate_criteria))), 2),
            "criteria": [round(float(value), 2) for value in candidate_criteria],
            "original_criteria": [round(float(value), 2) for value in population[closest_idx]]
        })
    
    original_team = []
    for candidate in team_candidates:
        original_team.extend(candidate["original_criteria"])
    
    improvements = analyze_improvements(original_team, best_team)
    
    return {
        "team": team_candidates,
        "team_fitness": round(float(best_fitness), 2),
        "improvement_analysis": improvements
    }

@router.get("/best_team")
def get_best_team():
    result = run_team_genetic_algorithm()
    
    # Convertir explicitement tous les types numpy
    converted_result = {
        "optimal_team": result["team"],
        "team_score": result["team_fitness"],
        "improvement_analysis": result["improvement_analysis"]
    }
    
    return converted_result 