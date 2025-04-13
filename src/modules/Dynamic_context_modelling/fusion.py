import numpy as np

def fuse_vectors(user_id, query_vector, context_vector, alpha=0.6):
    """
    Fuses the query vector and context vector based on a given weight (alpha).

    Args:
    - alpha (float): The weight to balance between the query vector and context vector.
    - user_id (str): The user ID whose context vector is to be used.
    - query_log (object): The query log object containing the query embedding.
    - context_vectors (dict): Dictionary of context vectors for users, with user IDs as keys.

    Returns:
    - fused_vector (numpy array): The weighted sum of the query vector and context vector.
    """
    # Initialize the query vector from the query_log's embedding
    query_vector = np.array(query_vector)
    
    # Initialize an empty list for the fused vector (though it will be a numpy array)
    fused_vector = []
    
    # Check if the target user_id exists in context_vectors
    if user_id in context_vectors:
        # Get the context vector for the target user_id and convert it to numpy array
        context_vec = np.array(context_vectors[user_id])
        
        # Perform element-wise multiplication and fusion
        fused_vector = alpha * query_vector + (1 - alpha) * context_vec
    else:
        return 
    
    return fused_vector
