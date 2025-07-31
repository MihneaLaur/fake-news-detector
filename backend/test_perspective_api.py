#!/usr/bin/env python3
"""
Test direct pentru Perspective API cu cheia furnizată
"""

import requests
import json
from config import GOOGLE_PERSPECTIVE_API_KEY

def test_perspective_api():
    """Testează Perspective API cu diferite texte"""
    
    print("🧪 TESTEZ PERSPECTIVE API")
    print("=" * 50)
    print(f"Cheie API: {GOOGLE_PERSPECTIVE_API_KEY[:20]}...")
    
    url = f'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={GOOGLE_PERSPECTIVE_API_KEY}'
    
    # Test cases pentru diferite niveluri de toxicitate
    test_cases = [
        {
            "text": "This is a normal, respectful comment about politics.",
            "expected": "low toxicity",
            "description": "Text normal"
        },
        {
            "text": "URGENT: Government hides secret microchips in vaccines!!!",
            "expected": "medium toxicity", 
            "description": "Știre fake conspirativă"
        },
        {
            "text": "You are stupid and should not exist!",
            "expected": "high toxicity",
            "description": "Text toxic"
        },
        {
            "text": "Această cercetare universitară arată beneficiile noului tratament medical.",
            "expected": "low toxicity",
            "description": "Text academic românesc"
        },
        {
            "text": "BREAKING: Aliens are controlling the government from underground bases!",
            "expected": "medium toxicity",
            "description": "Teorii conspirației"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Text: {test_case['text'][:60]}...")
        
        data = {
            'requestedAttributes': {
                'TOXICITY': {},
                'SEVERE_TOXICITY': {},
                'IDENTITY_ATTACK': {},
                'INSULT': {},
                'PROFANITY': {},
                'THREAT': {},
                'UNSUBSTANTIAL': {},
                'SPAM': {}
            },
            'comment': {'text': test_case['text']},
            'doNotStore': True,
            'languages': ['en', 'ro']
        }
        
        try:
            response = requests.post(
                url, 
                data=json.dumps(data), 
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'attributeScores' in result:
                    scores = {}
                    for attr, data in result['attributeScores'].items():
                        scores[attr.lower()] = data['summaryScore']['value']
                    
                    toxicity = scores.get('toxicity', 0)
                    severe_toxicity = scores.get('severe_toxicity', 0)
                    spam = scores.get('spam', 0)
                    
                    # Interpretare rezultate
                    if toxicity < 0.3:
                        status = "✅ NORMAL"
                    elif toxicity < 0.7:
                        status = "🟡 SUSPECT"
                    else:
                        status = "🚨 TOXIC"
                    
                    print(f"   Rezultat: {status}")
                    print(f"   Toxicitate: {toxicity:.3f}")
                    print(f"   Toxicitate severă: {severe_toxicity:.3f}")
                    print(f"   Spam: {spam:.3f}")
                    print(f"   Așteptat: {test_case['expected']}")
                    
                else:
                    print(f"   ❌ Răspuns neașteptat: {result}")
                    
            else:
                print(f"   ❌ Eroare HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Eroare: {e}")

def test_fake_news_detection():
    """Testează detectarea fake news cu Perspective API"""
    
    print("\n" + "=" * 50)
    print("🕵️ TESTEZ DETECTAREA FAKE NEWS CU PERSPECTIVE")
    print("=" * 50)
    
    fake_news_examples = [
        "URGENT: Scientists discover that drinking water causes cancer!",
        "BREAKING: Government admits aliens control the economy!",
        "SHOCKING: 5G towers are mind control devices confirmed!",
        "Government announces new vaccination program for children.",
        "University research shows benefits of regular exercise.",
        "Climate change study published in Nature journal."
    ]
    
    url = f'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={GOOGLE_PERSPECTIVE_API_KEY}'
    
    for i, text in enumerate(fake_news_examples, 1):
        print(f"\n{i}. {text}")
        
        data = {
            'requestedAttributes': {
                'TOXICITY': {},
                'UNSUBSTANTIAL': {},
                'SPAM': {},
                'ATTACK_ON_AUTHOR': {},
                'ATTACK_ON_COMMENTER': {}
            },
            'comment': {'text': text},
            'doNotStore': True
        }
        
        try:
            response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                result = response.json()
                scores = {}
                for attr, data in result['attributeScores'].items():
                    scores[attr.lower()] = data['summaryScore']['value']
                
                # Calculează scorul de suspiciune pentru fake news
                suspicion_score = (
                    scores.get('unsubstantial', 0) * 0.4 +
                    scores.get('spam', 0) * 0.3 +
                    scores.get('toxicity', 0) * 0.3
                )
                
                if suspicion_score > 0.6:
                    verdict = "🚨 SUSPECT FAKE"
                elif suspicion_score > 0.3:
                    verdict = "🟡 NECESITĂ VERIFICARE"
                else:
                    verdict = "✅ PARE AUTENTIC"
                
                print(f"   {verdict} (scor: {suspicion_score:.3f})")
                print(f"   Unsubstantial: {scores.get('unsubstantial', 0):.3f}")
                print(f"   Spam: {scores.get('spam', 0):.3f}")
                
            else:
                print(f"   ❌ Eroare: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Eroare: {e}")

if __name__ == "__main__":
    test_perspective_api()
    test_fake_news_detection()
    print("\n🎉 TESTARE PERSPECTIVE API COMPLETĂ!") 