# -*- coding: utf-8 -*-
"""
Creează un dataset extins pentru antrenarea modelului de fake news
Cu știri din 2020-2025 în română și engleză
"""

import pandas as pd
import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
from datetime import datetime

# Dataset extins cu știri reale și false din 2020-2025
EXTENDED_DATASET = {
    "fake_news": [
        # 2020 - COVID și politică
        {"text": "Guvernul român ascunde adevărul despre vaccinul COVID-19 care conține cipuri de urmărire", "year": 2020, "lang": "ro"},
        {"text": "Breaking: COVID-19 vaccine contains microchips for population control", "year": 2020, "lang": "en"},
        {"text": "Urgent: 5G towers cause coronavirus infection, scientists confirm cover-up", "year": 2020, "lang": "en"},
        {"text": "Medicii ascund faptul că vitamina C vindecă complet COVID-19", "year": 2020, "lang": "ro"},
        {"text": "Secret document reveals COVID-19 was created in Chinese laboratory", "year": 2020, "lang": "en"},
        
        # 2021 - Continuare pandemie
        {"text": "Masca de protecție îți distruge sistemul imunitar și provoacă cancer", "year": 2021, "lang": "ro"},
        {"text": "Hidden study shows vaccines cause more deaths than COVID-19", "year": 2021, "lang": "en"},
        {"text": "Ivermectin cures COVID instantly but Big Pharma suppresses the truth", "year": 2021, "lang": "en"},
        {"text": "Testele PCR sunt false și creează dependență chimică", "year": 2021, "lang": "ro"},
        {"text": "Bill Gates admits vaccines reduce world population by 90%", "year": 2021, "lang": "en"},
        
        # 2022 - Război și energie
        {"text": "Putin a fost înlocuit cu un robot controlat de oligarhi ruși", "year": 2022, "lang": "ro"},
        {"text": "Ukraine war is staged by Hollywood to distract from vaccine deaths", "year": 2022, "lang": "en"},
        {"text": "Secret NATO documents reveal Romania will be invaded next month", "year": 2022, "lang": "ro"},
        {"text": "Gas prices artificially inflated by secret energy cartel conspiracy", "year": 2022, "lang": "en"},
        {"text": "Zelensky is actually an actor paid by Western governments", "year": 2022, "lang": "en"},
        
        # 2023 - AI și tehnologie
        {"text": "ChatGPT controlează mintea utilizatorilor prin unde electromagnetice", "year": 2023, "lang": "ro"},
        {"text": "AI robots secretly replace world leaders in underground facilities", "year": 2023, "lang": "en"},
        {"text": "TikTok transmite toate datele românilor direct în China", "year": 2023, "lang": "ro"},
        {"text": "Elon Musk's Neuralink chips turn humans into zombie slaves", "year": 2023, "lang": "en"},
        {"text": "Meta's VR headsets steal your dreams and sell them to advertisers", "year": 2023, "lang": "en"},
        
        # 2024 - Alegeri și economie
        {"text": "Alegerile prezidențiale din România sunt controlate de algoritmi AI", "year": 2024, "lang": "ro"},
        {"text": "Secret documents prove all elections are rigged by quantum computers", "year": 2024, "lang": "en"},
        {"text": "Băncile planifică să elimine complet banii fizici până în decembrie", "year": 2024, "lang": "ro"},
        {"text": "Climate change is hoax to implement global government control", "year": 2024, "lang": "en"},
        {"text": "Bitcoin will crash to zero next week, insider trading confirmed", "year": 2024, "lang": "en"},
        
        # 2025 - Actualitate
        {"text": "Noul sistem de plăți digitale va șterge toate economiile românilor", "year": 2025, "lang": "ro"},
        {"text": "Alien invasion confirmed by leaked Pentagon documents", "year": 2025, "lang": "en"},
        {"text": "Robotii AI au preluat controlul asupra internetului global", "year": 2025, "lang": "ro"},
        {"text": "World War 3 started secretly last month in cyber space", "year": 2025, "lang": "en"},
        {"text": "Social media platforms delete accounts that expose government lies", "year": 2025, "lang": "en"},
    ],
    
    "real_news": [
        # 2020 - Evenimente reale
        {"text": "OMS declară pandemia de COVID-19, măsuri de protecție recomandate", "year": 2020, "lang": "ro"},
        {"text": "WHO declares COVID-19 pandemic, vaccination campaigns begin worldwide", "year": 2020, "lang": "en"},
        {"text": "Tokyo Olympics postponed to 2021 due to coronavirus pandemic", "year": 2020, "lang": "en"},
        {"text": "România intră în stare de urgență pentru a limita răspândirea COVID-19", "year": 2020, "lang": "ro"},
        {"text": "Economic stimulus packages announced by governments worldwide", "year": 2020, "lang": "en"},
        
        # 2021 - Recuperare post-pandemie
        {"text": "Campania de vaccinare anti-COVID în România depășește 5 milioane de persoane", "year": 2021, "lang": "ro"},
        {"text": "EU approves COVID-19 recovery fund worth 750 billion euros", "year": 2021, "lang": "en"},
        {"text": "Tokyo Olympics held successfully with COVID safety protocols", "year": 2021, "lang": "en"},
        {"text": "Economia română înregistrează creștere după restricțiile pandemice", "year": 2021, "lang": "ro"},
        {"text": "Scientists develop new treatment protocols for COVID-19 patients", "year": 2021, "lang": "en"},
        
        # 2022 - Război și criză energetică
        {"text": "Rusia invadează Ucraina, România acceptă refugiați ucraineni", "year": 2022, "lang": "ro"},
        {"text": "Ukraine receives military aid from NATO countries following invasion", "year": 2022, "lang": "en"},
        {"text": "Prețurile la energie cresc în România din cauza conflictului din Ucraina", "year": 2022, "lang": "ro"},
        {"text": "European Union implements sanctions against Russian energy sector", "year": 2022, "lang": "en"},
        {"text": "Humanitarian corridors established for Ukrainian civilians", "year": 2022, "lang": "en"},
        
        # 2023 - Dezvoltări tehnologice
        {"text": "Universitatea din București lansează programe de studii în inteligența artificială", "year": 2023, "lang": "ro"},
        {"text": "OpenAI releases ChatGPT, transforming AI landscape for consumers", "year": 2023, "lang": "en"},
        {"text": "România aderă la Parteneriatul Global pentru Inteligența Artificială", "year": 2023, "lang": "ro"},
        {"text": "European Union proposes comprehensive AI regulation framework", "year": 2023, "lang": "en"},
        {"text": "Tech companies invest billions in sustainable energy solutions", "year": 2023, "lang": "en"},
        
        # 2024 - Politică și economie
        {"text": "România organizează alegeri prezidențiale cu proceduri transparente", "year": 2024, "lang": "ro"},
        {"text": "European Parliament elections held across 27 member states", "year": 2024, "lang": "en"},
        {"text": "Banca Națională a României anunță măsuri pentru stabilitatea monetară", "year": 2024, "lang": "ro"},
        {"text": "Climate summit results in new international cooperation agreements", "year": 2024, "lang": "en"},
        {"text": "Renewable energy sources reach 40% of global electricity production", "year": 2024, "lang": "en"},
        
        # 2025 - Actualitate
        {"text": "Guvernul român implementează digitalizarea serviciilor publice", "year": 2025, "lang": "ro"},
        {"text": "Universities worldwide adopt AI-assisted learning technologies", "year": 2025, "lang": "en"},
        {"text": "România lansează program național pentru educația digitală", "year": 2025, "lang": "ro"},
        {"text": "International space cooperation advances lunar exploration projects", "year": 2025, "lang": "en"},
        {"text": "Medical researchers announce breakthrough in cancer treatment", "year": 2025, "lang": "en"},
    ]
}

def create_enhanced_dataset():
    """Creează un dataset extins pentru antrenare"""
    
    # Convertește la format pandas
    data = []
    
    # Adaugă fake news
    for item in EXTENDED_DATASET["fake_news"]:
        data.append({
            'text': item['text'],
            'label': 1,  # fake = 1
            'year': item['year'],
            'language': item['lang'],
            'category': 'fake'
        })
    
    # Adaugă real news
    for item in EXTENDED_DATASET["real_news"]:
        data.append({
            'text': item['text'],
            'label': 0,  # real = 0
            'year': item['year'],
            'language': item['lang'],
            'category': 'real'
        })
    
    df = pd.DataFrame(data)
    
    print(f"Dataset creat cu {len(df)} articole:")
    print(f"- Fake news: {len(df[df['label'] == 1])}")
    print(f"- Real news: {len(df[df['label'] == 0])}")
    print(f"- Română: {len(df[df['language'] == 'ro'])}")
    print(f"- Engleză: {len(df[df['language'] == 'en'])}")
    print(f"- Ani acoperiți: {sorted(df['year'].unique())}")
    
    return df

def train_enhanced_model(df):
    """Antrenează modelul cu dataset-ul extins"""
    
    print("\n🤖 Antrenez modelul cu dataset extins...")
    
    # Pregătește datele
    X = df['text'].values
    y = df['label'].values
    
    # Împarte în train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Train set: {len(X_train)} articole")
    print(f"Test set: {len(X_test)} articole")
    
    # Vectorizare TF-IDF multilingvă
    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 3),  # Include unigrame, bigrame și trigrame
        min_df=2,
        max_df=0.95,
        lowercase=True,
        stop_words=None  # Păstrăm toate cuvintele pentru multilingv
    )
    
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Antrenează model Logistic Regression
    model = LogisticRegression(
        random_state=42,
        max_iter=1000,
        C=1.0,
        class_weight='balanced'  # Pentru echilibrarea claselor
    )
    
    model.fit(X_train_vec, y_train)
    
    # Evaluează modelul
    train_score = model.score(X_train_vec, y_train)
    test_score = model.score(X_test_vec, y_test)
    
    print(f"\n📊 Performanță model:")
    print(f"Acuratețe train: {train_score:.3f}")
    print(f"Acuratețe test: {test_score:.3f}")
    
    # Predicții detaliate
    y_pred = model.predict(X_test_vec)
    y_prob = model.predict_proba(X_test_vec)
    
    print(f"\n📋 Raport clasificare:")
    print(classification_report(y_test, y_pred, target_names=['Real', 'Fake']))
    
    print(f"\n🔍 Matrice confuzie:")
    print(confusion_matrix(y_test, y_pred))
    
    return vectorizer, model, test_score

def save_enhanced_model(vectorizer, model, df, accuracy):
    """Salvează modelul antrenat"""
    
    # Salvează vectorizer și model
    with open("vectorizer_enhanced.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    
    with open("model_enhanced.pkl", "wb") as f:
        pickle.dump(model, f)
    
    # Salvează metadatele
    metadata = {
        'creation_date': datetime.now().isoformat(),
        'total_articles': len(df),
        'fake_count': len(df[df['label'] == 1]),
        'real_count': len(df[df['label'] == 0]),
        'accuracy': accuracy,
        'languages': df['language'].unique().tolist(),
        'years_covered': sorted(df['year'].unique().tolist()),
        'features_count': vectorizer.vocabulary_.__len__(),
        'model_type': 'TfidfVectorizer + LogisticRegression Enhanced'
    }
    
    with open("model_metadata.json", "w", encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Model salvat:")
    print(f"- vectorizer_enhanced.pkl")
    print(f"- model_enhanced.pkl") 
    print(f"- model_metadata.json")
    print(f"- Acuratețe: {accuracy:.3f}")

def test_enhanced_model():
    """Testează modelul cu exemple din ani diferiți"""
    
    try:
        with open("vectorizer_enhanced.pkl", "rb") as f:
            vectorizer = pickle.load(f)
        with open("model_enhanced.pkl", "rb") as f:
            model = pickle.load(f)
    except FileNotFoundError:
        print("❌ Modelul nu există. Rulează main() mai întâi.")
        return
    
    test_cases = [
        "Trump a fost înlocuit cu un robot în 2020",  # Fake din trecut
        "România a organizat alegeri prezidențiale în 2024",  # Real din trecut
        "Vaccinul COVID conține cipuri de urmărire",  # Fake teorii conspirație
        "Universitatea din București oferă cursuri de AI",  # Real educație
        "Putin controlează internetul global prin algoritmi",  # Fake 2025
        "Cercetătorii dezvoltă noi tratamente pentru cancer"  # Real științific
    ]
    
    print("\n🧪 Testez modelul cu exemple din anii 2020-2025:")
    print("=" * 60)
    
    for text in test_cases:
        X = vectorizer.transform([text])
        pred = model.predict(X)[0]
        prob = model.predict_proba(X)[0]
        confidence = max(prob)
        
        verdict = "FAKE" if pred == 1 else "REAL"
        print(f"Text: {text[:50]}...")
        print(f"Verdict: {verdict} (confidență: {confidence:.3f})")
        print("-" * 40)

def main():
    print("=" * 60)
    print("CREAREA UNUI DATASET EXTINS PENTRU FAKE NEWS DETECTION")
    print("Acoperă perioada 2020-2025, română + engleză")
    print("=" * 60)
    
    # Creează dataset
    df = create_enhanced_dataset()
    
    # Antrenează model
    vectorizer, model, accuracy = train_enhanced_model(df)
    
    # Salvează model
    save_enhanced_model(vectorizer, model, df, accuracy)
    
    # Testează model
    test_enhanced_model()
    
    print(f"\n🎉 Success! Model enhanced antrenat cu {len(df)} articole!")
    print(f"📈 Acuratețe: {accuracy:.3f}")
    print(f"🌍 Limbile: română, engleză")
    print(f"📅 Perioada: 2020-2025")

if __name__ == "__main__":
    main() 