import math

def normalize_scores(scores, mode='min-max'):
    """
    Normalise a list of numerical scores using the specified method.
    
    Params:
    - scores (list): A list of numerical scores to be normalised.
    - mode (str): The normalization mode. Can be 'min-max' or 'z-score'.
    
    Returns:
    - list: A list of normalised scores.
    """
    if not scores:
        return []

    if mode == 'min-max':
        min_score = min(scores)
        max_score = max(scores)
        if max_score == min_score:
            # Special case: If there's only one candidate, set normalized score to 1.0.
            # Otherwise, if multiple candidates have identical scores, return 0.5.
            return [1.0 if len(scores)==1 else 0.5 for _ in scores]
        range_score = max_score - min_score
        return [(score - min_score) / range_score for score in scores]

    elif mode == 'z-score':
        mean = sum(scores) / len(scores)
        variance = sum((score - mean) ** 2 for score in scores) / len(scores)
        std_dev = math.sqrt(variance) if variance > 0 else 1.0
        return [(score - mean) / std_dev for score in scores]
    
    else:
        raise ValueError("Unsupported normalization mode. Use 'min-max' or 'z-score'.")