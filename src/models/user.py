from datetime import datetime
from pydantic import BaseModel, Field


class Preferences(BaseModel):
    favorite_brands: list[str] = Field(..., alias="favoriteBrands")
    interests: list[str]


class UserProfile(BaseModel):
    id: str = Field(..., alias="userId")
    name: str
    email: str
    preferences: Preferences
    last_login: datetime = Field(..., alias="lastLogin")
