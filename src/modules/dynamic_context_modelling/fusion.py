import numpy as np
import warnings

class VectorFuser:
    def __init__(self, alpha=0.5):
        """
        Initializes the fuser with a given weight alpha.
        alpha: weight for query vector in fusion (e.g. 0.6 means 60% query, 40% context)
        """
        self.alpha = alpha

    def __call__(self, query_vector, context_vector):
        """
        Fuses the query and context vectors.

        Args:
            query_vector (array-like): The embedding of the query.
            context_vector (array-like or None): The user context embedding.

        Returns:
            numpy.ndarray or None: The fused vector or None if context is missing.
        """
        if context_vector is None:
            return None

        query_vector = np.array(query_vector)
        context_vector = np.array(context_vector)

        return self.alpha * query_vector + (1 - self.alpha) * context_vector