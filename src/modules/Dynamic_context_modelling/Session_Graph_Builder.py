import numpy as np
import json
import math
from sentence_transformers import SentenceTransformer

class SessionGraphBuilder:
    def __init__(self, lambda_recency=0.05):
        self.lambda_recency = lambda_recency
        self.session_graphs = {}

    def build_graph(self, session_data):
        """
        Builds a session graph for each user from session logs.
        Returns a dictionary: {userId: {from_query: {to_query: weighted_value}}}
        """
        for session in session_data:
            user_id = session['userId']
            transitions = session['transitions']
            if user_id not in self.session_graphs:
                self.session_graphs[user_id] = {}

            for trans in transitions:
                from_q = trans['from']
                to_q = trans['to']
                count = trans['weight']
                delta_t = trans['timeDifference']
                base_weight = count / sum(
                    t['count'] for t in transitions if t['from'] == from_q
                )

                recency_weight = base_weight * math.exp(-self.lambda_recency * delta_t)

                if from_q not in self.session_graphs[user_id]:
                    self.session_graphs[user_id][from_q] = {}
                self.session_graphs[user_id][from_q][to_q] = recency_weight
# why i did that, and what is the calculation equation for weight in dtatset
        return self.session_graphs


class UserProfileEmbedder:
    def __init__(self, model_name='paraphrase-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def embed_users(self, user_data):
        """
        Returns a dictionary of {userId: embedding_vector}
        """
        user_embeddings = {}
        for user in user_data:
            user_id = user['userId']
            brands = user['preferences'].get('favoriteBrands', [])
            interests = user['preferences'].get('interests', [])
            profile_text = " ".join(brands + interests)
            embedding = self.model.encode(profile_text)
            user_embeddings[user_id] = embedding
        return user_embeddings
