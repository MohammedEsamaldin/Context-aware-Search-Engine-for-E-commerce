from src.utils.normalization import normalize_scores
# import math

def fuse_candidates(bm25_candidates, vector_candidates, beta=0.5, top_n=None):
    """
    Merges BM25 and vector retrieval candidate lists in a single list using a weighted sum.

    Params:
    - bm25_candidates (list): List of dicts, containing keys "productId" and "score" for BM25 candidates.
    - vector_candidates (list): List of dicts, containing keys "productId" and "score" for vector candidates.
    - beta (float): Weight (0 <= beta <= 1) to balance BM25 and vector scores.
    - top_n (int): if provided, return only the top N candidates.

    Returns:
    - list: Final sorted candidate list.

    Raises:
    - ValueError: If any of the input lists is empty.
    - ValueError: If missing or invalid score field in candidates
    - ValueError: If beta is not between 0 and 1.
    - ValueError: If top_n is negative.
    """
    if not bm25_candidates or not vector_candidates:
        raise ValueError("Input lists cannot be empty.")
    
    for cand in bm25_candidates:
        if "score" not in cand:
            raise ValueError("Missing 'score' field in BM25 candidates.")
    for cand in vector_candidates:
        if "score" not in cand:
            raise ValueError("Missing 'score' field in vector candidates.")

    if not (0 <= beta <= 1):
        raise ValueError("Beta must be between 0 and 1.")

    if top_n is not None and top_n < 0:
        raise ValueError("top_n must be non-negative.")

    ## Normalise BM25 scores.
    bm25_scores = [cand["score"] for cand in bm25_candidates]
    norm_bm25 = normalize_scores(bm25_scores, mode='min-max')
    for idx, cand in enumerate(bm25_candidates):
        cand["norm_BM25"] = norm_bm25[idx]
    
    ## Normalise vector (cosine similarity) scores.
    vector_scores = [cand["score"] for cand in vector_candidates]
    norm_vector = normalize_scores(vector_scores, mode='min-max')
    for idx, cand in enumerate(vector_candidates):
        cand["norm_Vector"] = norm_vector[idx]
    
    ## Merge candidates by productId.
    merged = {}
    for cand in bm25_candidates:
        pid = cand["productId"]
        merged[pid] = {
            "productId": pid,
            "norm_BM25": cand.get("norm_BM25", 0.0),
            "norm_Vector": 0.0  # default if missing in vector_candidates
        }
    
    for cand in vector_candidates:
        pid = cand["productId"]
        if pid in merged:
            merged[pid]["norm_Vector"] = cand.get("norm_Vector", 0.0)
        else:
            merged[pid] = {
                "productId": pid,
                "norm_BM25": 0.0,  # default if missing in bm25_candidates
                "norm_Vector": cand.get("norm_Vector", 0.0)
            }
    
    # Compute final scores (get up to 3 decimal places)
    final_candidates = []
    for pid, scores in merged.items():
        final_score = beta * scores["norm_BM25"] + (1 - beta) * scores["norm_Vector"]
        final_candidates.append({
            "productId": pid,
            "score": round(final_score, 3)
        })
    
    # Sort in descending order of finalScore.
    final_candidates.sort(key=lambda x: x["score"], reverse=True)
    
    # Truncate to top_n if specified.
    if top_n is not None:
        final_candidates = final_candidates[:top_n]
    
    return final_candidates