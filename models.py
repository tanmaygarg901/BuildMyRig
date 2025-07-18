from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union

class BuildRequest(BaseModel):
    budget: float = Field(..., gt=0, description="Budget in USD")
    brand_preferences: Optional[Dict[str, str]] = Field(default={}, description="Brand preferences by component type")
    use_case: str = Field(..., description="Use case: gaming, workstation, etc.")

class PartResponse(BaseModel):
    id: int
    name: str
    category: str
    price: float
    performance_score: int
    compatibility_tags: Dict
    brand: str
    hardware_brand: Optional[str] = None
    specifications: Dict

class BuildResponse(BaseModel):
    parts: List[PartResponse]
    total_price: float
    performance_score: float
    budget_allocation: Dict[str, float]
    compatibility_status: str
    bang_for_buck_score: float

class RecommendationResponse(BaseModel):
    builds: List[BuildResponse]
    message: str
    request_summary: Dict
