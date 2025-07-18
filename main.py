from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import uvicorn
import os

from database import Database
from recommendation_engine import RecommendationEngine
from models import BuildRequest, RecommendationResponse, PartResponse

# Initialize FastAPI app
app = FastAPI(
    title="BuildMyRig - PC Part Recommender",
    description="A backend API for recommending optimized PC builds based on budget and preferences",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

# Initialize database and recommendation engine
db = Database()
recommendation_engine = RecommendationEngine(db)

@app.get("/")
async def serve_frontend():
    """Serve the frontend application"""
    return FileResponse("frontend/index.html")

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Welcome to BuildMyRig API",
        "version": "1.0.0",
        "endpoints": {
            "POST /recommend": "Get PC build recommendations",
            "GET /parts": "Get all available parts",
            "GET /parts/{category}": "Get parts by category",
            "GET /health": "Health check endpoint"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "BuildMyRig API is running"}

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: BuildRequest):
    """
    Get PC build recommendations based on budget, brand preferences, and use case.
    
    Expected JSON input:
    {
        "budget": 1000,
        "brand_preferences": {"cpu": "AMD", "gpu": "NVIDIA"},
        "use_case": "gaming"
    }
    """
    try:
        # Get recommendations from the engine
        builds = recommendation_engine.get_recommendations(
            budget=request.budget,
            brand_preferences=request.brand_preferences,
            use_case=request.use_case
        )
        
        if not builds:
            raise HTTPException(
                status_code=404,
                detail="No valid builds found within the specified budget and preferences"
            )
        
        # Create response
        response = RecommendationResponse(
            builds=builds,
            message=f"Found {len(builds)} optimized build(s) for your {request.use_case} setup",
            request_summary={
                "budget": request.budget,
                "brand_preferences": request.brand_preferences,
                "use_case": request.use_case
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/parts", response_model=List[PartResponse])
async def get_all_parts():
    """Get all available PC parts"""
    try:
        parts = db.get_all_parts()
        return [PartResponse(**part) for part in parts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching parts: {str(e)}")

@app.get("/parts/{category}", response_model=List[PartResponse])
async def get_parts_by_category(
    category: str, 
    brand: str = None, 
    limit: int = 50, 
    offset: int = 0, 
    sort_by: str = "performance_score",
    sort_order: str = "desc"
):
    """
    Get parts by category with optional brand filtering, pagination, and sorting.
    
    Categories: cpu, gpu, motherboard, ram, storage, psu, case
    Sort by: performance_score, price, name
    Sort order: asc, desc
    """
    try:
        valid_categories = ["cpu", "gpu", "motherboard", "ram", "storage", "psu", "case"]
        if category not in valid_categories:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            )
        
        valid_sort_fields = ["performance_score", "price", "name"]
        if sort_by not in valid_sort_fields:
            sort_by = "performance_score"
            
        if sort_order not in ["asc", "desc"]:
            sort_order = "desc"
            
        if limit > 100:
            limit = 100  # Cap at 100 parts per request
            
        # Convert brand parameter to tuple format if provided
        brand_tuple = None
        if brand:
            if category in ["cpu", "gpu"]:
                brand_tuple = ("any", brand)
            else:
                brand_tuple = (brand, "any")
        
        parts = db.get_parts_by_category_paginated(
            category, brand_tuple, limit, offset, sort_by, sort_order
        )
        
        if not parts:
            raise HTTPException(
                status_code=404,
                detail=f"No parts found for category '{category}'" + (f" with brand '{brand}'" if brand else "")
            )
        
        return [PartResponse(**part) for part in parts]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching parts: {str(e)}")

@app.get("/stats")
async def get_database_stats():
    """Get database statistics"""
    try:
        all_parts = db.get_all_parts()
        
        # Count by category
        category_counts = {}
        brand_counts = {}
        
        for part in all_parts:
            category = part["category"]
            brand = part["brand"]
            
            category_counts[category] = category_counts.get(category, 0) + 1
            brand_counts[brand] = brand_counts.get(brand, 0) + 1
        
        return {
            "total_parts": len(all_parts),
            "categories": category_counts,
            "brands": brand_counts,
            "price_range": {
                "min": min(part["price"] for part in all_parts),
                "max": max(part["price"] for part in all_parts)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000)
