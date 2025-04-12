import numpy as np

def calculate_consistency_ratio(matrix):
    """
    Calculate the consistency ratio of a pairwise comparison matrix
    
    Returns:
        tuple: (consistency_ratio, consistent, suggestions, weights)
            - consistency_ratio: float, the consistency ratio value
            - consistent: boolean, whether the matrix is consistent (CR < 0.1)
            - suggestions: dict, suggestions for improvement if inconsistent
            - weights: list, priority weights for each criterion
    """
    n = len(matrix)
    
    # Debug: Print the input matrix
    print("Input Matrix for Consistency Check:")
    print(matrix)
    
    # Calculate eigenvalues and eigenvectors
    try:
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        max_idx = np.argmax(eigenvalues.real)
        lambda_max = eigenvalues[max_idx].real
        
        # Debug: Print eigenvalues and max eigenvalue
        print("Eigenvalues:", eigenvalues.real)
        print("Max Eigenvalue (λmax):", lambda_max)
        
        # Calculate principal eigenvector (priority weights)
        principal_eigenvector = eigenvectors[:, max_idx].real
        weights = principal_eigenvector / np.sum(principal_eigenvector)  # Normalize to sum to 1
        
        # Debug: Print weights
        print("Priority Weights:", weights)
        
        # Calculate Consistency Index
        CI = (lambda_max - n) / (n - 1)
        
        # Random Consistency Index values
        RI_values = {1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
        RI = RI_values.get(n, 1.5)  # Default to 1.5 for n > 10
        
        # Calculate Consistency Ratio
        CR = CI / RI if RI != 0 else 0
        
        # Debug: Print consistency metrics
        print(f"Consistency Index (CI): {CI}")
        print(f"Random Index (RI): {RI}")
        print(f"Consistency Ratio (CR): {CR}")
        print(f"Is Consistent: {CR < 0.1}")
        
        consistent = CR < 0.1
        
        suggestions = {}
        if not consistent:
            # Find the most inconsistent comparisons
            most_inconsistent = []
            for i in range(n):
                for j in range(i+1, n):
                    if i != j:
                        # Calculate the expected value based on eigenvector (weights)
                        weight_ratio = weights[i] / weights[j]
                        actual = matrix[i, j]
                        diff = abs(actual - weight_ratio)
                        most_inconsistent.append((i, j, diff, weight_ratio))
            
            # Sort by difference and get top 3
            most_inconsistent.sort(key=lambda x: x[2], reverse=True)
            for i, j, diff, weight_ratio in most_inconsistent[:3]:
                # Map the weight ratio to a standard AHP scale value
                suggested_value = map_to_ahp_scale(weight_ratio)
                suggestions[(i, j)] = suggested_value
                print(f"Suggestion for [{i},{j}]: Current={matrix[i,j]}, Raw ratio={weight_ratio}, Suggested AHP value={suggested_value}")
        
        return CR, consistent, suggestions, weights.tolist()
        
    except np.linalg.LinAlgError as e:
        # Handle cases where the matrix cannot be processed
        print(f"LinAlg Error: {e}")
        return float('inf'), False, {"error": f"Matrix computation error: {str(e)}"}, []
    except Exception as e:
        # Catch any other errors for debugging
        print(f"Unexpected Error: {e}")
        return float('inf'), False, {"error": f"Unexpected error: {str(e)}"}, []

def map_to_ahp_scale(value):
    """
    Map any positive value to the closest standard AHP scale value (1-9 or reciprocals)
    
    Args:
        value: The ratio value to map
        
    Returns:
        float: A standard AHP value (1, 2, 3, 4, 5, 6, 7, 8, 9) or its reciprocal
    """
    # Define the standard AHP scale values
    ahp_values = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    reciprocal_values = [1/9, 1/8, 1/7, 1/6, 1/5, 1/4, 1/3, 1/2]
    
    # Combine all possible values
    all_values = reciprocal_values + ahp_values
    
    # If value is less than 1, we'll treat is as a reciprocal
    if value < 1:
        # Find the closest reciprocal value
        closest_recip = min(reciprocal_values, key=lambda x: abs(x - value))
        return closest_recip
    else:
        # Find the closest integer value
        closest_integer = min(ahp_values, key=lambda x: abs(x - value))
        return closest_integer

def get_all_criteria(job):
    """
    Get all criteria for a job (both boolean built-in criteria and custom criteria)
    
    Returns:
        list: List of (id, name) tuples for all criteria
    """
    criteria = []
    
    # Add boolean criteria fields
    if job.business_unit_flexibility:
        criteria.append(("bf", "Business Unit Flexibility"))
    if job.past_experience_required:
        criteria.append(("pe", "Past Experience"))
    if job.min_education_level:
        criteria.append(("ed", f"Education ({job.min_education_level})"))
    if job.foreign_language_required:
        criteria.append(("fl", "Foreign Language"))
    if job.strategic_thinking_required:
        criteria.append(("st", "Strategic Thinking"))
    if job.oral_communication_required:
        criteria.append(("oc", "Oral Communication"))
    if job.computer_skills_required:
        criteria.append(("cs", "Computer Skills"))
    
    # Add custom criteria
    for c in job.criteria_set.all():
        criteria.append((f"c{c.id}", c.criteria))
    
    return criteria

# Add these new functions for Saaty scale consistency

# Saaty AHP scale
SAATY_SCALE = [1/9, 1/8, 1/7, 1/6, 1/5, 1/4, 1/3, 1/2, 1,
               2, 3, 4, 5, 6, 7, 8, 9]

def closest_saaty_value(value):
    """Find the closest value in the Saaty scale"""
    return min(SAATY_SCALE, key=lambda x: abs(x - value))

def generate_consistent_ahp_matrix(criteria_list):
    """
    Generate a consistent AHP matrix using Saaty scale
    
    Args:
        criteria_list: List of criteria items
        
    Returns:
        tuple: (priorities, matrix)
            - priorities: List of priority weights
            - matrix: Consistent matrix with Saaty scale values
    """
    n = len(criteria_list)

    # Step 1: Generate weights with enough variance to ensure diverse comparisons
    # Use exponential distribution to ensure more spread in the values
    raw_weights = np.random.exponential(scale=1.0, size=n)
    
    # Ensure minimum variation between weights
    while np.max(raw_weights) / np.min(raw_weights) < 5:
        # If weights are too similar, regenerate with more spread
        raw_weights = np.random.exponential(scale=1.0, size=n)
    
    # Normalize weights to sum to 1
    priorities = raw_weights / raw_weights.sum()

    # Step 2: Build consistent matrix and round values to Saaty scale
    matrix = np.ones((n, n))
    
    # Track how many "1" values are in non-diagonal positions
    ones_count = 0
    total_comparisons = n * (n - 1) // 2  # Number of comparisons in upper triangle
    
    for i in range(n):
        for j in range(i + 1, n):
            # Calculate the theoretical perfect ratio
            ratio = priorities[i] / priorities[j]
            
            # Find the closest Saaty scale value
            saaty_value = closest_saaty_value(ratio)
            
            # Count if it's a "1" value
            if saaty_value == 1:
                ones_count += 1
            
            matrix[i][j] = saaty_value
            matrix[j][i] = 1 / saaty_value
    
    # If more than half of the comparisons are 1's, try again with different weights
    if ones_count > total_comparisons * 0.5:
        print(f"Too many 1's in matrix: {ones_count}/{total_comparisons}. Regenerating...")
        return generate_consistent_ahp_matrix(criteria_list)

    # Double-check consistency
    cr, is_consistent, _, actual_weights = calculate_consistency_ratio(matrix)
    
    # If somehow not consistent (which should be rare), try again with different random weights
    if not is_consistent:
        print(f"Generated matrix not consistent (CR={cr}). Regenerating...")
        return generate_consistent_ahp_matrix(criteria_list)
    
    return actual_weights, matrix.tolist()
