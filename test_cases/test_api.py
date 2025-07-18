#!/usr/bin/env python3
"""Test API functionality"""

import requests
import json

def test_api():
    # Test the API endpoint
    try:
        response = requests.get('http://localhost:8000/parts/gpu?limit=3&sort_by=performance_score&sort_order=desc')
        if response.status_code == 200:
            parts = response.json()
            print(f'API returned {len(parts)} parts')
            for i, part in enumerate(parts[:3]):  # Show first 3 parts
                print(f'{i+1}. {part["name"]}: Performance {part["performance_score"]}, Price ${part["price"]}')
        else:
            print(f'API returned status code: {response.status_code}')
            print(f'Response: {response.text}')
    except Exception as e:
        print(f'Error calling API: {e}')

if __name__ == "__main__":
    test_api()
