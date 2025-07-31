#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplificat pentru antrenarea modelului cu datasetul extins
"""

import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from datetime import datetime
import os

def load_extended_dataset():
    """Încarcă datasetul extins"""
    try:
        with open("simple_large_dataset_extended.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Fișierul simple_large_dataset_extended.json nu a fost găsit!")
        return None
    except Exception as e:
        print(f"❌ Eroare la încărcarea datasetului: {e}")
        return None

def train_enhanced_model():
    """Antrenează modelul îmbunătățit"""
    print("🚀 ANTRENARE MODEL ÎMBUNĂTĂȚIT")
    print("=" * 40)
    
    # Încarcă datasetul
    print("📂 Încărcare dataset...")
    dataset = load_extended_dataset()
    if dataset is None:
        return False
    
    # Pregătește datele
    print("🔄 Pregătire date...")
    texts = [item['text'] for item in dataset]
    labels = [item['label'] for item in dataset]
    
    print(f"📊 Total: {len(texts)} texte")
    fake_count = sum(labels)
    real_count = len(labels) - fake_count
    print(f"📊 Fake: {fake_count} ({fake_count/len(labels)*100:.1f}%)")
    print(f"📊 Real: {real_count} ({real_count/len(labels)*100:.1f}%)")
    
    # Împarte în train/test
    print("📊 Împărțire train/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"   Train: {len(X_train)}")
    print(f"   Test: {len(X_test)}")
    
    # Creează vectorizer îmbunătățit
    print("🔤 Creează vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=3000,
        stop_words='english',
        ngram_range=(1, 3),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True
    )
    
    # Vectorizare
    print("🔄 Vectorizare...")
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print(f"   Vocabular: {len(vectorizer.get_feature_names_out())}")
    
    # Antrenare
    print("🤖 Antrenare...")
    classifier = LogisticRegression(
        max_iter=2000,
        C=1.0,
        random_state=42,
        class_weight='balanced'
    )
    classifier.fit(X_train_vec, y_train)
    
    # Evaluare
    print("📈 Evaluare...")
    y_pred = classifier.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✅ Acuratețe: {accuracy:.3f} ({accuracy*100:.1f}%)")
    
    # Backup model vechi
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if os.path.exists("model.pkl"):
        os.rename("model.pkl", f"model_backup_{timestamp}.pkl")
        print(f"💾 Backup: model_backup_{timestamp}.pkl")
    if os.path.exists("vectorizer.pkl"):
        os.rename("vectorizer.pkl", f"vectorizer_backup_{timestamp}.pkl")
        print(f"💾 Backup: vectorizer_backup_{timestamp}.pkl")
    
    # Salvează noul model
    print("💾 Salvare model nou...")
    with open("model.pkl", "wb") as f:
        pickle.dump(classifier, f)
    with open("vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    
    print(f"✅ Model salvat cu acuratețe: {accuracy:.3f}")
    
    # Test rapid
    print("\n🧪 TEST RAPID:")
    test_cases = [
        ("Leading experts discover revolutionary method that guarantees results.", "fake"),
        ("The Department of Health released new guidelines today.", "real"),
        ("Anonymous sources reveal shocking truth about common activity.", "fake"),
        ("City Council approved the budget yesterday.", "real")
    ]
    
    correct = 0
    for text, expected in test_cases:
        pred = classifier.predict(vectorizer.transform([text]))[0]
        pred_label = "fake" if pred == 1 else "real"
        
        if pred_label == expected:
            print(f"✅ {text[:40]}... → {pred_label}")
            correct += 1
        else:
            print(f"❌ {text[:40]}... → {pred_label} (expected {expected})")
    
    print(f"\nTest rapid: {correct}/{len(test_cases)} corecte")
    
    return accuracy >= 0.8

def update_dataset():
    """Actualizează datasetul principal"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Backup original
        if os.path.exists("simple_large_dataset.json"):
            os.rename("simple_large_dataset.json", f"simple_large_dataset_original_{timestamp}.json")
            print(f"💾 Original salvat: simple_large_dataset_original_{timestamp}.json")
        
        # Copiază versiunea extinsă
        if os.path.exists("simple_large_dataset_extended.json"):
            os.rename("simple_large_dataset_extended.json", "simple_large_dataset.json")
            print("✅ Dataset principal actualizat")
            return True
    except Exception as e:
        print(f"❌ Eroare actualizare dataset: {e}")
    
    return False

def main():
    """Funcția principală"""
    try:
        success = train_enhanced_model()
        
        if success:
            print("\n🎉 ANTRENARE REUȘITĂ!")
            
            if update_dataset():
                print("✅ Dataset actualizat!")
            
            print("\n" + "=" * 40)
            print("🚀 MODEL ÎMBUNĂTĂȚIT GATA!")
            print("=" * 40)
            
            return True
        else:
            print("\n❌ ANTRENARE EȘUATĂ!")
            return False
            
    except Exception as e:
        print(f"❌ EROARE: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 