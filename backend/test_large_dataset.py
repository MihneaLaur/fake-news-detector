#!/usr/bin/env python3
"""
Test pentru noul model mare cu 2000 articole
"""

import requests
import json

def login_for_testing(base_url):
    """Face login pentru a putea testa API-ul"""
    # Încearcă să se înregistreze cu un utilizator de test
    register_data = {
        "username": "test_user",
        "password": "test123",
        "email": "test@example.com"
    }
    
    session = requests.Session()  # Folosește sesiune pentru cookies
    
    try:
        # Încearcă înregistrarea
        response = session.post(f"{base_url}/register", json=register_data)
        if response.status_code not in [200, 409]:  # 409 = user already exists
            print(f"⚠️  Înregistrare eșuată: {response.status_code}")
        
        # Încearcă login-ul
        login_data = {
            "username": "test_user", 
            "password": "test123"
        }
        
        response = session.post(f"{base_url}/login", json=login_data)
        if response.status_code == 200:
            print("✅ Login reușit pentru testare")
            return session
        else:
            print(f"❌ Login eșuat: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Eroare la login: {e}")
        return None

def test_api_with_large_dataset():
    """Testează API-ul cu noul model mare"""
    base_url = "http://localhost:5000"
    
    # Fă login pentru testare
    session = login_for_testing(base_url)
    if not session:
        print("❌ Nu s-a putut face login pentru testare!")
        return
    
    # Test cases
    test_cases = [
        {
            "text": "URGENT: Government hides secret microchips in vaccines",
            "expected": "fake",
            "description": "Știre fake cu cuvinte cheie conspirative"
        },
        {
            "text": "Research study shows benefits of new medical treatment",
            "expected": "real", 
            "description": "Știre reală cu cuvinte academice"
        },
        {
            "text": "BREAKING: Aliens control world governments from underground",
            "expected": "fake",
            "description": "Știre fake cu teorii conspirației"
        },
        {
            "text": "University publishes findings on climate change solutions",
            "expected": "real",
            "description": "Știre reală academică"
        },
        {
            "text": "SHOCKING: 5G towers cause coronavirus infections worldwide",
            "expected": "fake", 
            "description": "Știre fake cu teorii 5G"
        }
    ]
    
    print("=" * 80)
    print("TESTARE API CU NOUL MODEL MARE (2000 ARTICOLE)")
    print("=" * 80)
    
    # Testează fiecare mod
    modes = ["traditional", "ml_only", "hybrid"]
    
    for mode in modes:
        print(f"\n🧪 TESTEZ MODUL: {mode.upper()}")
        print("-" * 60)
        
        correct_predictions = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                response = session.post(  # Folosește sesiunea cu login
                    f"{base_url}/predict",
                    json={
                        "text": test_case["text"],
                        "mode": mode
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Determină verdictul
                    verdict = result.get("verdict", "unknown")
                    confidence = result.get("confidence", 0)
                    
                    # Verifică dacă predicția este corectă
                    is_correct = verdict == test_case["expected"]
                    if is_correct:
                        correct_predictions += 1
                    
                    status_emoji = "✅" if is_correct else "❌"
                    verdict_emoji = "🚨" if verdict == "fake" else "✅"
                    
                    print(f"{i}. {status_emoji} {test_case['description']}")
                    print(f"   Text: {test_case['text'][:50]}...")
                    print(f"   Predicție: {verdict_emoji} {verdict.upper()} (confidență: {confidence:.3f})")
                    print(f"   Așteptat: {test_case['expected'].upper()}")
                    
                    # Afișează detalii specifice modului
                    if "source" in result:
                        source = result.get("source", "unknown")
                        print(f"   Model: {source}")
                    
                    print()
                    
                else:
                    print(f"{i}. ❌ Eroare HTTP {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                print(f"{i}. ❌ Eroare: {str(e)}")
        
        accuracy = correct_predictions / total_tests
        print(f"📊 REZULTATE {mode.upper()}:")
        print(f"   - Predicții corecte: {correct_predictions}/{total_tests}")
        print(f"   - Acuratețe: {accuracy:.1%}")
        print()

def test_system_status():
    """Testează status-ul sistemului"""
    try:
        response = requests.get("http://localhost:5000/system-status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print("🔧 STATUS SISTEM:")
            print(f"   - AI Services: {'✅' if status['ai_services']['enabled'] else '❌'}")
            print(f"   - ML Models: {'✅' if status['ml_models']['enabled'] else '❌'}")
            print(f"   - Traditional Model: {'✅' if status['ml_models']['traditional'] else '❌'}")
            print(f"   - Limbi suportate: {len(status['supported_languages'])}")
            return True
        else:
            print(f"❌ Backend nu răspunde: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Eroare conectare backend: {e}")
        return False

def main():
    print("🚀 ÎNCEPE TESTAREA NOULUI MODEL MARE")
    
    # Verifică status sistem
    if not test_system_status():
        print("❌ Backend-ul nu este disponibil!")
        return
    
    print()
    
    # Testează API
    test_api_with_large_dataset()
    
    print("🎉 TESTARE COMPLETĂ!")

if __name__ == "__main__":
    main() 