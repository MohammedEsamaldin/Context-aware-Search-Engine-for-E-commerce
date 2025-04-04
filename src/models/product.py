from pydantic import BaseModel, Field
from typing import List, Optional

class Product(BaseModel):
    id: str = Field(..., alias="product_id")
    title: str = Field(..., alias="product_title")
    description: Optional[str] = Field(None, alias="product_description")
    bullet_point: Optional[str] = Field(None, alias="product_bullet_point")
    brand: str = Field(..., alias="product_brand")
    color: Optional[str] = Field(None, alias="product_color")
    locale: str = Field(..., alias="product_locale")
    embedding: Optional[List[float]] = None

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "B079VKKJN7",  # Use FIELD NAMES here
                "title": "11 Degrees de los Hombres Playera con Logo, Ne.",
                "description": "Esta playera con el logo de la marca Carrier d...",
                "bullet_point": "11 Degrees Negro Playera con logo\nA estrenar ...",
                "brand": "11 Degrees",
                "color": "Negro",
                "locale": "es"
            }
        }