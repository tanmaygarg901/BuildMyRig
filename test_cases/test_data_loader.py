#!/usr/bin/env python3
"""
Test script to verify CSV data loading functionality
"""

import os
import sqlite3
from csv_loader import CSVDataLoader
from database import Database

def test_csv_loader():
    """Test the CSV data loader"""
    print("Testing CSV Data Loader...")
    
    # Remove existing database if it exists
    if os.path.exists("buildmyrig.db"):
        os.remove("buildmyrig.db")
        print("Removed existing database")
    
    # Test CSV loader directly
    loader = CSVDataLoader()
    
    try:
        loader.load_all_data()
        print("CSV data loaded successfully!")
        
        # Check database contents
        conn = sqlite3.connect("buildmyrig.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT category, COUNT(*) FROM parts GROUP BY category")
        results = cursor.fetchall()
        
        print("\nDatabase contents:")
        total_parts = 0
        for category, count in results:
            print(f"  {category}: {count} parts")
            total_parts += count
        
        print(f"Total parts: {total_parts}")
        
        # Test a few sample parts
        print("\nSample parts:")
        cursor.execute("SELECT name, category, price, performance_score FROM parts LIMIT 5")
        for row in cursor.fetchall():
            print(f"  {row[0]} ({row[1]}): ${row[2]} - Performance: {row[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_database_integration():
    """Test database integration"""
    print("\nTesting Database Integration...")
    
    # Test database class
    db = Database()
    
    # Test getting parts by category
    cpus = db.get_parts_by_category("cpu")
    gpus = db.get_parts_by_category("gpu")
    
    print(f"Found {len(cpus)} CPUs")
    print(f"Found {len(gpus)} GPUs")
    
    if cpus:
        print(f"Sample CPU: {cpus[0]['name']} - ${cpus[0]['price']}")
    
    if gpus:
        print(f"Sample GPU: {gpus[0]['name']} - ${gpus[0]['price']}")

def test_recommendation_engine():
    """Test recommendation engine with real data"""
    print("\nTesting Recommendation Engine...")
    
    from recommendation_engine import RecommendationEngine
    
    db = Database()
    engine = RecommendationEngine(db)
    
    # Test with a moderate budget
    budget = 1500.0
    brand_preferences = {}
    use_case = "gaming"
    
    try:
        recommendations = engine.get_recommendations(budget, brand_preferences, use_case)
        
        print(f"Generated {len(recommendations)} recommendations for ${budget} gaming build")
        
        for i, build in enumerate(recommendations, 1):
            print(f"\nBuild {i}:")
            print(f"  Total Price: ${build.total_price}")
            print(f"  Performance Score: {build.performance_score}")
            print(f"  Bang-for-Buck: {build.bang_for_buck_score}")
            print(f"  Parts:")
            for part in build.parts:
                print(f"    - {part.name} (${part.price})")
    
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_csv_loader()
    test_database_integration()
    test_recommendation_engine()
