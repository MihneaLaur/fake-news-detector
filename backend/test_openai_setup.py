#!/usr/bin/env python3
"""
Script pentru testarea configurației OpenAI API
"""

from openai import OpenAI
import requests
import json
from config import OPENAI_API_KEY, ENABLE_OPENAI, DEFAULT_MODEL

def test_openai_connection():
    """Testează conexiunea la OpenAI API"""
    
    print("🔑 TESTARE CONFIGURARE OPENAI")
    print("=" * 50)
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY nu este setat în config.py")
        print("📋 Pentru a configura:")
        print("   1. Mergi la: https://platform.openai.com/api-keys")
        print("   2. Creează API key nou")
        print("   3. Copiază cheia în config.py: OPENAI_API_KEY = 'sk-proj-...'")
        print("   4. Setează ENABLE_OPENAI = True")
        return False
    
    if not ENABLE_OPENAI:
        print("❌ ENABLE_OPENAI este False în config.py")
        print("📋 Setează ENABLE_OPENAI = True pentru a activa OpenAI")
        return False
    
    print(f"🔧 Cheie API: {OPENAI_API_KEY[:20]}...")
    print(f"🤖 Model: {DEFAULT_MODEL}")
    print(f"✅ ENABLE_OPENAI: {ENABLE_OPENAI}")
    
    # Setează clientul OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    try:
        # Test 1: Verifică validitatea cheii
        print("\n🧪 Test 1: Verificare cheie API...")
        
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! This is a test message."}
            ],
            max_tokens=10,
            temperature=0.3
        )
        
        print("✅ Cheia API funcționează!")
        print(f"📝 Răspuns test: {response.choices[0].message.content}")
        
        # Test 2: Verifică billing
        print("\n🧪 Test 2: Verificare credit disponibil...")
        
        # Încearcă să obțină informații despre utilizare
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Check usage (poate să nu funcționeze pentru toate conturile)
        try:
            usage_response = requests.get(
                'https://api.openai.com/v1/usage',
                headers=headers,
                timeout=10
            )
            if usage_response.status_code == 200:
                usage_data = usage_response.json()
                print("✅ Credit verificat cu succes")
            else:
                print("⚠️  Nu s-au putut verifica creditele (normal pentru unele conturi)")
        except:
            print("⚠️  Nu s-au putut verifica creditele (normal)")
        
        return True
        
    except Exception as e:
        error_str = str(e).lower()
        if 'authentication' in error_str or 'invalid' in error_str:
            print("❌ Cheia API nu este validă!")
            print("📋 Verifică că:")
            print("   - Cheia începe cu 'sk-proj-' sau 'sk-'")
            print("   - Nu are spații la început/sfârșit")
            print("   - Nu a fost revocată în dashboard")
            return False
        elif 'rate limit' in error_str:
            print("❌ Limita de rate depășită!")
            print("📋 Încearcă din nou în câteva minute")
            return False
        elif 'quota' in error_str or 'insufficient' in error_str:
            print("❌ Credit insuficient!")
            print("📋 Pentru a adăuga credit:")
            print("   1. Mergi la: https://platform.openai.com/account/billing")
            print("   2. Adaugă minimum $5")
            print("   3. Așteaptă 5-10 minute pentru procesare")
            return False
        else:
            print(f"❌ Eroare: {e}")
            return False

def test_fake_news_detection():
    """Testează detectarea fake news cu OpenAI"""
    
    if not OPENAI_API_KEY or not ENABLE_OPENAI:
        print("\n⚠️  OpenAI nu este configurat - saltez testarea fake news")
        return
    
    print("\n🕵️ TESTARE DETECTARE FAKE NEWS CU OPENAI")
    print("=" * 50)
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    test_cases = [
        {
            "text": "URGENT: Government hides secret microchips in vaccines!",
            "expected": "fake",
            "description": "Știre fake conspirativă"
        },
        {
            "text": "University research shows benefits of regular exercise.",
            "expected": "real",
            "description": "Știre reală academică"
        },
        {
            "text": "BREAKING: Aliens control world governments from underground!",
            "expected": "fake", 
            "description": "Teorii conspirației"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Text: {test_case['text']}")
        
        prompt = f"""Analyze the following text and determine if it's fake news.
        Consider: credible sources, verifiable facts, sensational language, contradictions.
        
        Text: "{test_case['text']}"
        
        Respond in JSON:
        {{
            "is_fake": true/false,
            "confidence": 0.0-1.0,
            "reasoning": "detailed explanation"
        }}"""
        
        try:
            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at detecting fake news and media analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            print(f"   🤖 OpenAI răspuns: {content[:100]}...")
            
            # Încearcă să parseze JSON
            try:
                result = json.loads(content)
                is_fake = result.get('is_fake', False)
                confidence = result.get('confidence', 0)
                verdict = "FAKE" if is_fake else "REAL"
                
                expected_verdict = test_case['expected'].upper()
                status = "✅" if verdict == expected_verdict else "❌"
                
                print(f"   {status} Verdict: {verdict} (confidență: {confidence:.2f})")
                print(f"   📊 Așteptat: {expected_verdict}")
                
            except json.JSONDecodeError:
                print("   ⚠️  Răspuns nu este JSON valid, dar API-ul funcționează")
                
        except Exception as e:
            print(f"   ❌ Eroare: {e}")

def show_cost_estimate():
    """Afișează estimarea costurilor"""
    
    print("\n💰 ESTIMARE COSTURI OPENAI")
    print("=" * 50)
    print("📊 Prețuri gpt-3.5-turbo:")
    print("   - Input: $0.0010 / 1K tokens")
    print("   - Output: $0.0020 / 1K tokens")
    print()
    print("📈 Estimări pentru analiza fake news:")
    print("   - 1 analiză text = ~100-200 tokens = $0.0002-0.0005")
    print("   - 100 analize = ~$0.02-0.05")
    print("   - 1000 analize = ~$0.20-0.50")
    print("   - 10000 analize = ~$2-5")
    print()
    print("💡 Cu $5 credit poți face:")
    print("   - ~1000-2500 analize fake news")
    print("   - Suficient pentru testarea completă a tezei")

if __name__ == "__main__":
    print("🚀 CONFIGURARE ȘI TESTARE OPENAI API")
    
    # Test configurare
    if test_openai_connection():
        print("\n🎉 OpenAI configurat cu succes!")
        test_fake_news_detection()
    else:
        print("\n📋 OpenAI nu este încă configurat complet")
    
    show_cost_estimate()
    
    print("\n📝 PASII URMĂTORI:")
    print("1. Obține cheia API de la https://platform.openai.com/api-keys")
    print("2. Adaugă credit ($5 minim) la https://platform.openai.com/account/billing")
    print("3. Actualizează config.py cu cheia ta")
    print("4. Setează ENABLE_OPENAI = True")
    print("5. Rulează din nou acest script pentru testare") 