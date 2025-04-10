import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import json

class Product(BaseModel):
    id: str = Field(..., alias="productId")
    title: str = Field(..., alias="productTitle")
    description: Optional[str] = Field(None, alias="productDescription")
    bulletPoint: Optional[str] = Field(None, alias="productBulletPoint")
    brand: Optional[str] = Field(None, alias="productBrand")
    color: Optional[str] = Field(None, alias="productColor")
    locale: str = Field(..., alias="productLocale")
    embedding: Optional[List[float]] = None

    class Config:
        populate_by_name = True
    
    @field_validator('embedding', mode='before')
    def parse_embedding(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return value
    
    @classmethod
    def load(cls, product_id: str) -> "Product":
        """Retrieve product from Firestore by ID"""
        from src.db.firebase_client import db
        
        doc_ref = db.collection("Products").document(product_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise ValueError(f"Product {product_id} not found")
            
        # Combine document ID with data
        product_data = doc.to_dict()
        product_data["product_id"] = doc.id  # Map Firestore ID to product_id alias
        
        return cls(**product_data)
    
    @classmethod
    def load_all(cls) -> list["Product"]:
        """Get all products from Firestore"""
        from src.db.firebase_client import db
        
        products_ref = db.collection("Products")
        docs = products_ref.stream()
        
        return [cls(
            # Map document ID to product_id alias
            **{"productId": doc.id, **doc.to_dict()}
        ) for doc in docs]

    @classmethod
    def load_batch(cls, limit: int = 100) -> list["Product"]:
        """Get products in batches"""
        from src.db.firebase_client import db
        
        products_ref = db.collection("Products").limit(limit)
        docs = products_ref.stream()
        
        return [cls(**doc.to_dict()) for doc in docs]
    
    def update_embedding(self, embedding: List[float]):
        """
        Update the product's embedding in Firestore.
        
        Args:
            embedding: List of floats representing the new embedding
        """
        from src.db.firebase_client import db
        
        # Update local instance
        self.embedding = embedding
        
        # Update Firestore document
        db.collection("Products").document(self.id).update({
            "embedding": embedding  # Direct field name match in Firestore
        })