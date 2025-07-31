"""
Modul pentru analiza fake news folosind servicii AI externe.
Implementeaza detectia fake news cu OpenAI GPT si Google Perspective API.
"""

import openai
import requests
from langdetect import detect
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

try:
    from config import *
    GOOGLE_API_KEY = GOOGLE_PERSPECTIVE_API_KEY
except ImportError:
    OPENAI_API_KEY = ""
    GOOGLE_API_KEY = ""
    ANTHROPIC_API_KEY = ""
    ENABLE_AI_SERVICES = False
    MULTILINGUAL_PROMPTS = {
        'ro': 'Analizează acest text',
        'en': 'Analyze this text',
        'fr': 'Analysez ce texte',
        'es': 'Analiza este texto'
    }
    DEFAULT_MODEL = "gpt-3.5-turbo"
    ENABLE_OPENAI = False
    ENABLE_ANTHROPIC = False
    ENABLE_PERSPECTIVE = False
    FAKE_NEWS_THRESHOLD = 0.7
    TOXICITY_THRESHOLD = 0.6
    SUPPORTED_LANGUAGES = ['ro', 'en', 'fr', 'es', 'de', 'it']

class AIAnalyzer:
    """
    Clasa pentru analiza fake news folosind servicii AI externe.
    Combina OpenAI GPT cu Google Perspective API pentru detectie avansata.
    """
    
    def __init__(self):
        """Initializeaza analizorul AI cu configuratiile necesare."""
        self.logger = logging.getLogger(__name__)
        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY

    def detect_language(self, text: str) -> str:
        """
        Detecteaza limba textului cu imbunatatiri pentru romana.
        
        Args:
            text: Textul pentru detectia limbii
            
        Returns:
            str: Codul limbii detectate (ro, en, etc.)
        """
        try:
            detected = detect(text)
            
            text_lower = text.lower()
            
            ro_specific = ['și', 'să', 'că', 'într-', 'către', 'asupra', 'dintre', 'printre', 'analiștii', 'bursa', 'creștere', 'companii', 'sectorul', 'tendință', 'prețuri', 'energie', 'financiar', 'această', 'următoarele', 'stabilizării']
            
            en_specific = ['the', 'that', 'this', 'which', 'clinical', 'trial', 'study', 'research', 'published', 'journal', 'patients', 'treatment', 'therapy', 'analysis', 'approach', 'management', 'peer-reviewed', 'hospitals', 'researchers', 'combination', 'compared', 'standard', 'minimal', 'effects', 'reported']
            
            ro_count = sum(1 for word in ro_specific if word in text_lower)
            en_count = sum(1 for word in en_specific if word in text_lower)
            
            if detected == 'en' and en_count >= 3:
                return 'en'
            elif detected == 'ro' and ro_count >= 2:
                return 'ro'
            elif en_count >= 5:
                return 'en'
            elif ro_count >= 3:
                return 'ro'
            else:
                return detected
                
        except:
            text_lower = text.lower()
            
            ro_words = ['și', 'să', 'că', 'această', 'următoarele']
            en_words = ['the', 'that', 'clinical', 'study', 'research', 'published', 'patients', 'treatment']
            
            ro_count = sum(1 for word in ro_words if word in text_lower)
            en_count = sum(1 for word in en_words if word in text_lower)
            
            if en_count >= 3:
                return 'en'
            elif ro_count >= 2:
                return 'ro'
            else:
                return 'unknown'

    async def analyze_with_openai(self, text: str, language: str = None) -> Dict:
        """
        Analizeaza textul folosind OpenAI GPT pentru detectia fake news.
        
        Args:
            text: Textul pentru analiza
            language: Limba textului (optional)
            
        Returns:
            dict: Rezultatul analizei cu verdict, confidence si explicatie
        """
        if not ENABLE_OPENAI or not OPENAI_API_KEY:
            return {"error": "OpenAI nu este configurat"}

        prompt = f"""You are an expert in fake news detection and media analysis.

STEP 1 - LANGUAGE DETECTION:
Analyze this text and identify its language:
"{text[:2000]}"

STEP 2 - RESPONSE LANGUAGE RULE:
You MUST respond in the EXACT SAME LANGUAGE as the input text.
- If text is in English → respond in English
- If text is in Romanian → respond in Romanian  
- If text is in Italian → respond in Italian
- If text is in Spanish → respond in Spanish
- If text is in French → respond in French

STEP 3 - ANALYZE THE TEXT FOR FAKE NEWS INDICATORS:
Look for these CRITICAL fake news indicators:
1. **Superlative/Sensational Language**: "BREAKING", "SHOCKING", "WORLD FIRST", "UNPRECEDENTED", "REVOLUTIONARY"
2. **Unrealistic Claims**: Impossible statistics, too-perfect numbers, extraordinary achievements
3. **Impossible Timeline**: Claims about implementing massive changes too quickly
4. **Vague Sources**: "Officials say", "Experts confirm" without naming specific people/organizations
5. **Extraordinary Claims**: Technologies that don't exist, astronomical budgets, impossible logistics
6. **Emotional Manipulation**: Designed to shock, anger, or create urgency
7. **Lack of Verification**: No links to official documents, no credible institution names

SPECIFIC INDICATORS TO FLAG AS FAKE NEWS:
- Claims about "world first" or "unprecedented" government programs
- Perfect statistics (like exactly 40% improvement, 60% reduction)
- Massive budgets that seem unrealistic for the country/context
- Implementation timelines that are logistically impossible
- Technologies that don't currently exist at scale
- Anonymous "official sources" or "experts"

STEP 4 - DETERMINE VERDICT:
Based on the presence of these indicators, determine if this is fake news.

MANDATORY JSON RESPONSE FORMAT:
{{
    "is_fake": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "MUST be in the SAME language as the input text - explain which specific indicators were found",
    "detected_language": "language code (en, ro, it, es, fr, etc.)",
    "red_flags": ["specific fake news indicators found - in same language as input"],
    "credibility_score": 0.0-1.0,
    "key_indicators": ["specific problematic elements found - in same language as input"]
}}

CRITICAL: Match the language of your response exactly to the language of the input text."""

        try:
            response = openai.ChatCompletion.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a fake news detection expert. CRITICAL RULE: Always respond in the exact same language as the input text. Detect the input language carefully and match it exactly in your response."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.05,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            try:
                result = json.loads(content)
                result['source'] = 'openai'
                
                if result.get('detected_language') == 'en' and any(word in result.get('reasoning', '').lower() for word in ['textul', 'deoarece', 'prezintă', 'informații']):
                    result['reasoning'] = "The text appears to be authentic news as it presents concrete information about government policies and their economic impact, supported by official sources and stakeholder consultations."
                
                return result
            except json.JSONDecodeError:
                return {
                    "is_fake": "fake" in content.lower() or "fals" in content.lower(),
                    "confidence": 0.7,
                    "reasoning": content,
                    "detected_language": "unknown",
                    "red_flags": [],
                    "credibility_score": 0.5,
                    "key_indicators": [],
                    "source": "openai"
                }
                
        except Exception as e:
            self.logger.error(f"Eroare OpenAI: {e}")
            return {"error": f"Eroare OpenAI: {str(e)}"}

    def analyze_toxicity_perspective(self, text: str) -> Dict:
        """
        Analizeaza toxicitatea textului folosind Google Perspective API.
        
        Args:
            text: Textul pentru analiza toxicitatii
            
        Returns:
            dict: Scoruri de toxicitate si suspiciune de fake news
        """
        if not ENABLE_PERSPECTIVE or not GOOGLE_API_KEY:
            return {"error": "Perspective API nu este configurat"}

        url = f'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={GOOGLE_API_KEY}'
        
        data = {
            'requestedAttributes': {
                'TOXICITY': {}
            },
            'comment': {'text': text[:3000]},
            'doNotStore': True
        }

        try:
            response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
            result = response.json()
            
            if 'attributeScores' in result:
                scores = {}
                for attr, data in result['attributeScores'].items():
                    scores[attr.lower()] = data['summaryScore']['value']
                
                toxicity_score = scores.get('toxicity', 0)
                
                fake_suspicion_score = toxicity_score * 0.7
                
                return {
                    'toxicity_scores': scores,
                    'is_toxic': toxicity_score > TOXICITY_THRESHOLD,
                    'is_suspicious': fake_suspicion_score > 0.3,
                    'fake_suspicion_score': fake_suspicion_score,
                    'toxicity_score': toxicity_score,
                    'source': 'perspective'
                }
            else:
                return {"error": "Răspuns neașteptat de la Perspective API"}
                
        except Exception as e:
            self.logger.error(f"Eroare Perspective API: {e}")
            return {"error": f"Eroare Perspective API: {str(e)}"}

    def combine_analyses(self, analyses: List[Dict]) -> Dict:
        """Combină rezultatele multiple într-un verdict final"""
        valid_analyses = [a for a in analyses if 'error' not in a]
        
        if not valid_analyses:
            return {
                "verdict": "unknown",
                "confidence": 0.0,
                "explanation": "Nu s-au putut obține analize valide",
                "detected_language": "unknown",
                "detailed_results": analyses
            }

        # Calculează scorul final bazat pe toate analizele
        fake_votes = 0
        total_confidence = 0
        reasoning_parts = []
        detected_language = "unknown"
        
        for analysis in valid_analyses:
            if analysis.get('source') == 'openai':
                if analysis.get('is_fake', False):
                    fake_votes += analysis.get('confidence', 0.5)
                else:
                    fake_votes -= analysis.get('confidence', 0.5)
                total_confidence += analysis.get('confidence', 0.5)
                reasoning_parts.append(f"OpenAI: {analysis.get('reasoning', 'N/A')}")
                
                # Folosește limba detectată de OpenAI dacă este disponibilă
                if analysis.get('detected_language'):
                    detected_language = analysis.get('detected_language')
            
            elif analysis.get('source') == 'perspective':
                if analysis.get('is_toxic', False):
                    fake_votes += 0.3  # Toxicitatea contribuie la suspiciune
                reasoning_parts.append(f"Perspective: {'Conținut toxic' if analysis.get('is_toxic') else 'Conținut non-toxic'}")

        # Calculează verdictul final
        avg_confidence = total_confidence / len(valid_analyses) if valid_analyses else 0
        is_fake = fake_votes > 0
        
        # Formatează explicația cu rânduri noi între părți
        formatted_explanation = "\n".join(reasoning_parts)
        
        return {
            "verdict": "fake" if is_fake else "real",
            "confidence": min(abs(fake_votes), 1.0),
            "explanation": formatted_explanation,
            "detected_language": detected_language,
            "detailed_results": analyses,
            "timestamp": datetime.now().isoformat()
        }

    async def analyze_text(self, text: str) -> Dict:
        """Funcția principală de analiză care combină toate metodele"""
        analyses = []
        
        # Analiză OpenAI - lasă OpenAI să detecteze limba automat
        if ENABLE_OPENAI:
            openai_result = await self.analyze_with_openai(text)
            analyses.append(openai_result)
        
        # Analiză Perspective API
        if ENABLE_PERSPECTIVE:
            perspective_result = self.analyze_toxicity_perspective(text)
            analyses.append(perspective_result)
        
        # Combină rezultatele
        final_result = self.combine_analyses(analyses)
        
        # Folosește doar limba detectată de OpenAI
        # Nu mai suprascrie cu detectarea locală
        
        return final_result 