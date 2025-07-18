#!/usr/bin/env python3
"""
Test script to verify balanced builds at specific price points
"""

from database import Database
from recommendation_engine import RecommendationEngine

def test_workstation_1400():
    """Test $1400 workstation build for balance"""
    print("=== Testing $1400 Workstation Build ===")
    
    db = Database()
    engine = RecommendationEngine(db)
    
    budget = 1400.0
    use_case = "workstation"
    
    try:
        recommendations = engine.get_recommendations(budget, {}, use_case)
        
        print(f"Generated {len(recommendations)} recommendations for ${budget} {use_case} build")
        
        for i, build in enumerate(recommendations, 1):
            print(f"\nBuild {i}:")
            print(f"  Total Price: ${build.total_price}")
            print(f"  Performance Score: {build.performance_score}")
            print(f"  Bang-for-Buck: {build.bang_for_buck_score}")
            print(f"  Component Breakdown:")
            
            for part in build.parts:
                percentage = (part.price / build.total_price) * 100
                print(f"    {part.category.upper()}: {part.name} - ${part.price} ({percentage:.1f}%)")
                
                # Check for extreme imbalances
                if part.category == "cpu" and percentage > 50:
                    print(f"    ⚠️  WARNING: CPU takes {percentage:.1f}% of budget - too high!")
                elif part.category == "gpu" and percentage < 15:
                    print(f"    ⚠️  WARNING: GPU only gets {percentage:.1f}% of budget - too low!")
                elif part.category == "ram" and percentage < 8:
                    print(f"    ⚠️  WARNING: RAM only gets {percentage:.1f}% of budget - too low!")
    
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        import traceback
        traceback.print_exc()

def test_gaming_800():
    """Test $800 gaming build for balance"""
    print("\n=== Testing $800 Gaming Build ===")
    
    db = Database()
    engine = RecommendationEngine(db)
    
    budget = 800.0
    use_case = "gaming"
    
    try:
        recommendations = engine.get_recommendations(budget, {}, use_case)
        
        print(f"Generated {len(recommendations)} recommendations for ${budget} {use_case} build")
        
        for i, build in enumerate(recommendations, 1):
            print(f"\nBuild {i}:")
            print(f"  Total Price: ${build.total_price}")
            print(f"  Performance Score: {build.performance_score}")
            print(f"  Bang-for-Buck: {build.bang_for_buck_score}")
            print(f"  Component Breakdown:")
            
            for part in build.parts:
                percentage = (part.price / build.total_price) * 100
                print(f"    {part.category.upper()}: {part.name} - ${part.price} ({percentage:.1f}%)")
                
                # Check for extreme imbalances
                if part.category == "cpu" and percentage > 45:
                    print(f"    ⚠️  WARNING: CPU takes {percentage:.1f}% of budget - too high!")
                elif part.category == "gpu" and percentage < 25:
                    print(f"    ⚠️  WARNING: GPU only gets {percentage:.1f}% of budget - too low!")
    
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workstation_1400()
    test_gaming_800()
