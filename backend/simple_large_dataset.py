# -*- coding: utf-8 -*-
"""
Creează un dataset mare simplu pentru fake news detection
Fără dependențe complexe, doar standard library
"""

import json
import pickle
import random
from datetime import datetime
import os

# Dataset mare cu știri reale și false
LARGE_FAKE_NEWS = [
    # Teorii conspirației COVID
    "Breaking: COVID-19 vaccine contains microchips for government tracking surveillance",
    "Secret documents reveal 5G towers cause coronavirus infections worldwide pandemic",
    "Bill Gates admits vaccines designed to reduce world population by 90 percent",
    "Hydroxychloroquine cures COVID-19 instantly but Big Pharma suppresses truth",
    "Masks destroy immune system and cause cancer in healthy people",
    "Ivermectin horse medicine proven 100% effective against coronavirus",
    "PCR tests are fake and create chemical dependency in patients",
    "Vitamins C and D completely prevent COVID-19 infection naturally",
    "Lockdowns are government mind control experiments on population",
    "Ventilators kill more patients than coronavirus itself doctors admit",
    
    # Teorii politice
    "Secret society controls all world governments from underground bunkers",
    "Elections are rigged by quantum computers owned by tech billionaires",
    "Politicians are replaced by AI robots in underground facilities",
    "Deep state controls media through alien technology from Roswell",
    "President is actually a clone controlled by foreign powers",
    "Government hides flat earth truth to maintain global conspiracy",
    "Chemtrails spray mind control chemicals to manipulate voters",
    "Moon landing was completely staged in Hollywood studios",
    "Area 51 houses alien government officials running shadow operations",
    "Time travel technology exists but hidden from public knowledge",
    
    # Tehnologie și AI
    "ChatGPT controls human minds through electromagnetic brain waves",
    "Social media apps steal dreams and sell them to corporations",
    "Smartphones cause instant cancer when placed near human body",
    "Internet algorithms brainwash users with subliminal hidden messages",
    "AI robots secretly replace world leaders in government positions",
    "Quantum computers predict future to manipulate stock markets",
    "Virtual reality headsets implant false memories in users",
    "Facial recognition software identifies thought crimes before commission",
    "Cryptocurrency mining destroys ozone layer causing climate change",
    "Self-driving cars programmed to eliminate specific ethnic groups",
    
    # Sănătate și medicină
    "Drinking bleach instantly cures all types of cancer naturally",
    "Vaccines cause autism in 99 percent of children studies prove",
    "Fluoride in water supply designed to make population docile",
    "Essential oils cure HIV AIDS and all viral infections",
    "Chemotherapy kills more patients than cancer itself doctors hide",
    "Hospitals profit from keeping patients sick with hidden poison",
    "Medical degrees are fake Big Pharma controls all doctors",
    "Natural herbs completely replace need for pharmaceutical drugs",
    "Surgery is unnecessary for any medical condition holistic healing",
    "Doctors inject tracking devices during routine medical examinations",
    
    # Economie și finanțe
    "Banks planning to eliminate all physical money by next month",
    "Stock market crashes are artificially created by secret societies",
    "Bitcoin will crash to zero value next week insider confirms",
    "Credit cards contain mind reading technology to track purchases",
    "Real estate prices manipulated by alien investors from space",
    "Gold standard abandoned to fund secret space military programs",
    "Tax money funds underground cities for government elite",
    "Economic inflation designed to force population into digital slavery",
    "Insurance companies use crystal balls to predict future claims",
    "Billionaires are actually immortal beings from another dimension",
    
    # Știință și mediu
    "Climate change is hoax to implement global government control",
    "Scientists hide discovery of perpetual motion energy machines",
    "Gravity is fake theory mountains grow upward not downward",
    "Evolution never happened dinosaurs lived with humans recently",
    "Nuclear power plants are actually alien communication devices",
    "Solar panels steal energy from sun causing global warming",
    "Earthquakes are caused by government underground drilling operations",
    "Weather is controlled by secret military atmospheric manipulation machines",
    "Ocean levels rise because fish are drinking too much water",
    "Space exploration is fake all rockets crash into invisible dome",
    
    # Alimentație și agricultură
    "GMO foods contain alien DNA to transform human genetics",
    "Organic labels are lies all food contains government mind chemicals",
    "Water bottles contain plastic that turns people into zombies",
    "Processed food companies add addiction chemicals to control behavior",
    "Farmers are paid to poison crops with experimental substances",
    "Fast food restaurants serve synthetic meat grown in laboratories",
    "Sugar is addictive drug designed to fund pharmaceutical industry",
    "Vitamins are actually poison disguised as health supplements",
    "Coffee beans contain tracking nanobots to monitor coffee drinkers",
    "Honey bees are government surveillance drones disguised as insects",
    
    # Media și comunicații
    "Television broadcasts hypnotic frequencies to control viewer thoughts",
    "Social media platforms delete accounts exposing government lies",
    "News anchors are actors reading scripts written by aliens",
    "Radio waves carry subliminal messages to influence political opinions",
    "Newspapers print with ink containing mind control chemicals",
    "Streaming services monitor viewers through smart TV cameras",
    "Podcasts are psychological warfare operations targeting specific demographics",
    "Video games train children to become future government assassins",
    "Movies contain hidden messages predicting future planned events",
    "Books are banned because they contain truth about reality"
]

LARGE_REAL_NEWS = [
    # Știință și tehnologie
    "Scientists discover new treatment for Alzheimer's disease using immunotherapy",
    "Research team develops breakthrough cancer therapy with 85% success rate",
    "University announces major advancement in quantum computing technology",
    "Medical researchers publish study on diabetes prevention methods",
    "Engineers create sustainable energy solution using solar panel innovation",
    "Pharmaceutical company completes successful COVID-19 vaccine trial",
    "Astronomers discover potentially habitable exoplanet in nearby system",
    "Researchers develop new antibiotic to combat drug-resistant bacteria",
    "Scientists create biodegradable plastic alternative from plant materials",
    "Study reveals genetic factors contributing to heart disease risk",
    
    # Educație și cercetare
    "Universities worldwide adopt AI-assisted learning technologies for students",
    "Education ministry announces increased funding for STEM programs",
    "Research institute publishes comprehensive climate change impact study",
    "Academic journal releases findings on mental health in teenagers",
    "International collaboration advances space exploration research projects",
    "Medical school introduces virtual reality training for surgery students",
    "Scientists complete decade-long longitudinal study on aging population",
    "University researchers develop new materials for renewable energy",
    "Educational technology shows promise in improving literacy rates",
    "Research center receives grant for neuroscience disease studies",
    
    # Sănătate publică
    "World Health Organization updates guidelines for infectious disease prevention",
    "Public health officials report successful vaccination campaign results",
    "Medical professionals recommend updated screening protocols for cancer",
    "Health department launches mental health awareness initiative",
    "Hospitals implement new safety measures to reduce infection rates",
    "Doctors report positive outcomes from new heart surgery technique",
    "Public health study reveals benefits of regular exercise routine",
    "Medical community emphasizes importance of preventive healthcare measures",
    "Healthcare workers receive training on latest treatment protocols",
    "Research shows effectiveness of community health intervention programs",
    
    # Politică și guvernare
    "Government announces infrastructure investment plan for transportation systems",
    "Parliament passes legislation to improve environmental protection standards",
    "Officials confirm successful international diplomatic cooperation agreement",
    "Public administration implements digital services for citizen convenience",
    "Legislative body approves budget allocation for education improvements",
    "Government establishes task force to address healthcare accessibility",
    "Officials announce renewable energy targets for next decade",
    "Parliament discusses measures to support small business development",
    "Government reports progress on poverty reduction initiatives",
    "Public policy experts recommend evidence-based decision making processes",
    
    # Economie și business
    "Stock market shows steady growth following quarterly earnings reports",
    "Central bank maintains interest rates to support economic stability",
    "Technology companies invest billions in renewable energy projects",
    "Small businesses report increased revenue from e-commerce expansion",
    "Economic indicators suggest continued recovery from pandemic impacts",
    "Manufacturing sector shows growth in sustainable production methods",
    "International trade agreements promote global economic cooperation",
    "Financial institutions implement new customer protection measures",
    "Economists project moderate inflation rates for upcoming year",
    "Investment in infrastructure creates jobs in construction industry",
    
    # Mediu și sustenabilitate
    "Environmental protection agency reports improvement in air quality",
    "Renewable energy sources reach 40% of national electricity production",
    "Conservation efforts show positive results for endangered species",
    "Cities implement sustainable transportation solutions to reduce emissions",
    "Climate scientists publish comprehensive assessment of global warming",
    "Government launches initiative to promote recycling and waste reduction",
    "Environmental researchers study effects of reforestation programs",
    "Green technology companies develop innovative carbon capture solutions",
    "Marine biologists report recovery in ocean ecosystem health",
    "Sustainable agriculture practices increase crop yields while protecting soil",
    
    # Cultură și societate
    "Museums expand digital accessibility for international virtual visitors",
    "Cultural festivals celebrate diversity and promote community engagement",
    "Libraries introduce new programs to support literacy development",
    "Arts organizations receive funding to support local creative projects",
    "Cultural heritage sites implement preservation measures for future generations",
    "Community centers offer programs to address social isolation",
    "Sports organizations promote youth participation in physical activities",
    "Cultural exchange programs strengthen international understanding and cooperation",
    "Public art installations enhance urban environments and community pride",
    "Social workers report positive outcomes from community support programs",
    
    # Transport și infrastructură
    "Transportation authorities improve public transit accessibility for disabled passengers",
    "Infrastructure projects create safer roads and bridges for communities",
    "Public transportation systems adopt electric buses to reduce emissions",
    "Urban planners design pedestrian-friendly streets to encourage walking",
    "Railway companies invest in high-speed rail technology improvements",
    "Airport authorities implement enhanced security measures for passenger safety",
    "Highway maintenance programs ensure safe travel conditions year-round",
    "Public works departments upgrade water treatment facilities",
    "Engineering teams complete seismic retrofitting of critical infrastructure",
    "Transportation networks integrate smart technology for traffic optimization",
    
    # Tehnologie și inovație
    "Tech companies develop accessibility software for visually impaired users",
    "Cybersecurity experts recommend best practices for online safety",
    "Innovation labs create solutions for sustainable manufacturing processes",
    "Software developers release open-source tools for educational purposes",
    "Telecommunications companies expand broadband access to rural areas",
    "Research teams advance artificial intelligence applications in healthcare",
    "Technology firms invest in employee training and development programs",
    "Digital platforms implement measures to protect user privacy",
    "Engineers develop more efficient battery technology for electric vehicles",
    "Computer scientists work on quantum computing applications for research",
    
    # Sport și recreație
    "Athletic programs promote physical fitness and health in schools",
    "Professional sports leagues implement safety protocols for player protection",
    "Olympic committees prepare for international competition events",
    "Recreation centers offer programs for all ages and ability levels",
    "Sports medicine advances help athletes recover from injuries faster",
    "Community organizations promote outdoor activities and nature appreciation",
    "Fitness research demonstrates benefits of regular physical exercise",
    "Adaptive sports programs provide opportunities for disabled athletes",
    "Youth sports leagues emphasize teamwork and character development",
    "Recreation facilities upgrade equipment to serve growing communities"
]

def create_large_simple_dataset(num_fake=500, num_real=500):
    """Creează un dataset mare simplu"""
    print(f"🔨 Creez dataset cu {num_fake} fake + {num_real} real = {num_fake + num_real} total articole...")
    
    data = []
    
    # Generează fake news prin variație
    fake_base = LARGE_FAKE_NEWS
    for i in range(num_fake):
        base_text = random.choice(fake_base)
        # Adaugă variații pentru a crea mai multe exemple
        variations = [
            f"URGENT: {base_text}",
            f"BREAKING NEWS: {base_text}",
            f"EXCLUSIVE: {base_text}",
            f"LEAKED: {base_text}",
            f"SHOCKING: {base_text}",
            base_text,
            f"{base_text} - Sources confirm",
            f"{base_text} - Experts warn",
            f"{base_text} - Investigation reveals",
            f"{base_text} - Documents show"
        ]
        
        selected_text = random.choice(variations)
        data.append({
            'text': selected_text,
            'label': 1,  # fake
            'category': 'fake',
            'id': f"fake_{i+1}"
        })
    
    # Generează real news prin variație
    real_base = LARGE_REAL_NEWS
    for i in range(num_real):
        base_text = random.choice(real_base)
        # Adaugă variații pentru știri reale
        variations = [
            f"Study: {base_text}",
            f"Report: {base_text}", 
            f"Research: {base_text}",
            f"Analysis: {base_text}",
            base_text,
            f"{base_text} according to officials",
            f"{base_text} researchers report",
            f"{base_text} study finds",
            f"{base_text} data shows",
            f"{base_text} experts say"
        ]
        
        selected_text = random.choice(variations)
        data.append({
            'text': selected_text,
            'label': 0,  # real
            'category': 'real',
            'id': f"real_{i+1}"
        })
    
    print(f"✅ Dataset creat cu success:")
    print(f"   - Fake news: {num_fake}")
    print(f"   - Real news: {num_real}")
    print(f"   - Total: {len(data)}")
    
    return data

def simple_train_test_split(data, test_size=0.2):
    """Împarte datele în train/test simplu"""
    random.shuffle(data)
    split_idx = int(len(data) * (1 - test_size))
    train_data = data[:split_idx]
    test_data = data[split_idx:]
    return train_data, test_data

def simple_accuracy(y_true, y_pred):
    """Calculează acuratețea simplu"""
    correct = sum(1 for true, pred in zip(y_true, y_pred) if true == pred)
    return correct / len(y_true)

def simple_fake_news_classifier(train_data, test_data):
    """Clasificator simplu bazat pe cuvinte cheie"""
    print("🤖 Antrenez clasificator simplu bazat pe cuvinte cheie...")
    
    # Cuvinte caracteristice pentru fake news
    fake_keywords = [
        'breaking', 'urgent', 'shocking', 'secret', 'hidden', 'leaked', 
        'conspiracy', 'government', 'control', 'mind', 'aliens', 'hoax',
        'instantly', 'proven', 'admits', 'reveals', 'truth', 'suppresses',
        'microchips', 'tracking', 'surveillance', 'underground', 'elite',
        'fake', 'designed', 'artificial', 'robot', 'clone', 'staged'
    ]
    
    # Cuvinte caracteristice pentru real news
    real_keywords = [
        'research', 'study', 'university', 'scientists', 'medical', 'health',
        'according', 'report', 'analysis', 'data', 'experts', 'officials',
        'published', 'findings', 'evidence', 'treatment', 'therapy', 'technology',
        'development', 'improvement', 'safety', 'measures', 'guidelines', 'professional'
    ]
    
    def predict_single(text):
        text_lower = text.lower()
        fake_score = sum(1 for word in fake_keywords if word in text_lower)
        real_score = sum(1 for word in real_keywords if word in text_lower)
        
        if fake_score > real_score:
            return 1  # fake
        elif real_score > fake_score:
            return 0  # real
        else:
            # Dacă egalitate, folosește lungimea textului și alte heuristici
            if len(text) > 100 and ('breaking' in text_lower or 'urgent' in text_lower):
                return 1  # fake
            else:
                return 0  # real
    
    # Testează pe datele de antrenare
    train_texts = [item['text'] for item in train_data]
    train_labels = [item['label'] for item in train_data]
    train_predictions = [predict_single(text) for text in train_texts]
    train_accuracy = simple_accuracy(train_labels, train_predictions)
    
    # Testează pe datele de test
    test_texts = [item['text'] for item in test_data]
    test_labels = [item['label'] for item in test_data]
    test_predictions = [predict_single(text) for text in test_texts]
    test_accuracy = simple_accuracy(test_labels, test_predictions)
    
    print(f"📊 Rezultate clasificator simplu:")
    print(f"   - Acuratețe antrenare: {train_accuracy:.3f}")
    print(f"   - Acuratețe testare: {test_accuracy:.3f}")
    
    return predict_single, test_accuracy

def save_simple_model(dataset, classifier_func, accuracy):
    """Salvează modelul simplu"""
    print("💾 Salvez modelul simplu...")
    
    # Salvează dataset-ul
    with open("simple_large_dataset.json", "w", encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    # Salvează metadatele
    metadata = {
        'creation_date': datetime.now().isoformat(),
        'total_articles': len(dataset),
        'fake_count': len([item for item in dataset if item['label'] == 1]),
        'real_count': len([item for item in dataset if item['label'] == 0]),
        'accuracy': accuracy,
        'model_type': 'Simple Keyword-based Classifier',
        'description': 'Large dataset with simple keyword-based classification'
    }
    
    with open("simple_model_metadata.json", "w", encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Model simplu salvat:")
    print(f"   - simple_large_dataset.json ({len(dataset)} articole)")
    print(f"   - simple_model_metadata.json")
    print(f"   - Acuratețe: {accuracy:.3f}")

def test_simple_model():
    """Testează modelul simplu"""
    print("\n🧪 Testez modelul simplu...")
    
    # Recrează clasificatorul (simplu pentru demo)
    fake_keywords = ['breaking', 'urgent', 'secret', 'conspiracy', 'microchips', 'control']
    real_keywords = ['research', 'study', 'university', 'medical', 'according', 'published']
    
    def predict(text):
        text_lower = text.lower()
        fake_score = sum(1 for word in fake_keywords if word in text_lower)
        real_score = sum(1 for word in real_keywords if word in text_lower)
        return 1 if fake_score > real_score else 0
    
    test_cases = [
        "URGENT: Government hides secret microchips in vaccines",
        "Research study shows benefits of new medical treatment",
        "BREAKING: Aliens control world governments from underground",
        "University publishes findings on climate change solutions",
        "SHOCKING: 5G towers cause coronavirus infections worldwide",
        "Medical experts recommend updated vaccination guidelines"
    ]
    
    print("=" * 70)
    for text in test_cases:
        pred = predict(text)
        verdict = "🚨 FAKE" if pred == 1 else "✅ REAL"
        print(f"Text: {text[:50]}...")
        print(f"Verdict: {verdict}")
        print("-" * 70)

def main():
    print("=" * 80)
    print("CREAREA UNUI DATASET MARE SIMPLU PENTRU FAKE NEWS DETECTION")
    print("Fără dependențe complexe - doar Python standard")
    print("=" * 80)
    
    # Creează dataset mare
    dataset = create_large_simple_dataset(num_fake=1000, num_real=1000)
    
    # Împarte în train/test
    train_data, test_data = simple_train_test_split(dataset, test_size=0.2)
    print(f"\n📊 Împărțire date:")
    print(f"   - Antrenare: {len(train_data)} articole")
    print(f"   - Testare: {len(test_data)} articole")
    
    # Antrenează clasificator simplu
    classifier, accuracy = simple_fake_news_classifier(train_data, test_data)
    
    # Salvează model
    save_simple_model(dataset, classifier, accuracy)
    
    # Testează model
    test_simple_model()
    
    print(f"\n🎉 SUCCESS! Dataset mare simplu creat cu {len(dataset)} articole!")
    print(f"📈 Acuratețe: {accuracy:.3f}")
    print(f"💾 Fișiere salvate: simple_large_dataset.json, simple_model_metadata.json")

if __name__ == "__main__":
    main() 