# import numpy as np
# import math
# from sentence_transformers import SentenceTransformer



from src.services.embedding_service import EmbeddingService
import numpy as np
import math
class ContextEmbedder:
    def __init__(self, embedding_service, alpha=0.5):
        self.embedding_service = embedding_service
        self.alpha = alpha

    def embed_single_user_and_session(self, user, session, fuse=True):
        # --- Step 1: Create profile text
        brands = user.preferences.favorite_brands if user.preferences else []
        interests = user.preferences.interests if user.preferences else []
        profile_text = " ".join(brands + interests)

        # --- Step 2: Collect unique query texts from session
        queries = {q.id: q.text for q in session.queries}
        transitions = session.transitions

        unique_texts = set()
        for trans in transitions:
            from_text = queries.get(trans.from_query)
            to_text = queries.get(trans.to)
            if from_text:
                unique_texts.add(from_text)
            if to_text:
                unique_texts.add(to_text)

        session_texts = list(unique_texts)

        # --- Step 3: Combine profile and session texts
        all_texts = [profile_text] + session_texts

        # --- Step 4: Embed all at once
        all_embeddings = self.embedding_service.embed_sentences(all_texts)

        # --- Step 5: Separate profile embedding
        profile_vec = np.array(all_embeddings[0])
        session_text_vecs = dict(zip(session_texts, all_embeddings[1:]))

        # --- Step 6: Compute session embedding with transition weights
        weighted_embeddings = []
        total_weight = 0

        for trans in transitions:
            from_text = queries.get(trans.from_query)
            to_text = queries.get(trans.to)
            weight = trans.weight

            if from_text and to_text:
                from_vec = np.array(session_text_vecs[from_text])
                to_vec = np.array(session_text_vecs[to_text])
                transition_vec = (from_vec + to_vec) / 2.0
                weighted_embeddings.append(transition_vec * weight)
                total_weight += weight

        if not weighted_embeddings:
            return None  # nothing to embed

        session_vec = np.sum(weighted_embeddings, axis=0) / total_weight

        # --- Step 7: Fuse or return separately
        if fuse:
            fused_vec = self.alpha * session_vec + (1 - self.alpha) * profile_vec
            return fused_vec
        else:
            return []
            # return {
            #     "session": session_vec,
            #     "profile": profile_vec
            # }

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
            user_id = session.user_id  # Updated to use attribute, not dictionary key
            transitions = session.transitions  # Same here

            if user_id not in self.session_graphs:
                self.session_graphs[user_id] = {}

            for trans in transitions:
                from_q = trans.from_query  # Adjust this based on your class definition
                to_q = trans.to     # Adjust this based on your class definition
                base_weight = trans.weight
                delta_t = trans.time_difference

                # Apply recency decay
                recency_weight = base_weight * math.exp(-self.lambda_recency * delta_t)

                if from_q not in self.session_graphs[user_id]:
                    self.session_graphs[user_id][from_q] = {}
                self.session_graphs[user_id][from_q][to_q] = recency_weight

        return self.session_graphs


# class SessionGraphBuilder:
#     def __init__(self, lambda_recency=0.05):
#         self.lambda_recency = lambda_recency
#         self.session_graphs = {}

#     def build_graph(self, session_data):
#         """
#         Builds a session graph for each user.
#         Output: {userId: {from_query: {to_query: weighted_value}}}
#         """
#         for session in session_data:
#             user_id = session.user_id  # Updated to use attribute, not dictionary key
#             transitions = session.transitions  # Same here

#             if user_id not in self.session_graphs:
#                 self.session_graphs[user_id] = {}

#             for trans in transitions:
#                 from_q = trans.from_query  # Adjust this based on your class definition
#                 to_q = trans.to     # Adjust this based on your class definition
#                 base_weight = trans.weight
#                 delta_t = trans.time_difference

#                 # Apply recency decay
#                 recency_weight = base_weight * math.exp(-self.lambda_recency * delta_t)

#                 if from_q not in self.session_graphs[user_id]:
#                     self.session_graphs[user_id][from_q] = {}
#                 self.session_graphs[user_id][from_q][to_q] = recency_weight

#         return self.session_graphs


# class SessionGraphEmbedder:
#     def __init__(self, model_name='paraphrase-MiniLM-L6-v2'):
#         self.model = SentenceTransformer(model_name)

#     def embed_session_graphs(self, session_data):
#         """
#         Converts each session graph into a single embedding vector per user.
#         Output: {userId: session_embedding_vector}
#         """
#         session_vectors = {}

#         for session in session_data:
#             user_id = session.user_id  # Access user_id attribute
#             queries = {q.id: q.text for q in session.queries}  # Assuming 'queries' is a list of QueryNode objects
#             transitions = session.transitions  # Assuming 'transitions' is a list of Transition objects

#             weighted_embeddings = []
#             total_weight = 0

#             for trans in transitions:
#                 from_id = trans.from_query  # Adjust based on actual attribute name
#                 to_id = trans.to     # Adjust based on actual attribute name
#                 weight = trans.weight

#                 from_text = queries.get(from_id)
#                 to_text = queries.get(to_id)

#                 if from_text and to_text:
#                     # Embed both queries
#                     from_vec = self.model.encode(from_text)
#                     to_vec = self.model.encode(to_text)

#                     # Average them to represent the transition
#                     transition_vec = (from_vec + to_vec) / 2.0
#                     weighted_embeddings.append(transition_vec * weight)
#                     total_weight += weight

#             if weighted_embeddings:
#                 session_vector = np.sum(weighted_embeddings, axis=0) / total_weight
#                 session_vectors[user_id] = session_vector

#         return session_vectors

# class UserProfileEmbedder:
#     def __init__(self, model_name='paraphrase-MiniLM-L6-v2'):
#         self.model = SentenceTransformer(model_name)

#     def embed_users(self, user_data):
#         """
#         Embeds user profile data (interests + favorite brands).
#         Output: {userId: embedding_vector}
#         """
#         user_embeddings = {}
        
#         for user in user_data:
#             user_id = user.id  # Accessing user ID correctly from UserProfile instance
            
#             # Safely access preferences, check if preferences is not None
#             brands = user.preferences.favorite_brands if user.preferences else []
#             interests = user.preferences.interests if user.preferences else []
            
#             # Combine favorite brands and interests into a single profile text
#             profile_text = " ".join(brands + interests)
            
#             # Create embedding for profile text
#             embedding = self.model.encode(profile_text)
            
#             # Store the embedding in the dictionary
#             user_embeddings[user_id] = embedding
            
#         return user_embeddings

# class ContextFusion:
#     def __init__(self, alpha=0.5):
#         """
#         alpha: balance between session and user profile embeddings
#                (0.5 means equal weight)
#         """
#         self.alpha = alpha

#     def fuse(self, session_embeddings, user_embeddings):
#         """
#         Returns: {userId: fused_vector}
#         """
#         fused_embeddings = {}

#         for user_id in session_embeddings:
#             if user_id in user_embeddings:
#                 session_vec = session_embeddings[user_id]
#                 user_vec = user_embeddings[user_id]
#                 # Weighted average
#                 fused = self.alpha * session_vec + (1 - self.alpha) * user_vec
#                 fused_embeddings[user_id] = fused
#             else:
#                 # fallback: use session vector only
#                 fused_embeddings[user_id] = session_embeddings[user_id]

#         return fused_embeddings
