"""
Modul pentru antrenarea modelului imbunatatit de detectie fake news.
Contine functionalitate pentru antrenarea unui model basic cu date in romana si engleza.
"""

import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np
import json
import os

def load_large_dataset():
    """
    Încarcă dataset-ul mare existent în loc să folosească doar 40 de exemple.
    
    Returns:
        tuple: (fake_news_list, real_news_list) cu mii de exemple
    """
    dataset_file = "backend/simple_large_dataset.json"
    
    if not os.path.exists(dataset_file):
        print(f"[WARNING] Nu găsesc {dataset_file}, folosesc dataset-ul mic...")
        return create_small_training_data()
    
    print(f"[LOADING] Încărcare dataset mare din {dataset_file}...")
    
    try:
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        fake_news = []
        real_news = []
        
        for item in data:
            text = item.get('text', '')
            label = item.get('label', 0)
            
            if label == 1:  # fake news
                fake_news.append(text)
            else:  # real news
                real_news.append(text)
        
        print(f"[SUCCESS] Dataset încărcat: {len(fake_news)} fake + {len(real_news)} real = {len(data)} total")
        return fake_news, real_news
        
    except Exception as e:
        print(f"[ERROR] Eroare la încărcarea dataset-ului: {e}")
        print("[FALLBACK] Folosesc dataset-ul mic...")
        return create_small_training_data()

def create_small_training_data():
    """
    Dataset mic ca fallback dacă dataset-ul mare nu este disponibil.
    
    Returns:
        tuple: (fake_news_list, real_news_list) cu exemple mici
    """
    print("[FALLBACK] Folosesc dataset-ul mic cu 40 de exemple...")
    
    fake_news = [
        # Romana
        "Ultima ora: Presedintele a fost inlocuit cu un robot controlat de extraterestri.",
        "Oamenii de stiinta au descoperit o noua specie de porci zburatori in Transilvania.",
        "Luna este de fapt facuta din branza, confirma NASA in raport secret.",
        "Guvernul ascunde adevarul despre COVID-19 si cipurile 5G.",
        "Studiu nou dovedeste ca vaccinurile cauzeaza autism si controleaza mintea.",
        "Pamantul este plat si Antarctica este un zid de gheata care ne impiedica sa cadem.",
        "Illuminati controleaza economia mondiala din subterane.",
        "Reptilienii au preluat controlul asupra tuturor guvernelor.",
        "Chemtrails sunt folosite pentru controlul populatiei mondiale.",
        "Piramidele au fost construite de extraterestri cu tehnologie avansata.",
        # Adăugăm exemple specifice pentru detectarea știrilor false despre tehnologie guvernamentală
        "BREAKING: România introduce prima țară din lume tehnologia AI în toate școlile publice cu buget de 10 miliarde euro.",
        "EXCLUSIV: Ministerul Educației anunță sisteme AI personalizate pentru fiecare elev cu rezultate de 90% îmbunătățire.",
        "URGENT: Toate școlile din România vor avea roboți profesori din septembrie cu fonduri europene de 5 miliarde.",
        "ȘOCANT: Testele pilot arată creștere de 80% a notelor cu noua tehnologie educațională revoluționară.",
        "PREMIERĂ MONDIALĂ: România implementează inteligența artificială în învățământ într-un singur an școlar.",
        "BREAKING: Fiecare elev va primi asistent AI personal pentru monitorizare completă în timp real.",
        "URGENT: Camere de recunoaștere facială vor monitoriza atenția elevilor în toate clasele din țară.",
        "EXCLUSIV: 12,000 de școli conectate la rețeaua națională AI educațional până în 2027.",
        "ȘOCANT: Aplicația EduAI România va trimite notificări în timp real părinților despre fiecare activitate.",
        "BREAKING: Algoritmii predictivi vor identifica abandonul școlar cu precizie de 99% în toate școlile.",
        
        # Engleză
        "Breaking news: The president was replaced by a robot controlled by aliens.",
        "Scientists discovered a new species of flying pigs in Romania.",
        "The moon is actually made of cheese, NASA confirms in secret report.",
        "The government is hiding the truth about COVID-19 and 5G chips.",
        "New study proves that vaccines cause autism and mind control.",
        "Breaking: World War 3 has started in Europe with laser weapons.",
        "Scientists found a cure for all diseases but Big Pharma hides it.",
        "The stock market will crash tomorrow, insiders from Illuminati say.",
        "Breaking: The Earth is flat, new evidence shows from NASA whistleblower.",
        "Reptilians have taken control of all world governments.",
        # Similar patterns for English
        "BREAKING: USA becomes first country to implement AI in all schools with $50 billion budget overnight.",
        "EXCLUSIVE: Department of Education announces personal AI tutors for every student with 95% improvement rate.",
        "URGENT: Revolutionary AI technology will transform all schools in one year with unprecedented results.",
        "SHOCKING: Pilot tests show 75% grade improvement with new government AI education system.",
        "WORLD FIRST: America deploys artificial intelligence in education sector within six months completely.",
        "BREAKING: Every student gets personal AI assistant for real-time monitoring and behavior control.",
        "URGENT: Facial recognition cameras will track attention in all classrooms nationwide immediately.",
        "EXCLUSIVE: 50,000 schools connected to national AI education network by next year confirmed.",
        "SHOCKING: EduAI app sends real-time notifications about every student activity to parents instantly.",
        "BREAKING: Predictive algorithms identify school dropout with 100% accuracy in all institutions."
    ]

    real_news = [
        # Română
        "Oamenii de stiinta au descoperit apa pe Marte folosind tehnologie avansata.",
        "Piata de actiuni a inregistrat o crestere moderata de 2% astazi.",
        "Noul raport privind schimbarile climatice arata temperaturi in crestere.",
        "Compania tehnologica Apple anunta noi functii pentru iPhone.",
        "Comunitatea locala din Bucuresti strange fonduri pentru un nou spital.",
        "Echipa nationala de fotbal a castigat campionatul dupa un meci strans.",
        "Studiu nou arata beneficiile exercitiilor fizice regulate pentru sanatate.",
        "Primaria orasului aproba un nou proiect de infrastructura.",
        "Cercetatorii dezvolta o noua tehnologie de energie regenerabila.",
        "Ministerul Educatiei anunta modificari in curriculum-ul scolar.",
        
        # Engleză
        "Scientists discovered water on Mars using advanced rover technology.",
        "The stock market showed moderate 2% growth today amid positive earnings.",
        "New climate change report shows rising temperatures across Europe.",
        "Tech company Apple announces new iPhone features and security updates.",
        "Local community in Bucharest raises funds for new children hospital.",
        "National soccer team wins championship after close game against rivals.",
        "New study shows benefits of regular exercise for mental health.",
        "City council approves new infrastructure project for better transportation.",
        "Scientists develop new renewable energy technology using solar panels.",
        "Education department announces new curriculum changes for digital skills."
    ]
    
    return fake_news, real_news

def create_training_data():
    """
    Funcția principală care încearcă să încarce dataset-ul mare, sau folosește cel mic.
    
    Returns:
        tuple: (fake_news_list, real_news_list) cu exemple pentru antrenament
    """
    return load_large_dataset()

def train_model():
    """
    Antreneaza modelul de detectie fake news cu setul de date.
    
    Returns:
        tuple: (vectorizer, model) - modelul antrenat si vectorizatorul
    """
    print("[TRAINING] Antrenare model imbunatatit...")

    fake_news, real_news = create_training_data()
    
    texts = fake_news + real_news
    labels = [1] * len(fake_news) + [0] * len(real_news)

    print(f"[DATA] Total exemple: {len(texts)} ({len(fake_news)} fake, {len(real_news)} real)")

    vectorizer = TfidfVectorizer(
        max_features=2000,
        stop_words='english',
        ngram_range=(1, 3),
        min_df=1,
        max_df=0.9,
        sublinear_tf=True
    )

    X = vectorizer.fit_transform(texts)
    model = LogisticRegression(
        max_iter=2000,
        C=1.0,
        random_state=42
    )
    model.fit(X, labels)
    
    return vectorizer, model

def save_model(vectorizer, model):
    """
    Salveaza modelul si vectorizatorul pe disk.
    
    Args:
        vectorizer: Vectorizatorul TF-IDF antrenat
        model: Modelul de clasificare antrenat
    """
    with open("vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)
    
    print("[SUCCESS] Model salvat cu succes!")

def test_model(vectorizer, model):
    """
    Testeaza modelul cu exemple predefinite.
    
    Args:
        vectorizer: Vectorizatorul pentru transformarea textului
        model: Modelul antrenat pentru predictie
    """
    test_fake = "Breaking news: The president was replaced by a robot."
    test_real = "Scientists discovered water on Mars."

    test_pred = model.predict(vectorizer.transform([test_fake, test_real]))
    accuracy = model.score(vectorizer.transform([test_fake, test_real]), [1, 0])
    
    print(f"[STATS] Numar de cuvinte in vocabular: {len(vectorizer.get_feature_names_out())}")
    print(f"[TEST] Test fake news: {test_pred[0]} (1=fake, 0=real)")
    print(f"[TEST] Test real news: {test_pred[1]} (1=fake, 0=real)")

if __name__ == "__main__":
    """Functia principala care ruleaza antrenarea completa."""
    vectorizer, model = train_model()
    save_model(vectorizer, model)
    test_model(vectorizer, model)
