#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pentru antrenarea din nou a modelului cu datasetul extins
"""

import json
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from datetime import datetime
import os

def load_extended_dataset():
    """Încarcă datasetul extins"""
    try:
        with open("simple_large_dataset_extended.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Fișierul simple_large_dataset_extended.json nu a fost găsit!")
        print("Rulez mai întâi extend_dataset.py")
        return None
    except Exception as e:
        print(f"❌ Eroare la încărcarea datasetului: {e}")
        return None

def prepare_data(dataset):
    """Pregătește datele pentru antrenare"""
    texts = [item['text'] for item in dataset]
    labels = [item['label'] for item in dataset]
    
    print(f"📊 Total texte: {len(texts)}")
    print(f"📊 Fake news: {sum(labels)} ({sum(labels)/len(labels)*100:.1f}%)")
    print(f"📊 Real news: {len(labels)-sum(labels)} ({(len(labels)-sum(labels))/len(labels)*100:.1f}%)")
    
    return texts, labels

def create_enhanced_vectorizer():
    """Creează un vectorizer îmbunătățit"""
    return TfidfVectorizer(
        max_features=3000,          # Mărit pentru mai mult vocabular
        stop_words='english',       # Elimină cuvintele comune în engleză
        ngram_range=(1, 3),         # Include unigrame, bigrame și trigrame
        min_df=2,                   # Cuvântul trebuie să apară în cel puțin 2 documente
        max_df=0.95,                # Exclude cuvintele care apar în peste 95% din documente
        sublinear_tf=True,          # Folosește log scaling pentru frecvențe
        norm='l2',                  # Normalizare L2
        lowercase=True,             # Convertește în minuscule
        token_pattern=r'\b[a-zA-Z]{2,}\b'  # Doar cuvinte cu minimum 2 litere
    )

def create_enhanced_classifier():
    """Creează un clasificator îmbunătățit"""
    return LogisticRegression(
        max_iter=2000,              # Mărit pentru convergență
        C=1.0,                      # Regularizare optimă
        random_state=42,            # Pentru reproducibilitate
        class_weight='balanced',    # Balansează clasele
        solver='liblinear',         # Solver potrivit pentru datasets mici-medii
        penalty='l2'                # Regularizare L2
    )

def train_enhanced_model():
    """Antrenează modelul îmbunătățit"""
    print("🚀 ANTRENARE MODEL ÎMBUNĂTĂȚIT PENTRU FAKE NEWS")
    print("=" * 60)
    
    # Încarcă datasetul
    print("📂 Încărcare dataset extins...")
    dataset = load_extended_dataset()
    if dataset is None:
        return False
    
    # Pregătește datele
    print("🔄 Pregătire date...")
    texts, labels = prepare_data(dataset)
    
    # Împarte în train/test
    print("📊 Împărțire în train/test (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"   Train: {len(X_train)} exemple")
    print(f"   Test: {len(X_test)} exemple")
    
    # Creează și antrenează vectorizer-ul
    print("🔤 Creează vectorizer îmbunătățit...")
    vectorizer = create_enhanced_vectorizer()
    
    print("🔄 Vectorizare texte...")
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print(f"   Vocabular: {len(vectorizer.get_feature_names_out())} cuvinte")
    print(f"   Matrice train: {X_train_vec.shape}")
    print(f"   Matrice test: {X_test_vec.shape}")
    
    # Antrenează modelul
    print("🤖 Antrenare clasificator îmbunătățit...")
    classifier = create_enhanced_classifier()
    classifier.fit(X_train_vec, y_train)
    
    # Evaluare pe setul de test
    print("📈 Evaluare pe setul de test...")
    y_pred = classifier.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✅ REZULTATE ANTRENARE:")
    print(f"   Acuratețe: {accuracy:.3f} ({accuracy*100:.1f}%)")
    
    # Raport detaliat
    print("\n📊 RAPORT CLASIFICARE:")
    report = classification_report(y_test, y_pred, target_names=['Real', 'Fake'])
    print(report)
    
    # Matricea de confuzie
    cm = confusion_matrix(y_test, y_pred)
    print("\n🔍 MATRICE CONFUZIE:")
    print("        Prezis")
    print("       Real Fake")
    print(f"Real   {cm[0][0]:4d} {cm[0][1]:4d}")
    print(f"Fake   {cm[1][0]:4d} {cm[1][1]:4d}")
    
    # Salvează modelul și vectorizer-ul
    print("\n💾 Salvare model îmbunătățit...")
    
    # Backup model vechi
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if os.path.exists("model.pkl"):
        os.rename("model.pkl", f"model_backup_{timestamp}.pkl")
    if os.path.exists("vectorizer.pkl"):
        os.rename("vectorizer.pkl", f"vectorizer_backup_{timestamp}.pkl")
    
    # Salvează noul model
    with open("model.pkl", "wb") as f:
        pickle.dump(classifier, f)
    with open("vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    
    # Salvează metadatele
    metadata = {
        "timestamp": timestamp,
        "dataset_size": len(dataset),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "accuracy": accuracy,
        "vocabulary_size": len(vectorizer.get_feature_names_out()),
        "fake_count": sum(labels),
        "real_count": len(labels) - sum(labels),
        "vectorizer_params": vectorizer.get_params(),
        "classifier_params": classifier.get_params()
    }
    
    with open("enhanced_model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Model salvat cu acuratețe: {accuracy:.3f}")
    print(f"💾 Backup model vechi: model_backup_{timestamp}.pkl")
    print(f"📄 Metadata salvată: enhanced_model_metadata.json")
    
    # Test rapid
    print("\n🧪 TEST RAPID:")
    test_cases = [
        ("Leading experts discover revolutionary method that guarantees amazing results.", "fake"),
        ("The Department of Health released new guidelines based on clinical trials.", "real"),
        ("Anonymous sources reveal shocking truth about everyday activity.", "fake"),
        ("City Council approved the budget with a 7-3 vote yesterday.", "real")
    ]
    
    for text, expected in test_cases:
        pred = classifier.predict(vectorizer.transform([text]))[0]
        pred_label = "fake" if pred == 1 else "real"
        confidence = max(classifier.predict_proba(vectorizer.transform([text]))[0])
        
        status = "✅" if pred_label == expected else "❌"
        print(f"{status} '{text[:50]}...' → {pred_label} ({confidence:.2f})")
    
    return accuracy >= 0.8  # Pragul de succes

def update_simple_large_dataset():
    """Actualizează fișierul principal cu datasetul extins"""
    try:
        # Redenumește originalul
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        os.rename("simple_large_dataset.json", f"simple_large_dataset_original_{timestamp}.json")
        
        # Copiază versiunea extinsă
        os.rename("simple_large_dataset_extended.json", "simple_large_dataset.json")
        
        print(f"✅ Dataset principal actualizat")
        print(f"💾 Original salvat ca: simple_large_dataset_original_{timestamp}.json")
        
        # Actualizează metadata
        with open("simple_model_metadata.json", "r", encoding="utf-8") as f:
            old_metadata = json.load(f)
        
        old_metadata.update({
            "total_articles": 2600,
            "last_updated": timestamp,
            "extended": True,
            "original_size": 2000,
            "added_articles": 600
        })
        
        with open("simple_model_metadata.json", "w", encoding="utf-8") as f:
            json.dump(old_metadata, f, ensure_ascii=False, indent=2)
            
        return True
        
    except Exception as e:
        print(f"❌ Eroare la actualizarea datasetului: {e}")
        return False

def main():
    """Funcția principală"""
    try:
        # Antrenează modelul
        success = train_enhanced_model()
        
        if success:
            print("\n🎉 ANTRENARE REUȘITĂ!")
            
            # Întreabă dacă să actualizez datasetul principal
            print("\n🔄 Actualizez datasetul principal...")
            if update_simple_large_dataset():
                print("✅ Dataset principal actualizat cu succes!")
            else:
                print("⚠️ Datasetul principal nu a fost actualizat")
                
        else:
            print("\n❌ ANTRENARE EȘUATĂ!")
            return False
            
        print("\n" + "=" * 60)
        print("🚀 MODEL ÎMBUNĂTĂȚIT GATA DE FOLOSIRE!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ EROARE: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 