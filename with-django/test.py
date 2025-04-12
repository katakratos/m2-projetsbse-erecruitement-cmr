import numpy as np

SAATY_SCALE = [1/9, 1/8, 1/7, 1/6, 1/5, 1/4, 1/3, 1/2, 1,
               2, 3, 4, 5, 6, 7, 8, 9]

# Random Index values for matrix sizes 1–10
RI_VALUES = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
}

def closest_saaty_value(value):
    return min(SAATY_SCALE, key=lambda x: abs(x - value))

def generate_ahp_matrix_with_cr(criteria, max_trials=1000):
    n = len(criteria)

    for trial in range(max_trials):
        # Step 1: Generate random weights and normalize
        raw_weights = np.random.rand(n)
        priorities = raw_weights / raw_weights.sum()

        # Step 2: Build matrix with rounded Saaty scale values
        matrix = np.ones((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                ratio = priorities[i] / priorities[j]
                saaty_value = closest_saaty_value(ratio)
                matrix[i][j] = saaty_value
                matrix[j][i] = 1 / saaty_value

        # Step 3: Compute Consistency Ratio
        cr = calculate_consistency_ratio(matrix)
        if cr < 0.1:
            return priorities.tolist(), matrix.tolist(), cr

    raise ValueError("Could not generate a consistent matrix after many trials")

def calculate_consistency_ratio(matrix):
    n = len(matrix)
    matrix = np.array(matrix)
    
    # Estimate priority vector using geometric mean method
    row_products = np.prod(matrix, axis=1)
    weights = row_products ** (1/n)
    weights /= np.sum(weights)

    # Calculate lambda_max
    weighted_sum = np.dot(matrix, weights)
    lambda_max = np.sum(weighted_sum / weights) / n

    # Consistency Index
    ci = (lambda_max - n) / (n - 1)
    ri = RI_VALUES.get(n, 1.49)  # Use max known RI if n > 10
    cr = ci / ri if ri else 0
    return cr

criteria = ['Price', 'Quality', 'Durability', 'Brand']
priorities, matrix, cr = generate_ahp_matrix_with_cr(criteria)

from pprint import pprint
print("Priorities:")
pprint(dict(zip(criteria, priorities)))

print("\nAHP Matrix:")
pprint(matrix)

print(f"\n✅ Consistency Ratio (CR): {cr:.4f} → {'Acceptable' if cr < 0.1 else 'Not acceptable'}")
