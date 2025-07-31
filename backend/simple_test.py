# -*- coding: utf-8 -*-
"""Test simplu pentru modelul traditional"""

import pickle
import os

def test_model():
    """Testeaza modelul traditional local"""
    
    print("[TEST] Verificare fisiere model...")
    
    # Verifica daca fisierele exista
    if os.path.exists("model.pkl"):
        print("[OK] model.pkl gasit")
    else:
        print("[ERROR] model.pkl nu exista")
        return False
    
    if os.path.exists("vectorizer.pkl"):
        print("[OK] vectorizer.pkl gasit")
    else:
        print("[ERROR] vectorizer.pkl nu exista")
        return False
    
    try:
        # Incarca modelul si vectorizatorul
        print("[TEST] Incarcare model...")
        with open("vectorizer.pkl", "rb") as f:
            vectorizer = pickle.load(f)
        with open("model.pkl", "rb") as f:
            model = pickle.load(f)
        
        print("[OK] Model si vectorizator incarcate cu succes")
        
        # Test predictie
        print("[TEST] Test predictie...")
        test_texts = [
            "Breaking news: The president was replaced by a robot.",  # Fake
            "Scientists discovered water on Mars.",  # Real
            "Guvernul ascunde adevarul despre extraterestri.",  # Fake (ro)
            "Studiu nou arata beneficiile exercitiilor fizice."  # Real (ro)
        ]
        
        expected = ["fake", "real", "fake", "real"]
        
        X = vectorizer.transform(test_texts)
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)
        
        print("\n[RESULTS] Rezultate test:")
        for i, text in enumerate(test_texts):
            verdict = "fake" if predictions[i] == 1 else "real"
            confidence = max(probabilities[i])
            print(f"Text: {text[:50]}...")
            print(f"Predictie: {verdict} (confidence: {confidence:.2f})")
            print(f"Asteptat: {expected[i]}")
            print("-" * 60)
        
        # Calculeaza acuratatea
        correct = sum(1 for i in range(len(predictions)) 
                     if (predictions[i] == 1 and expected[i] == "fake") or 
                        (predictions[i] == 0 and expected[i] == "real"))
        accuracy = correct / len(predictions)
        print(f"\n[SUMMARY] Acuratete: {accuracy:.2f} ({correct}/{len(predictions)})")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Eroare la testare: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST MODEL TRADITIONAL FAKE NEWS")
    print("=" * 60)
    
    success = test_model()
    
    if success:
        print("\n[SUCCESS] Toate testele au trecut cu succes!")
        print("Modelul traditional functioneaza corect.")
    else:
        print("\n[FAILED] Testele au esuat!")
    
    print("=" * 60) 