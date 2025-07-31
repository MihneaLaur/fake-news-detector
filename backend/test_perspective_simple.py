#!/usr/bin/env python3
"""
Test simplu pentru Perspective API - doar TOXICITY
"""

import requests
import json
from config import GOOGLE_PERSPECTIVE_API_KEY

def test_simple_perspective():
    """Test simplu cu doar TOXICITY"""
    
    print("🧪 TEST SIMPLU PERSPECTIVE API (doar TOXICITY)")
    print("=" * 60)
    
    url = f'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={GOOGLE_PERSPECTIVE_API_KEY}'
    
    test_cases = [
        "This is a normal comment about news.",
        "URGENT: Government conspiracy exposed!!!",
        "You are stupid and I hate you!",
        "Această știre pare suspectă și fake.",
        "Breaking: Aliens control the world!"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. {text}")
        
        data = {
            'requestedAttributes': {
                'TOXICITY': {}
            },
            'comment': {'text': text},
            'doNotStore': True
        }
        
        try:
            response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                result = response.json()
                
                if 'attributeScores' in result:
                    toxicity = result['attributeScores']['TOXICITY']['summaryScore']['value']
                    
                    if toxicity < 0.3:
                        status = "✅ NORMAL"
                    elif toxicity < 0.7:
                        status = "🟡 MODERAT"
                    else:
                        status = "🚨 TOXIC"
                    
                    print(f"   {status} - Toxicitate: {toxicity:.3f}")
                    
                    # Pentru fake news detection
                    fake_suspicion = toxicity * 0.7
                    if fake_suspicion > 0.3:
                        print(f"   🔍 Posibil fake news (suspicion: {fake_suspicion:.3f})")
                else:
                    print(f"   ❌ Format neașteptat: {result}")
            else:
                print(f"   ❌ Eroare {response.status_code}: {response.text[:150]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    test_simple_perspective() 