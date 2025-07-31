# -*- coding: utf-8 -*-
"""
Versiune simplificată a aplicației Flask pentru detectarea fake news
Folosește doar modelul tradițional fără dependințe complexe
"""

import json
import pickle
import os
from datetime import datetime

# Simulare Flask pentru test
class MockFlask:
    def __init__(self):
        self.routes = {}
    
    def route(self, path, methods=['GET']):
        def decorator(func):
            self.routes[path] = func
            return func
        return decorator
    
    def run(self, host='localhost', port=5000, debug=False):
        print(f"[MOCK] Flask app ar rula pe {host}:{port}")
        print(f"[MOCK] Endpoint-uri disponibile: {list(self.routes.keys())}")

# Mock pentru a simula aplicația
app = MockFlask()

# Încarcă modelul tradițional
def load_traditional_model():
    try:
        if os.path.exists("vectorizer.pkl") and os.path.exists("model.pkl"):
            with open("vectorizer.pkl", "rb") as f:
                vectorizer = pickle.load(f)
            with open("model.pkl", "rb") as f:
                model = pickle.load(f)
            print("[OK] Model tradițional încărcat cu succes!")
            return vectorizer, model
        else:
            print("[ERROR] Fisierele model nu exista!")
            return None, None
    except Exception as e:
        print(f"[ERROR] Nu s-a putut încărca modelul: {e}")
        return None, None

vectorizer, model = load_traditional_model()

# Modurile de analiză disponibile
ANALYSIS_MODES = {
    'traditional': {
        'name': 'Model Tradițional',
        'description': 'TF-IDF + Logistic Regression - Rapid și eficient',
        'accuracy': 'Medie',
        'speed': 'Foarte rapidă',
        'languages': ['en', 'parțial multilingv']
    },
    'hybrid': {
        'name': 'Analiză Hibridă (DEMO)',
        'description': 'Combină AI și ML - Necesită configurare avansată',
        'accuracy': 'Foarte mare',
        'speed': 'Medie',
        'languages': ['ro', 'en', 'fr', 'es', 'de', 'it']
    },
    'ai_only': {
        'name': 'Doar AI (DEMO)',
        'description': 'OpenAI GPT + Google Perspective - Necesită API keys',
        'accuracy': 'Mare',
        'speed': 'Rapidă',
        'languages': ['6+ limbi majore']
    },
    'ml_only': {
        'name': 'Doar ML (DEMO)', 
        'description': 'mBERT + Sentence Transformers - Necesită modele pre-antrenate',
        'accuracy': 'Mare',
        'speed': 'Rapidă',
        'languages': ['ro', 'en', 'fr', 'es', 'de', 'it']
    }
}

@app.route('/analysis-modes')
def analysis_modes():
    """Returnează modurile de analiză disponibile"""
    return ANALYSIS_MODES

@app.route('/system-status')
def system_status():
    """Returnează status-ul sistemului"""
    return {
        'system_status': 'operational',
        'ai_services': {
            'enabled': False,
            'openai': False,
            'perspective': False
        },
        'ml_models': {
            'enabled': False,
            'sentence_transformer': False,
            'mbert': False,
            'traditional': model is not None
        },
        'supported_languages': ['en', 'ro'],
        'timestamp': datetime.now().isoformat(),
        'mode': 'simplified'
    }

@app.route('/predict', methods=['POST'])
def predict():
    """Simulare predicție"""
    if not model or not vectorizer:
        return {'error': 'Model tradițional nu este disponibil'}
    
    # În versiunea reală, ar primi JSON data
    # Pentru demo, returnăm rezultate mock
    
    # Simulare analiză pentru diferite moduri
    mock_results = {
        'traditional': {
            'verdict': 'fake',
            'confidence': 0.75,
            'explanation': 'Model tradițional: Analiză TF-IDF + Logistic Regression',
            'analysis_mode': 'traditional',
            'detected_language': 'en',
            'processing_time': 0.05
        },
        'hybrid': {
            'verdict': 'fake',
            'confidence': 0.89,
            'explanation': 'Analiza hibridă AI+ML: Consens între multiple sisteme',
            'analysis_mode': 'hybrid',
            'detected_language': 'en',
            'processing_time': 2.3,
            'risk_level': 'high',
            'ai_ml_agreement': True,
            'consensus_strength': 'strong'
        },
        'ai_only': {
            'verdict': 'fake',
            'confidence': 0.91,
            'explanation': 'AI Analysis: OpenAI GPT detectează limbaj manipulativ și afirmații false',
            'analysis_mode': 'ai_only',
            'detected_language': 'en',
            'processing_time': 1.8
        },
        'ml_only': {
            'verdict': 'fake',
            'confidence': 0.82,
            'explanation': 'ML Analysis: mBERT + Sentence Transformers detectează similaritate cu știri false cunoscute',
            'analysis_mode': 'ml_only',
            'detected_language': 'en',
            'processing_time': 1.2
        }
    }
    
    # Pentru demo, returnăm rezultatul pentru traditional
    return mock_results['traditional']

def test_prediction(text, mode='traditional'):
    """Testează predicția cu modelul real"""
    if not model or not vectorizer:
        return {'error': 'Model nu este disponibil'}
    
    try:
        # Transformă textul
        X = vectorizer.transform([text])
        pred = model.predict(X)[0]
        proba = model.predict_proba(X)[0]
        
        verdict = "fake" if pred == 1 else "real"
        confidence = float(max(proba))
        
        return {
            'verdict': verdict,
            'confidence': confidence,
            'explanation': f'Model tradițional: Probabilitate {verdict} = {confidence:.2f}',
            'analysis_mode': mode,
            'detected_language': 'auto',
            'processing_time': 0.01
        }
    except Exception as e:
        return {'error': f'Eroare predicție: {str(e)}'}

def main():
    print("=" * 60)
    print("FAKE NEWS DETECTION - VERSIUNE SIMPLIFICATĂ")
    print("=" * 60)
    
    # Test sistem
    print("\n[TEST] Verificare status sistem...")
    status = system_status()
    print(f"Status: {status['system_status']}")
    print(f"Model tradițional: {'✓' if status['ml_models']['traditional'] else '✗'}")
    
    # Test moduri disponibile
    print("\n[TEST] Moduri de analiză disponibile:")
    modes = analysis_modes()
    for key, mode in modes.items():
        print(f"  {key}: {mode['name']}")
    
    # Test predicție
    print("\n[TEST] Test predicție model tradițional...")
    test_texts = [
        "Breaking news: The president was replaced by a robot.",
        "Scientists discovered water on Mars using rovers.",
        "Guvernul ascunde adevărul despre extraterestri.",
        "Studiu nou arată beneficiile exercițiilor fizice."
    ]
    
    for text in test_texts:
        result = test_prediction(text)
        if 'error' not in result:
            print(f"Text: {text[:50]}...")
            print(f"Rezultat: {result['verdict']} (confidență: {result['confidence']:.2f})")
        else:
            print(f"Eroare: {result['error']}")
        print("-" * 40)
    
    # Simulare pornire server
    print("\n[INFO] Pentru a porni server-ul real:")
    print("1. Rezolvă problemele de import Python")
    print("2. Rulează: python app.py")
    print("3. Accesează: http://localhost:5000")
    
    app.run(port=5000, debug=True)

if __name__ == "__main__":
    main() 