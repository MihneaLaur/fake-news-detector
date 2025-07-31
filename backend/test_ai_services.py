# -*- coding: utf-8 -*-
"""
Script pentru testarea serviciilor AI configurate
"""

import sys
import os
import json
import requests

# Adaugă directorul curent la path pentru importuri
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import *
    print("✅ Config.py încărcat cu succes!")
except ImportError as e:
    print(f"❌ Eroare la încărcarea config.py: {e}")
    sys.exit(1)

def test_perspective_api():
    """Testează Google Perspective API"""
    print("\n🔍 Testez Google Perspective API...")
    
    if not ENABLE_PERSPECTIVE:
        print("⚠️ Perspective API este dezactivat în config")
        return False
        
    if not GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY nu este configurat")
        print("💡 Pentru a obține API key gratuit:")
        print("   1. Vizitează: https://developers.google.com/codelabs/setup-perspective-api")
        print("   2. Completează formularul pentru acces")
        print("   3. Creează API key în Google Cloud Console")
        return False
    
    url = f'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={GOOGLE_API_KEY}'
    
    data = {
        'requestedAttributes': {
            'TOXICITY': {},
            'SEVERE_TOXICITY': {},
            'IDENTITY_ATTACK': {},
            'INSULT': {},
            'PROFANITY': {},
            'THREAT': {}
        },
        'comment': {'text': 'This is a test comment for fake news detection.'},
        'doNotStore': True
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
                toxicity = result['attributeScores']['TOXICITY']['summaryScore']['value']
                print(f"✅ Perspective API funcționează!")
                print(f"   Toxicitate test: {toxicity:.3f}")
                return True
            else:
                print(f"⚠️ Răspuns neașteptat: {result}")
                return False
        else:
            print(f"❌ Eroare HTTP {response.status_code}: {response.text}")
            if response.status_code == 400:
                print("💡 Verifică că API key-ul este valid și are permisiuni pentru Perspective API")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la conectarea la Perspective API: {e}")
        return False

def test_openai_api():
    """Testează OpenAI API"""
    print("\n🔍 Testez OpenAI API...")
    
    if not ENABLE_OPENAI:
        print("⚠️ OpenAI API este dezactivat în config")
        return False
        
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY nu este configurat")
        print("💰 OpenAI API necesită plată minimă de $5")
        print("💡 Pentru teză, recomand doar Perspective API (gratuit) + ML models")
        return False
    
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=10
        )
        
        print("✅ OpenAI API funcționează!")
        return True
        
    except Exception as e:
        print(f"❌ Eroare OpenAI: {e}")
        return False

def test_ml_models():
    """Testează modelele ML locale"""
    print("\n🔍 Testez modelele ML locale...")
    
    if not ENABLE_ML_MODELS:
        print("⚠️ ML Models sunt dezactivate în config")
        return False
    
    try:
        from ml_analyzer import MLAnalyzer
        analyzer = MLAnalyzer()
        
        # Test model tradițional
        if analyzer.traditional_model and analyzer.vectorizer:
            print("✅ Model tradițional (TF-IDF + LogisticRegression) încărcat")
        else:
            print("⚠️ Model tradițional nu este disponibil")
        
        # Test Sentence Transformer
        if analyzer.sentence_model:
            print("✅ Sentence Transformer încărcat")
        else:
            print("⚠️ Sentence Transformer nu este disponibil")
            
        # Test mBERT
        if analyzer.classifier_model:
            print("✅ mBERT classifier încărcat")
        else:
            print("⚠️ mBERT classifier nu este disponibil")
            
        return True
        
    except Exception as e:
        print(f"❌ Eroare la testarea modelelor ML: {e}")
        return False

def main():
    print("=" * 60)
    print("TEST SERVICII AI - SISTEM HIBRID FAKE NEWS DETECTION")
    print("=" * 60)
    
    # Verifică configurația
    print(f"\n📋 Configurație actuală:")
    print(f"   ENABLE_OPENAI: {ENABLE_OPENAI}")
    print(f"   ENABLE_PERSPECTIVE: {ENABLE_PERSPECTIVE}")
    print(f"   ENABLE_ML_MODELS: {ENABLE_ML_MODELS}")
    print(f"   OPENAI_API_KEY: {'✅ Configurat' if OPENAI_API_KEY else '❌ Neconfigurator'}")
    print(f"   GOOGLE_API_KEY: {'✅ Configurat' if GOOGLE_API_KEY else '❌ Neconfigurator'}")
    
    # Testează serviciile
    results = {
        'perspective': test_perspective_api(),
        'openai': test_openai_api() if ENABLE_OPENAI else None,
        'ml_models': test_ml_models()
    }
    
    print("\n" + "=" * 60)
    print("REZULTATE FINALE:")
    print("=" * 60)
    
    if results['perspective']:
        print("✅ AI Services: PARȚIAL ACTIV (Perspective API)")
    elif results['openai']:
        print("✅ AI Services: COMPLET ACTIV (OpenAI + Perspective)")
    else:
        print("❌ AI Services: INACTIV")
        
    if results['ml_models']:
        print("✅ ML Models: ACTIV")
    else:
        print("❌ ML Models: INACTIV")
    
    # Recomandări
    print("\n💡 RECOMANDĂRI:")
    if not results['perspective'] and not GOOGLE_API_KEY:
        print("🆓 OBȚINE PERSPECTIVE API GRATUIT:")
        print("   1. https://developers.google.com/codelabs/setup-perspective-api")
        print("   2. Completează formularul (menționează cercetare academică)")
        print("   3. Configurează API key în config.py")
        print("   4. Restart backend")
        
    if results['perspective'] and results['ml_models']:
        print("🎉 SISTEMUL HIBRID FUNCȚIONEAZĂ!")
        print("   - Perspective API pentru toxicitate")
        print("   - mBERT + Sentence Transformers pentru semantică")
        print("   - Model tradițional ca backup")
        print("   - Perfect pentru teză de licență!")

if __name__ == "__main__":
    main() 