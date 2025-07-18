#!/usr/bin/env python3
"""Test script to verify brand filtering works correctly"""

import json
from recommendation_engine import RecommendationEngine
from database import Database

def test_brand_filtering():
    """Test brand filtering for different scenarios"""
    
    # Initialize the database and engine
    db = Database()
    engine = RecommendationEngine(db)
    
    print("Testing brand filtering...")
    print("=" * 50)
    
    # Test 1: AMD GPU preference
    print("\n1. Testing AMD GPU preference...")
    budget = 1500
    use_case = 'gaming'
    brand_preferences = {
        'gpu': 'AMD'
    }
    
    try:
        recommendations = engine.get_recommendations(budget, brand_preferences, use_case)
        
        if recommendations and len(recommendations) > 0:
            # Get the GPU from the first recommended build
            gpu = None
            for part in recommendations[0].parts:
                if part.category == 'gpu':
                    gpu = part
                    break
            
            if gpu:
                gpu_name = gpu.name
                gpu_brand = gpu.brand
                gpu_hardware_brand = gpu.hardware_brand
                gpu_price = gpu.price
                
                print(f"Recommended GPU: {gpu_name}")
                print(f"Brand: {gpu_brand}")
                print(f"Hardware Brand: {gpu_hardware_brand}")
                print(f"Price: ${gpu_price}")
                
                # Verify it's an AMD GPU
                if gpu_hardware_brand == 'AMD':
                    print("✓ SUCCESS: AMD GPU correctly recommended")
                else:
                    print("✗ FAILURE: Non-AMD GPU recommended")
            else:
                print("✗ FAILURE: No GPU found in recommendation")
        else:
            print("✗ FAILURE: No recommendations found")
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
    
    # Test 2: NVIDIA GPU preference
    print("\n2. Testing NVIDIA GPU preference...")
    budget = 1500
    use_case = 'gaming'
    brand_preferences = {
        'gpu': 'NVIDIA'
    }
    
    try:
        recommendations = engine.get_recommendations(budget, brand_preferences, use_case)
        
        if recommendations and len(recommendations) > 0:
            # Get the GPU from the first recommended build
            gpu = None
            for part in recommendations[0].parts:
                if part.category == 'gpu':
                    gpu = part
                    break
            
            if gpu:
                gpu_name = gpu.name
                gpu_brand = gpu.brand
                gpu_hardware_brand = gpu.hardware_brand
                gpu_price = gpu.price
                
                print(f"Recommended GPU: {gpu_name}")
                print(f"Brand: {gpu_brand}")
                print(f"Hardware Brand: {gpu_hardware_brand}")
                print(f"Price: ${gpu_price}")
                
                # Verify it's an NVIDIA GPU
                if gpu_hardware_brand == 'NVIDIA':
                    print("✓ SUCCESS: NVIDIA GPU correctly recommended")
                else:
                    print("✗ FAILURE: Non-NVIDIA GPU recommended")
            else:
                print("✗ FAILURE: No GPU found in recommendation")
        else:
            print("✗ FAILURE: No recommendations found")
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
    
    # Test 3: AMD CPU preference
    print("\n3. Testing AMD CPU preference...")
    budget = 1500
    use_case = 'gaming'
    brand_preferences = {
        'cpu': 'AMD'
    }
    
    try:
        recommendations = engine.get_recommendations(budget, brand_preferences, use_case)
        
        if recommendations and len(recommendations) > 0:
            # Get the CPU from the first recommended build
            cpu = None
            for part in recommendations[0].parts:
                if part.category == 'cpu':
                    cpu = part
                    break
            
            if cpu:
                cpu_name = cpu.name
                cpu_brand = cpu.brand
                cpu_hardware_brand = cpu.hardware_brand
                cpu_price = cpu.price
                
                print(f"Recommended CPU: {cpu_name}")
                print(f"Brand: {cpu_brand}")
                print(f"Hardware Brand: {cpu_hardware_brand}")
                print(f"Price: ${cpu_price}")
                
                # Verify it's an AMD CPU
                if cpu_hardware_brand == 'AMD':
                    print("✓ SUCCESS: AMD CPU correctly recommended")
                else:
                    print("✗ FAILURE: Non-AMD CPU recommended")
            else:
                print("✗ FAILURE: No CPU found in recommendation")
        else:
            print("✗ FAILURE: No recommendations found")
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
    
    # Test 4: Intel CPU preference
    print("\n4. Testing Intel CPU preference...")
    budget = 1500
    use_case = 'gaming'
    brand_preferences = {
        'cpu': 'Intel'
    }
    
    try:
        recommendations = engine.get_recommendations(budget, brand_preferences, use_case)
        
        if recommendations and len(recommendations) > 0:
            # Get the CPU from the first recommended build
            cpu = None
            for part in recommendations[0].parts:
                if part.category == 'cpu':
                    cpu = part
                    break
            
            if cpu:
                cpu_name = cpu.name
                cpu_brand = cpu.brand
                cpu_hardware_brand = cpu.hardware_brand
                cpu_price = cpu.price
                
                print(f"Recommended CPU: {cpu_name}")
                print(f"Brand: {cpu_brand}")
                print(f"Hardware Brand: {cpu_hardware_brand}")
                print(f"Price: ${cpu_price}")
                
                # Verify it's an Intel CPU
                if cpu_hardware_brand == 'Intel':
                    print("✓ SUCCESS: Intel CPU correctly recommended")
                else:
                    print("✗ FAILURE: Non-Intel CPU recommended")
            else:
                print("✗ FAILURE: No CPU found in recommendation")
        else:
            print("✗ FAILURE: No recommendations found")
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("Brand filtering tests completed!")

if __name__ == "__main__":
    test_brand_filtering()
