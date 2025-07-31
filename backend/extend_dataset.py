#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pentru extinderea datasetului cu fake news subtile și real news
"""

import json
import random
from datetime import datetime

def load_existing_dataset():
    """Încarcă datasetul existent"""
    try:
        with open("simple_large_dataset.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Eroare la încărcarea datasetului: {e}")
        return []

def generate_subtle_fake_news():
    """Generează fake news subtile pentru antrenare"""
    
    # Template-uri pentru fake news subtile
    fake_templates = [
        # Autorități vagi + afirmații mari
        "{authority} confirms {claim} shows {result}.",
        "Leading {experts} discover {breakthrough} that {impact}.",
        "Recent {study_type} reveals {result} according to {source}.",
        "International {organization} announces {breakthrough} will {impact}.",
        "{prestigious_entity} finds {surprising_result} in {study_area}.",
        "Anonymous {expert_type} shares {secret_info} about {topic}.",
        
        # Combinații suspecte
        "{urgency}: {authority} proves {exaggerated_claim}.",
        "Sources confirm {shocking_discovery} that {absolute_claim}.",
        "{breaking_phrase} {vague_source} reveals {incredible_result}.",
        "Experts stunned by {remarkable_finding} that {guarantee}.",
        "{organization_type} study shows {dramatic_improvement} using {method}."
    ]
    
    # Componente pentru template-uri
    authorities = [
        "International Health Organization", "Global Research Institute", "Advanced Medical Center",
        "Prestigious University", "Leading Research Foundation", "Renowned Scientific Center",
        "World Health Alliance", "International Medical Board", "Elite Research Group"
    ]
    
    experts = [
        "specialists", "researchers", "authorities", "professionals", "scientists",
        "medical experts", "industry leaders", "top researchers", "leading scientists"
    ]
    
    study_types = [
        "study", "research", "investigation", "analysis", "survey", "report",
        "clinical trial", "scientific review", "comprehensive study"
    ]
    
    organizations = [
        "Medical Association", "Research Council", "Health Foundation", "Scientific Alliance",
        "Medical Board", "Research Institute", "Health Organization", "Science Council"
    ]
    
    claims = [
        "new method", "revolutionary technique", "breakthrough discovery", "innovative approach", 
        "advanced treatment", "secret formula", "natural remedy", "proven system"
    ]
    
    results = [
        "remarkable improvements", "incredible benefits", "amazing results", "unprecedented success",
        "dramatic changes", "extraordinary outcomes", "stunning effects", "miraculous healing"
    ]
    
    breakthroughs = [
        "revolutionary method", "groundbreaking technique", "innovative solution", "secret approach",
        "advanced system", "proven formula", "natural treatment", "breakthrough therapy"
    ]
    
    impacts = [
        "transforms lives completely", "guarantees instant results", "changes everything forever",
        "provides immediate relief", "solves problems permanently", "works 100% of the time"
    ]
    
    fake_news_list = []
    fake_id = 2000  # Pornesc de la un ID mare să nu se suprapună
    
    # Generez 300 de fake news subtile
    for i in range(300):
        template = random.choice(fake_templates)
        
        # Înlocuiesc toate variabilele necesare
        format_dict = {
            'authority': random.choice(authorities),
            'claim': random.choice(claims),
            'result': random.choice(results),
            'experts': random.choice(experts),
            'breakthrough': random.choice(breakthroughs),
            'impact': random.choice(impacts),
            'study_type': random.choice(study_types),
            'source': random.choice(authorities),
            'organization': random.choice(organizations),
            'prestigious_entity': random.choice(authorities),
            'surprising_result': random.choice(results),
            'study_area': "various fields",
            'expert_type': random.choice(experts),
            'secret_info': "confidential information",
            'topic': "important matters",
            'urgency': random.choice(["BREAKING", "URGENT", "EXCLUSIVE", "SHOCKING"]),
            'exaggerated_claim': random.choice(claims),
            'shocking_discovery': random.choice(breakthroughs),
            'absolute_claim': random.choice(impacts),
            'breaking_phrase': random.choice(["Breaking news:", "Urgent update:", "Exclusive report:"]),
            'vague_source': random.choice(["reliable sources", "inside sources", "anonymous experts"]),
            'incredible_result': random.choice(results),
            'guarantee': random.choice(["guarantees success", "ensures results", "promises benefits"]),
            'organization_type': random.choice(["International", "Global", "Leading"]),
            'dramatic_improvement': random.choice(results),
            'method': random.choice(["simple technique", "natural method", "proven approach"]),
            'finding': random.choice(results),
            'discovery': random.choice(breakthroughs),
            'outcome': random.choice(impacts),
            'remarkable_finding': random.choice(results)
        }
        
        try:
            fake_text = template.format(**format_dict)
        except KeyError as e:
            # Fallback pentru variabile lipsă
            fake_text = f"Leading experts discover {random.choice(breakthroughs)} that {random.choice(impacts)}."
        
        fake_news_list.append({
            "text": fake_text,
            "label": 1,
            "category": "fake",
            "id": f"fake_new_{fake_id + i}",
            "type": "subtle_generated"
        })
    
    return fake_news_list

def generate_real_news():
    """Generează real news pentru balansarea datasetului"""
    
    real_templates = [
        # Știri reale cu surse concrete
        "The {department} announced {specific_action} following {concrete_reason}.",
        "According to {official_source}, {factual_statement} as reported in {publication}.",
        "{organization} released {document_type} showing {statistical_data}.",
        "Research conducted by {university} indicates {measured_result} over {time_period}.",
        "The {government_body} approved {specific_policy} with {vote_details}.",
        "{company} reported {financial_data} in their {report_type} filed with {regulatory_body}.",
        
        # Știri cu date concrete
        "{location} officials confirm {specific_event} occurred on {timeframe}.",
        "Data from {source_organization} shows {percentage} change in {metric}.",
        "The {institution} study involving {participant_count} participants found {moderate_result}.",
        "{expert_name}, {title} at {institution}, stated that {reasonable_claim}.",
        "Emergency services responded to {incident_type} at {specific_location} on {date}."
    ]
    
    departments = [
        "Department of Health", "Ministry of Education", "Transportation Department",
        "Environmental Agency", "Labor Department", "Commerce Department"
    ]
    
    specific_actions = [
        "new safety guidelines", "updated regulations", "budget allocation changes",
        "policy modifications", "procedural updates", "regulatory adjustments"
    ]
    
    concrete_reasons = [
        "recent safety assessments", "quarterly reviews", "public feedback",
        "compliance requirements", "operational evaluations", "standard procedures"
    ]
    
    official_sources = [
        "the Census Bureau", "Federal Reserve", "Department of Labor",
        "Environmental Protection Agency", "Centers for Disease Control"
    ]
    
    real_news_list = []
    real_id = 2000
    
    # Generez 300 de real news
    for i in range(300):
        template = random.choice(real_templates)
        
        # Dictionary pentru toate variabilele real news
        real_format_dict = {
            'department': random.choice(departments),
            'specific_action': random.choice(specific_actions),
            'concrete_reason': random.choice(concrete_reasons),
            'official_source': random.choice(official_sources),
            'factual_statement': "unemployment rates decreased by 0.3%",
            'publication': "quarterly economic report",
            'organization': random.choice(official_sources),
            'document_type': "quarterly report",
            'statistical_data': "a 2.1% increase in applications",
            'university': random.choice(["Stanford University", "MIT", "Harvard University", "UC Berkeley"]),
            'measured_result': "moderate improvements in test scores",
            'time_period': "the past 6 months",
            'government_body': "City Council",
            'specific_policy': "the infrastructure improvement plan",
            'vote_details': "a 7-3 vote",
            'company': "ABC Corporation",
            'financial_data': "$2.3 million in quarterly revenue",
            'report_type': "earnings report",
            'regulatory_body': "Securities and Exchange Commission",
            'location': random.choice(["Chicago", "Seattle", "Austin", "Denver"]),
            'specific_event': "a traffic accident",
            'timeframe': "Tuesday morning",
            'source_organization': random.choice(official_sources),
            'percentage': random.choice(["3.2%", "1.8%", "4.1%", "2.7%"]),
            'metric': random.choice(["enrollment", "applications", "participation", "compliance"]),
            'institution': random.choice(["City University", "State College", "Regional Hospital"]),
            'participant_count': random.choice(["150", "247", "389", "512"]),
            'moderate_result': "slight improvements in the measured outcomes",
            'expert_name': random.choice(["Dr. Johnson", "Prof. Smith", "Dr. Martinez"]),
            'title': random.choice(["Director", "Professor", "Senior Researcher"]),
            'reasonable_claim': "the results are encouraging but require further study",
            'incident_type': "a minor building evacuation",
            'specific_location': "1st Avenue",
            'date': "Monday afternoon"
        }
        
        try:
            real_text = template.format(**real_format_dict)
        except KeyError as e:
            # Fallback pentru variabile lipsă
            real_text = f"The {random.choice(departments)} announced {random.choice(specific_actions)} following {random.choice(concrete_reasons)}."
        
        real_news_list.append({
            "text": real_text,
            "label": 0,
            "category": "real", 
            "id": f"real_new_{real_id + i}",
            "type": "concrete_generated"
        })
    
    return real_news_list

def extend_dataset():
    """Extinde datasetul cu noi exemple"""
    print("🔄 Încărcare dataset existent...")
    existing_data = load_existing_dataset()
    original_count = len(existing_data)
    
    print(f"📊 Dataset original: {original_count} intrări")
    
    print("🎯 Generare fake news subtile...")
    new_fake_news = generate_subtle_fake_news()
    
    print("📰 Generare real news...")
    new_real_news = generate_real_news()
    
    # Combină toate datele
    extended_data = existing_data + new_fake_news + new_real_news
    
    # Amestecă datasetul
    random.shuffle(extended_data)
    
    print(f"📈 Dataset extins: {len(extended_data)} intrări (+{len(new_fake_news + new_real_news)})")
    
    # Salvează datasetul extins
    with open("simple_large_dataset_extended.json", "w", encoding="utf-8") as f:
        json.dump(extended_data, f, ensure_ascii=False, indent=2)
    
    # Salvează și o versiune backup a originalului
    with open(f"simple_large_dataset_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    print("✅ Dataset extins salvat ca 'simple_large_dataset_extended.json'")
    print("💾 Backup original salvat")
    
    # Statistici
    fake_count = len([item for item in extended_data if item['label'] == 1])
    real_count = len([item for item in extended_data if item['label'] == 0])
    
    print(f"\n📊 STATISTICI FINALE:")
    print(f"Total intrări: {len(extended_data)}")
    print(f"Fake news: {fake_count} ({fake_count/len(extended_data)*100:.1f}%)")
    print(f"Real news: {real_count} ({real_count/len(extended_data)*100:.1f}%)")
    
    return extended_data

if __name__ == "__main__":
    try:
        extended_data = extend_dataset()
        print("\n🎉 Dataset extins cu succes!")
    except Exception as e:
        print(f"❌ Eroare: {e}") 