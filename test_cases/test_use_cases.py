#!/usr/bin/env python3
"""
Test script to verify all three use cases work correctly
"""

from database import Database
from recommendation_engine import RecommendationEngine

def test_use_case(use_case, budget=1500.0):
    """Test a specific use case"""
    print(f"\n=== Testing {use_case.upper()} Use Case ===")
    print(f"Budget: ${budget}")
    
    db = Database()
    engine = RecommendationEngine(db)
    
    try:
        recommendations = engine.get_recommendations(budget, {}, use_case)
        
        print(f"Generated {len(recommendations)} recommendations")
        
        for i, build in enumerate(recommendations, 1):
            print(f"\nBuild {i}:")
            print(f"  Total Price: ${build.total_price}")
            print(f"  Performance Score: {build.performance_score}")
            print(f"  Bang-for-Buck: {build.bang_for_buck_score}")
            print(f"  Parts:")
            for part in build.parts:
                if part.category == "ram":
                    # Extract RAM capacity from name
                    import re
                    ram_match = re.search(r'(\d+)\s*GB', part.name, re.IGNORECASE)
                    ram_capacity = ram_match.group(1) + "GB" if ram_match else "Unknown"
                    print(f"    - {part.name} ({ram_capacity}) - ${part.price}")
                else:
                    print(f"    - {part.name} - ${part.price}")
    
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test all three use cases
    test_use_case("gaming")
    test_use_case("workstation")
    test_use_case("general")
    
    print("\n=== Testing with different budgets ===")
    test_use_case("gaming", 800.0)
    test_use_case("workstation", 2000.0)
