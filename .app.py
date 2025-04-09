import os
from fastapi import FastAPI, HTTPException
import firebase_admin
from firebase_admin import credentials, firestore

# Import your models from src/models using absolute imports.
from src.models import UserProfile, Preferences, Product, QueryLog, RetrievalResults, Session, QueryNode, Transition, UnifiedEmbedding

# Initialize Firebase Admin using your service account file.
# Replace "path/to/serviceAccountKey.json" with the actual path.
cred_path = "config/firebase_cart_admin.json"
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI(title="Context-Aware Search Engine Backend")

# --- User Profile Endpoints ---
@app.post("/users", response_model=UserProfile)
def create_user(user: UserProfile):
    doc_ref = db.collection("users").document(user.id)
    doc_ref.set(user.dict(by_alias=True))
    return user

@app.get("/users/{user_id}", response_model=UserProfile)
def get_user(user_id: str):
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfile(**doc.to_dict())

@app.put("/users/{user_id}", response_model=UserProfile)
def update_user(user_id: str, user: UserProfile):
    doc_ref = db.collection("users").document(user_id)
    doc_ref.update(user.dict(by_alias=True))
    updated_doc = doc_ref.get()
    return UserProfile(**updated_doc.to_dict())

@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    db.collection("users").document(user_id).delete()
    return {"detail": "User deleted"}

# --- Product Endpoints ---
@app.post("/products", response_model=Product)
def create_product(product: Product):
    doc_ref = db.collection("products").document(product.id)
    doc_ref.set(product.dict(by_alias=True))
    return product

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    doc_ref = db.collection("products").document(product_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**doc.to_dict())

@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: str, product: Product):
    doc_ref = db.collection("products").document(product_id)
    doc_ref.update(product.dict(by_alias=True))
    updated_doc = doc_ref.get()
    return Product(**updated_doc.to_dict())

@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    db.collection("products").document(product_id).delete()
    return {"detail": "Product deleted"}

# --- QueryLog Endpoints ---
@app.post("/query_logs", response_model=QueryLog)
def create_query_log(query_log: QueryLog):
    doc_ref = db.collection("query_logs").document(query_log.id)
    doc_ref.set(query_log.dict(by_alias=True))
    return query_log

@app.get("/query_logs/{log_id}", response_model=QueryLog)
def get_query_log(log_id: str):
    doc_ref = db.collection("query_logs").document(log_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="QueryLog not found")
    return QueryLog(**doc.to_dict())

@app.put("/query_logs/{log_id}", response_model=QueryLog)
def update_query_log(log_id: str, query_log: QueryLog):
    doc_ref = db.collection("query_logs").document(log_id)
    doc_ref.update(query_log.dict(by_alias=True))
    updated_doc = doc_ref.get()
    return QueryLog(**updated_doc.to_dict())

@app.delete("/query_logs/{log_id}")
def delete_query_log(log_id: str):
    db.collection("query_logs").document(log_id).delete()
    return {"detail": "QueryLog deleted"}

# --- UnifiedEmbedding Endpoints ---
@app.post("/unified_embeddings", response_model=UnifiedEmbedding)
def create_unified_embedding(embedding: UnifiedEmbedding):
    doc_ref = db.collection("unified_embeddings").document(embedding.id)
    doc_ref.set(embedding.dict(by_alias=True))
    return embedding

@app.get("/unified_embeddings/{embedding_id}", response_model=UnifiedEmbedding)
def get_unified_embedding(embedding_id: str):
    doc_ref = db.collection("unified_embeddings").document(embedding_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="UnifiedEmbedding not found")
    return UnifiedEmbedding(**doc.to_dict())

@app.put("/unified_embeddings/{embedding_id}", response_model=UnifiedEmbedding)
def update_unified_embedding(embedding_id: str, embedding: UnifiedEmbedding):
    doc_ref = db.collection("unified_embeddings").document(embedding_id)
    doc_ref.update(embedding.dict(by_alias=True))
    updated_doc = doc_ref.get()
    return UnifiedEmbedding(**updated_doc.to_dict())

@app.delete("/unified_embeddings/{embedding_id}")
def delete_unified_embedding(embedding_id: str):
    db.collection("unified_embeddings").document(embedding_id).delete()
    return {"detail": "UnifiedEmbedding deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
