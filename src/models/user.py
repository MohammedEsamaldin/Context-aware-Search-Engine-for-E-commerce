import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import List, Optional
import random

class Preferences(BaseModel):
    favorite_brands: List[str] = Field(default_factory=list, alias="favoriteBrands")
    interests: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True

class UserProfile(BaseModel):
    id: str = Field(..., alias="userId")
    name: str
    email: str
    preferences: Optional[Preferences] = None
    last_login: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="lastLogin")
    embedding: Optional[List[float]] = Field(None, alias="userEmbedding")

    class Config:
        populate_by_name = True

    @classmethod
    def create(
        cls,
        user_id: str,
        name: str,
        email: str,
        favorite_brands: Optional[List[str]] = None,
        interests: Optional[List[str]] = None,
        embedding: Optional[List[float]] = None
    ) -> "UserProfile":
        """Create user profile with specified ID"""
        from src.db.firebase_client import db
        
        # Handle preferences
        preferences = None
        if favorite_brands or interests:
            preferences = Preferences(
                favoriteBrands=favorite_brands or [],
                interests=interests or []
            )

        # Build user data
        user_data = {
            "userId": user_id,
            "name": name,
            "email": email,
            "lastLogin": datetime.now(timezone.utc),
            "embedding": embedding
        }
        if preferences:
            user_data["preferences"] = preferences.model_dump(by_alias=True)

        # Save to Firestore
        db.collection("Users").document(user_id).set(user_data)
        
        return cls(
            userId=user_id,
            name=name,
            email=email,
            preferences=preferences,
            lastLogin=datetime.now(timezone.utc)
        )
    
    @classmethod
    def create_with_generated_id(
        cls,
        name: str,
        email: str,
        favorite_brands: Optional[List[str]] = None,
        interests: Optional[List[str]] = None
    ) -> "UserProfile":
        """Public method for auto-generated IDs"""
        user_id = cls.generate_user_id()
        return cls.create(
            user_id=user_id,
            name=name,
            email=email,
            favorite_brands=favorite_brands,
            interests=interests
        )
    
    @classmethod
    def generate_user_id(cls) -> str:
        """Generate unique Uxxxxx ID with collision check"""
        from src.db.firebase_client import db
        
        max_attempts = 10
        for _ in range(max_attempts):
            # Generate 5-digit number with leading zeros
            number = random.randint(0, 99999)
            candidate_id = f"U{number:05d}"
            
            # Check if ID exists in Firestore
            doc_ref = db.collection("Users").document(candidate_id)
            if not doc_ref.get().exists:
                return candidate_id
        
        raise ValueError("Failed to generate unique user ID after 10 attempts")
    

    @classmethod
    def get(cls, user_id: str) -> "UserProfile":
        """Improved with explicit field mapping"""
        from src.db.firebase_client import db
        
        doc_ref = db.collection("Users").document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise ValueError(f"User {user_id} not found")
            
        data = doc.to_dict()
        
        # Explicitly map Firestore fields to model aliases
        return cls(
            userId=user_id,  # Ensures ID matches document ID
            name=data.get("name"),
            email=data.get("email"),
            preferences=Preferences(**data["preferences"]) if "preferences" in data else None,
            lastLogin=data.get("lastLogin"),
            userEmbedding=data.get("embedding")  # Direct map using Firestore field name
        )
    
    @classmethod
    def get_all(cls) -> list["UserProfile"]:
        """Load all user profiles from Firestore"""
        from src.db.firebase_client import db
        
        users_ref = db.collection("Users")
        docs = users_ref.stream()
        
        return [cls(
            # Map document ID to product_id alias
            **{"userId": doc.id, **doc.to_dict()}
        ) for doc in docs]

    def save(self):
        """Full profile update"""
        from src.db.firebase_client import db
        
        db.collection("Users").document(self.id).set(
            self.model_dump(by_alias=True, exclude_unset=True),
            merge=True
        )

    def update_preferences(
        self,
        favorite_brands: Optional[List[str]] = None,
        interests: Optional[List[str]] = None
    ):
        """Update or clear preferences"""
        from src.db.firebase_client import db
        from google.cloud import firestore
        
        if favorite_brands is None and interests is None:
            # Clear preferences
            self.preferences = None
            db.collection("Users").document(self.id).update({
                "preferences": firestore.DELETE_FIELD
            })
        else:
            # Update preferences
            self.preferences = Preferences(
                favoriteBrands=favorite_brands or self.preferences.favorite_brands if self.preferences else [],
                interests=interests or self.preferences.interests if self.preferences else []
            )
            db.collection("Users").document(self.id).update({
                "preferences": self.preferences.model_dump(by_alias=True)
            })

    def update_last_login(self):
        """Update last login timestamp"""
        from src.db.firebase_client import db
        
        self.last_login = datetime.now(timezone.utc)
        db.collection("Users").document(self.id).update({
            "lastLogin": self.last_login
        })

    def update_embedding(self, embedding: List[float]):
        from src.db.firebase_client import db
        
        # Update local instance
        self.embedding = embedding
        
        # Update Firestore document
        db.collection("Users").document(self.id).update({
            "embedding": embedding  # Direct field name match in Firestore
        })

# if __name__ == "__main__":
#     # U78644
#     user = UserProfile.get('U78644')
#     print(user)