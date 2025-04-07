import numpy as np
import math
from sentence_transformers import SentenceTransformer

class SessionGraphBuilder:
    def __init__(self, lambda_recency=0.05):
        self.lambda_recency = lambda_recency
        self.session_graphs = {}

    def build_graph(self, session_data):
        """
        Builds a session graph for each user.
        Output: {userId: {from_query: {to_query: weighted_value}}}
        """
        for session in session_data:
            user_id = session['userId']
            transitions = session['transitions']
            if user_id not in self.session_graphs:
                self.session_graphs[user_id] = {}

            for trans in transitions:
                from_q = trans['from']
                to_q = trans['to']
                base_weight = trans['weight']
                delta_t = trans['timeDifference']

                # Apply recency decay
                recency_weight = base_weight * math.exp(-self.lambda_recency * delta_t)

                if from_q not in self.session_graphs[user_id]:
                    self.session_graphs[user_id][from_q] = {}
                self.session_graphs[user_id][from_q][to_q] = recency_weight

        return self.session_graphs


class SessionGraphEmbedder:
    def __init__(self, model_name='paraphrase-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def embed_session_graphs(self, session_data):
        """
        Converts each session graph into a single embedding vector per user.
        Output: {userId: session_embedding_vector}
        """
        session_vectors = {}

        for session in session_data:
            user_id = session['userId']
            queries = {q['queryId']: q['text'] for q in session['queries']}
            transitions = session['transitions']

            weighted_embeddings = []
            total_weight = 0

            for trans in transitions:
                from_id = trans['from']
                to_id = trans['to']
                weight = trans['weight']

                from_text = queries.get(from_id)
                to_text = queries.get(to_id)

                if from_text and to_text:
                    # Embed both queries
                    from_vec = self.model.encode(from_text)
                    to_vec = self.model.encode(to_text)

                    # Average them to represent the transition
                    transition_vec = (from_vec + to_vec) / 2.0
                    weighted_embeddings.append(transition_vec * weight)
                    total_weight += weight

            if weighted_embeddings:
                session_vector = np.sum(weighted_embeddings, axis=0) / total_weight
                session_vectors[user_id] = session_vector

        return session_vectors


class UserProfileEmbedder:
    def __init__(self, model_name='paraphrase-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def embed_users(self, user_data):
        """
        Embeds user profile data (interests + favorite brands).
        Output: {userId: embedding_vector}
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
class ContextFusion:
    def __init__(self, alpha=0.5):
        """
        alpha: balance between session and user profile embeddings
               (0.5 means equal weight)
        """
        self.alpha = alpha

    def fuse(self, session_embeddings, user_embeddings):
        """
        Returns: {userId: fused_vector}
        """
        fused_embeddings = {}

        for user_id in session_embeddings:
            if user_id in user_embeddings:
                session_vec = session_embeddings[user_id]
                user_vec = user_embeddings[user_id]
                # Weighted average
                fused = self.alpha * session_vec + (1 - self.alpha) * user_vec
                fused_embeddings[user_id] = fused
            else:
                # fallback: use session vector only
                fused_embeddings[user_id] = session_embeddings[user_id]

        return fused_embeddings
