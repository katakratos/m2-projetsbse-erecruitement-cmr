import numpy as np
import json
import random
from ..models import CandidateData, Job

# Genetic Algorithm parameters
POPULATION_SIZE = 50
MUTATION_RATE = 10  # Percentage of genes to be mutated
MAX_GENERATIONS = 100

def get_candidate_data_for_job(job_id):
    """Get all candidates for a job with their scores"""
    job = Job.objects.get(id=job_id)
    candidates = CandidateData.objects.filter(job=job).order_by('ahp_rank')
    
    # Get the top 50 candidates at most (or fewer if there are less than 50)
    candidates = candidates[:50]
    
    names = []
    scores_array = []
    
    for candidate in candidates:
        name = candidate.jobseeker.get_full_name()
        
        # Extract all the criteria scores
        criteria_scores = [
            candidate.business_unit_flexibility,
            candidate.past_experience,
            candidate.education_level,
            candidate.language_skills,
            candidate.strategic_thinking,
            candidate.communication_skills,
            candidate.computer_skills
        ]
        
        names.append(name)
        scores_array.append(criteria_scores)
    
    return names, np.array(scores_array)

def get_weights_from_ahp(job_id):
    """Get the weights from the AHP model for a job"""
    job = Job.objects.get(id=job_id)
    try:
        ahp = job.ahp_priority
        if ahp and ahp.weights:
            weights = np.array(ahp.weights)
            return weights
    except Exception as e:
        print(f"Error getting AHP weights: {e}")
    
    # Default equal weights if AHP not defined
    return np.array([1/7, 1/7, 1/7, 1/7, 1/7, 1/7, 1/7])

class GeneticTeamOptimizer:
    def __init__(self, job_id, team_size):
        self.job_id = job_id
        self.team_size = team_size
        self.names, self.population = get_candidate_data_for_job(job_id)
        self.weights = get_weights_from_ahp(job_id)
        self.num_criteria = len(self.weights)
        
        # Ensure we have enough candidates
        if len(self.names) < team_size:
            raise ValueError(f"Not enough candidates ({len(self.names)}) for team size ({team_size})")
            
        # Initialize the genetic algorithm
        self.best_solution = None
        self.best_fitness = -1
        
    def initial_population(self):
        """Create initial population with random teams"""
        population = []
        
        for _ in range(POPULATION_SIZE):
            # Select random indices for team members
            team_indices = random.sample(range(len(self.names)), self.team_size)
            chromosome = np.concatenate([self.population[idx] for idx in team_indices])
            population.append(chromosome)
            
        return np.array(population)
    
    def fitness_function(self, solution):
        """Calculate fitness of a solution (team)"""
        fitness = 0
        
        # Calculate team's total weighted score
        for i in range(self.team_size):
            start_idx = i * self.num_criteria
            end_idx = (i + 1) * self.num_criteria
            
            member_scores = solution[start_idx:end_idx]
            member_fitness = sum(score * weight for score, weight in zip(member_scores, self.weights))
            fitness += member_fitness
        
        # Apply penalties for duplicate team members
        team_indices = self.get_candidate_indices(solution)
        if len(set(team_indices)) < self.team_size:
            # Penalize solutions with duplicate candidates
            fitness -= 1000
            
        return fitness
    
    def get_candidate_indices(self, solution):
        """Get the indices of candidates in the solution"""
        team_indices = []
        
        for i in range(self.team_size):
            start_idx = i * self.num_criteria
            end_idx = (i + 1) * self.num_criteria
            
            member_scores = solution[start_idx:end_idx]
            
            # Find the closest candidate in our population
            distances = np.array([np.linalg.norm(member_scores - candidate) for candidate in self.population])
            closest_idx = np.argmin(distances)
            team_indices.append(closest_idx)
            
        return team_indices
    
    def selection(self, population, fitness_scores):
        """Tournament selection"""
        selected_parents = []
        
        for _ in range(POPULATION_SIZE // 2):  # Select half the population
            # Select 3 random candidates for tournament
            tournament_indices = random.sample(range(POPULATION_SIZE), 3)
            tournament_fitness = [fitness_scores[idx] for idx in tournament_indices]
            
            # Select the best from the tournament
            winner_idx = tournament_indices[np.argmax(tournament_fitness)]
            selected_parents.append(population[winner_idx])
            
        return np.array(selected_parents)
    
    def crossover(self, parents):
        """Perform crossover to create offspring"""
        offspring = []
        
        # Ensure even number of parents
        if len(parents) % 2 == 1:
            parents = parents[:-1]
            
        # Random shuffling of parents
        np.random.shuffle(parents)
        
        # Perform crossover for each pair of parents
        for i in range(0, len(parents), 2):
            parent1 = parents[i]
            parent2 = parents[i+1]
            
            # Single point crossover
            crossover_point = np.random.randint(1, len(parent1) - 1)
            
            child1 = np.concatenate([parent1[:crossover_point], parent2[crossover_point:]])
            child2 = np.concatenate([parent2[:crossover_point], parent1[crossover_point:]])
            
            offspring.append(child1)
            offspring.append(child2)
            
        return np.array(offspring)
    
    def mutation(self, offspring):
        """Apply mutation to offspring"""
        for i in range(len(offspring)):
            # Decide which genes to mutate
            mutation_mask = np.random.random(len(offspring[i])) < (MUTATION_RATE / 100)
            
            if np.any(mutation_mask):
                # Apply small random changes to selected genes
                mutation_values = np.random.uniform(-5, 5, size=len(offspring[i]))
                offspring[i] = offspring[i] + mutation_values * mutation_mask
                
                # Ensure values stay within reasonable bounds (0-100)
                offspring[i] = np.clip(offspring[i], 0, 100)
                
        return offspring
    
    def run(self):
        """Run the genetic algorithm"""
        # Generate initial population
        population = self.initial_population()
        
        for generation in range(MAX_GENERATIONS):
            # Calculate fitness for each solution
            fitness_scores = np.array([self.fitness_function(solution) for solution in population])
            
            # Find the best solution
            best_idx = np.argmax(fitness_scores)
            if fitness_scores[best_idx] > self.best_fitness:
                self.best_solution = population[best_idx]
                self.best_fitness = fitness_scores[best_idx]
                
            # Selection
            parents = self.selection(population, fitness_scores)
            
            # Crossover
            offspring = self.crossover(parents)
            
            # Mutation
            offspring = self.mutation(offspring)
            
            # Create new population with elitism (keep the best solution)
            population = np.concatenate([offspring, [self.best_solution]])
            
            # Fill the remaining population with random new solutions
            remaining = POPULATION_SIZE - len(population)
            if remaining > 0:
                population = np.concatenate([population, self.initial_population()[:remaining]])
        
        # Return best solution after all generations
        return self.analyze_solution()
    
    def analyze_solution(self):
        """Analyze the best solution and format for display"""
        if self.best_solution is None:
            return None
            
        team_indices = self.get_candidate_indices(self.best_solution)
        team_members = []
        
        # Build team information
        for i, idx in enumerate(team_indices):
            start_idx = i * self.num_criteria
            end_idx = (i + 1) * self.num_criteria
            
            optimized_scores = self.best_solution[start_idx:end_idx]
            original_scores = self.population[idx]
            
            # Calculate improvements for each criterion
            improvements = []
            for j in range(self.num_criteria):
                if optimized_scores[j] > original_scores[j]:
                    improvements.append({
                        'criterion': j,
                        'improvement': round(optimized_scores[j] - original_scores[j], 2),
                        'original': round(original_scores[j], 2),
                        'optimized': round(optimized_scores[j], 2)
                    })
            
            # Calculate weighted scores
            original_weighted = sum(score * weight for score, weight in zip(original_scores, self.weights))
            optimized_weighted = sum(score * weight for score, weight in zip(optimized_scores, self.weights))
            
            team_members.append({
                'name': self.names[idx],
                'original_scores': [round(score, 2) for score in original_scores],
                'optimized_scores': [round(score, 2) for score in optimized_scores],
                'original_weighted': round(original_weighted, 2),
                'optimized_weighted': round(optimized_weighted, 2),
                'improvement': round(optimized_weighted - original_weighted, 2),
                'criteria_improvements': improvements
            })
        
        # Sort team by improvement (descending)
        team_members.sort(key=lambda x: x['improvement'], reverse=True)
        
        result = {
            'team_size': self.team_size,
            'team_members': team_members,
            'total_score': round(self.best_fitness, 2),
            'criteria_names': [
                'Business Unit Flexibility',
                'Past Experience',
                'Education Level',
                'Language Skills',
                'Strategic Thinking',
                'Communication Skills',
                'Computer Skills'
            ]
        }
        
        return result

def optimize_team_for_job(job_id, team_size=5):
    """Main function to run genetic algorithm and optimize a team"""
    try:
        optimizer = GeneticTeamOptimizer(job_id, team_size)
        result = optimizer.run()
        return result
    except Exception as e:
        print(f"Error in team optimization: {e}")
        return {'error': str(e)}
