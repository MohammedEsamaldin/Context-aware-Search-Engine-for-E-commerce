import numpy as np
import warnings

def fuse_vectors(alpha, user_id, query_vector, context_vectors, projection_method='linear',
                 projection_matrix=None, bias=None):
    """
    Fuses vectors with dimension handling using projection or fallback strategies.
    
    Parameters:
    - alpha (float): Weight between query (alpha) and context (1-alpha)
    - user_id (str): Target user ID for context lookup
    - query_vector (list/np.array): Current query embedding
    - context_vectors (dict): User-context mappings
    - projection_method (str): 'linear' (default) or 'pad' for handling mismatches
    - projection_matrix (np.array, optional): Predefined matrix for linear projection
    - bias (np.array, optional): Predefined bias for linear projection
  
    Returns:
    - np.array: Fused vector with handling for dimension mismatches
    """
    # Convert inputs to numpy arrays
    query = np.array(query_vector).flatten()  # expected shape, e.g., (1536,)
    context = np.array(context_vectors.get(user_id, [])).flatten()  # e.g., (384,)
    
    if not context.size:
        # No context available, return pure query vector scaled by alpha.
        return alpha * query
    
    if query.shape == context.shape:
        # Perfect dimension match - simple weighted sum.
        return alpha * query + (1 - alpha) * context
    
    # Handle dimension mismatch
    warnings.warn(f"Dimension mismatch: Query {query.shape} vs Context {context.shape}. Using {projection_method} projection.")
    
    if projection_method == 'linear':
        # Define target dimensions: map context to query dimension.
        context_dim = context.shape[0]   # e.g., 384
        query_dim = query.shape[0]       # e.g., 1536
        
        # If no projection matrix is provided, initialize one randomly.
        if projection_matrix is None:
            # Random matrix: shape (context_dim, query_dim)
            projection_matrix = np.random.randn(context_dim, query_dim).astype(np.float32)
        # Apply the projection: projected_context will have shape (query_dim,)
        projected_context = np.dot(context, projection_matrix)
        
        # Optionally, if bias is provided or needed:
        if bias is not None:
            projected_context = projected_context + bias
        
        # Fuse the query vector and projected context vector
        fused = alpha * query + (1 - alpha) * projected_context
        return fused
    
    elif projection_method == 'pad':
        # Pad the smaller vector (context) with zeros to match query dimension.
        target_dim = query.shape[0]
        padded_context = np.zeros(target_dim, dtype=context.dtype)
        padded_context[:context.shape[0]] = context
        fused = alpha * query + (1 - alpha) * padded_context
        return fused

    else:
        raise ValueError(f"Unknown projection method: {projection_method}")

def project_vector(source_vec, target_dim, seed=None):
    """Projects vector to target dimension using random matrix"""
    rng = np.random.default_rng(seed)
    orig_dim = len(source_vec)
    
    if orig_dim == target_dim:
        return source_vec
    
    # Create projection matrix (consider caching this)
    projection_matrix = rng.normal(size=(orig_dim, target_dim))
    
    # Normalize and project
    source_normalized = source_vec / np.linalg.norm(source_vec)
    return np.dot(source_normalized, projection_matrix)

def pad_or_truncate(vec, target_dim):
    """Matches dimensions by padding with zeros or truncating"""
    if len(vec) < target_dim:
        return np.pad(vec, (0, target_dim - len(vec)))
    return vec[:target_dim]

# def fuse_vectors(alpha, user_id, query_vector, context_vectors):
#     """
#     Fuses the query vector and context vector based on a given weight (alpha).

#     Args:
#     - alpha (float): The weight to balance between the query vector and context vector.
#     - user_id (str): The user ID whose context vector is to be used.
#     - query_log (object): The query log object containing the query embedding.
#     - context_vectors (dict): Dictionary of context vectors for users, with user IDs as keys.

#     Returns:
#     - fused_vector (numpy array): The weighted sum of the query vector and context vector.
#     """
#     # Initialize the query vector from the query_log's embedding
#     query_vector = np.array(query_vector)
    
#     # Initialize an empty list for the fused vector (though it will be a numpy array)
#     fused_vector = []
    
#     # Check if the target user_id exists in context_vectors
#     if user_id in context_vectors:
#         # Get the context vector for the target user_id and convert it to numpy array
#         context_vec = np.array(context_vectors[user_id])
        
#         # Perform element-wise multiplication and fusion
#         fused_vector = alpha * query_vector + (1 - alpha) * context_vec
#     else:
#         return 
    
#     return fused_vector
