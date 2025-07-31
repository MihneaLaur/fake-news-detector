"""
Sistem hibrid pentru detectarea fake news care combina AI si ML.
Implementeaza un ensemble de modele pentru analiza completa.
"""

import asyncio
from typing import Dict, List
import logging
from datetime import datetime
import json

from ai_analyzer import AIAnalyzer
from ml_analyzer import MLAnalyzer

class HybridAnalyzer:
    """
    Sistem hibrid pentru detectarea fake news care combina:
    - AI APIs (OpenAI, Perspective)
    - Modele ML pre-antrenate (mBERT, Sentence Transformers)
    - Model traditional (TF-IDF + Logistic Regression)
    """
    
    def __init__(self):
        """Initializeaza sistemul hibrid cu analizoarele AI si ML."""
        self.logger = logging.getLogger(__name__)
        self.ai_analyzer = AIAnalyzer()
        self.ml_analyzer = MLAnalyzer()
        
        # Ponderi pentru sistemul de ensemble
        self.weights = {
            'ai': 0.5,      # 50% pentru analiza AI (OpenAI + Perspective)
            'ml': 0.5       # 50% pentru analiza ML (mBERT + ST + Traditional)
        }

    async def analyze_text(self, text: str, include_details: bool = True) -> Dict:
        """
        Functia principala care realizeaza analiza hibrida completa.
        
        Args:
            text: Textul de analizat
            include_details: Daca sa includa detaliile complete ale fiecarei analize
            
        Returns:
            dict: Rezultatul final si toate detaliile
        """
        start_time = datetime.now()
        
        # Realizează analizele în paralel pentru performanță
        try:
            ai_task = self.ai_analyzer.analyze_text(text)
            ml_task = asyncio.create_task(asyncio.to_thread(self.ml_analyzer.analyze_text, text))
            
            ai_result, ml_result = await asyncio.gather(ai_task, ml_task, return_exceptions=True)
            
            # Verifică dacă au fost excepții
            if isinstance(ai_result, Exception):
                self.logger.error(f"Eroare în analiza AI: {ai_result}")
                ai_result = {"error": str(ai_result), "verdict": "unknown", "confidence": 0.0}
            
            if isinstance(ml_result, Exception):
                self.logger.error(f"Eroare în analiza ML: {ml_result}")
                ml_result = {"error": str(ml_result), "verdict": "unknown", "confidence": 0.0}
                
        except Exception as e:
            self.logger.error(f"Eroare în analiza hibridă: {e}")
            return {
                "error": f"Eroare în sistemul hibrid: {str(e)}",
                "verdict": "unknown",
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat()
            }

        # Combină rezultatele
        final_result = self._ensemble_decision(ai_result, ml_result)
        
        # Calculează timpul de procesare
        processing_time = (datetime.now() - start_time).total_seconds()
        final_result['processing_time_seconds'] = processing_time
        
        # Adaugă detaliile dacă sunt cerute
        if include_details:
            final_result['detailed_analysis'] = {
                'ai_analysis': ai_result,
                'ml_analysis': ml_result
            }
        
        return final_result

    def _ensemble_decision(self, ai_result: Dict, ml_result: Dict) -> Dict:
        """
        Combina rezultatele AI si ML intr-o decizie finala
        folosind un sistem de ensemble ponderat.
        
        Args:
            ai_result: Rezultatul analizei AI
            ml_result: Rezultatul analizei ML
            
        Returns:
            dict: Decizia finala cu metrici combinate
        """
        
        # Extrage scorurile și verdictele
        ai_verdict = ai_result.get('verdict', 'unknown')
        ml_verdict = ml_result.get('verdict', 'unknown')
        
        ai_confidence = ai_result.get('confidence', 0.0)
        ml_confidence = ml_result.get('confidence', 0.0)
        
        # Calculează scorul ponderat pentru "fake"
        ai_fake_score = ai_confidence if ai_verdict == 'fake' else -ai_confidence
        ml_fake_score = ml_confidence if ml_verdict == 'fake' else -ml_confidence
        
        # Aplică ponderile
        weighted_score = (
            self.weights['ai'] * ai_fake_score + 
            self.weights['ml'] * ml_fake_score
        )
        
        # Determină verdictul final
        final_verdict = 'fake' if weighted_score > 0 else 'real'
        
        # Calculează metrici suplimentare
        agreement = ai_verdict == ml_verdict
        
        # Calculează confidența îmbunătățită
        base_confidence = min(abs(weighted_score), 1.0)
        
        # Bonus pentru acord între AI și ML
        if agreement:
            agreement_bonus = 0.15  # +15% pentru acord
            # Bonus suplimentar dacă ambele au confidență mare
            if ai_confidence > 0.7 and ml_confidence > 0.7:
                agreement_bonus += 0.1  # +10% suplimentar
        else:
            agreement_bonus = -0.1  # -10% pentru dezacord
        
        # Bonus pentru confidență mare individuală
        high_confidence_bonus = 0
        if max(ai_confidence, ml_confidence) > 0.8:
            high_confidence_bonus = 0.05
        
        final_confidence = min(base_confidence + agreement_bonus + high_confidence_bonus, 0.95)
        final_confidence = max(final_confidence, 0.5)  # Minimum 50%
        consensus_strength = self._calculate_consensus_strength(ai_result, ml_result)
        
        # Generează explicația
        explanation = self._generate_explanation(ai_result, ml_result, final_verdict, agreement)
        
        # Evaluează riscul
        risk_level = self._assess_risk_level(final_confidence, agreement, consensus_strength)
        
        return {
            'verdict': final_verdict,
            'confidence': final_confidence,
            'risk_level': risk_level,
            'explanation': explanation,
            'ensemble_score': weighted_score,
            'ai_ml_agreement': agreement,
            'consensus_strength': consensus_strength,
            'individual_verdicts': {
                'ai': ai_verdict,
                'ml': ml_verdict
            },
            'individual_confidences': {
                'ai': ai_confidence,
                'ml': ml_confidence
            },
            'detected_language': ml_result.get('detected_language', ai_result.get('detected_language', 'unknown')),
            'timestamp': datetime.now().isoformat()
        }

    def _calculate_consensus_strength(self, ai_result: Dict, ml_result: Dict) -> str:
        """
        Calculeaza puterea consensului intre diferitele analize.
        
        Args:
            ai_result: Rezultatul analizei AI
            ml_result: Rezultatul analizei ML
            
        Returns:
            str: Puterea consensului (strong/moderate/weak/very_weak)
        """
        
        ai_conf = ai_result.get('confidence', 0.0)
        ml_conf = ml_result.get('confidence', 0.0)
        
        avg_confidence = (ai_conf + ml_conf) / 2
        
        if avg_confidence >= 0.8:
            return 'strong'
        elif avg_confidence >= 0.6:
            return 'moderate'
        elif avg_confidence >= 0.4:
            return 'weak'
        else:
            return 'very_weak'

    def _assess_risk_level(self, confidence: float, agreement: bool, consensus_strength: str) -> str:
        """
        Evalueaza nivelul de risc al analizei.
        
        Args:
            confidence: Scorul de incredere final
            agreement: Daca AI si ML sunt de acord
            consensus_strength: Puterea consensului
            
        Returns:
            str: Nivelul de risc (low/medium/high/very_high)
        """
        
        if confidence >= 0.8 and agreement and consensus_strength in ['strong', 'moderate']:
            return 'low'
        elif confidence >= 0.6 and (agreement or consensus_strength != 'very_weak'):
            return 'medium'
        elif confidence >= 0.4:
            return 'high'
        else:
            return 'very_high'

    def _generate_explanation(self, ai_result: Dict, ml_result: Dict, 
                            final_verdict: str, agreement: bool) -> str:
        """
        Genereaza o explicatie comprehensiva a analizei.
        
        Args:
            ai_result: Rezultatul analizei AI
            ml_result: Rezultatul analizei ML
            final_verdict: Verdictul final
            agreement: Daca sistemele sunt de acord
            
        Returns:
            str: Explicatia completa a procesului de analiza
        """
        
        explanation_parts = []
        
        # Status-ul acordului
        if agreement:
            explanation_parts.append(f"✓ Sistemele AI și ML sunt de acord: articolul pare {final_verdict}")
        else:
            ai_verdict = ai_result.get('verdict', 'unknown')
            ml_verdict = ml_result.get('verdict', 'unknown')
            explanation_parts.append(f"⚠ Dezacord: AI consideră '{ai_verdict}', ML consideră '{ml_verdict}'")
        
        # Detalii AI
        if 'explanation' in ai_result and ai_result['explanation']:
            explanation_parts.append(f"🤖 AI: {ai_result['explanation'][:200]}...")
        
        # Detalii ML
        if 'explanation' in ml_result and ml_result['explanation']:
            explanation_parts.append(f"🧠 ML: {ml_result['explanation']}")
        
        # Limba detectată (prioritizează ML peste AI)
        detected_lang = ml_result.get('detected_language', ai_result.get('detected_language'))
        if detected_lang:
            lang_map = {'ro': 'română', 'en': 'engleză', 'fr': 'franceză', 'es': 'spaniolă'}
            lang_name = lang_map.get(detected_lang, detected_lang)
            explanation_parts.append(f"🌐 Limba detectată: {lang_name}")
        
        return " | ".join(explanation_parts)

    def get_system_status(self) -> Dict:
        """Returnează status-ul sistemului hibrid"""
        
        try:
            import config
            ai_enabled = getattr(config, 'ENABLE_OPENAI', False) or getattr(config, 'ENABLE_PERSPECTIVE', False)
            ml_enabled = getattr(config, 'ENABLE_ML_MODELS', True)
        except ImportError:
            ai_enabled = False
            ml_enabled = True  # Presupunem că modelele simple funcționează
        
        return {
            'system_status': 'operational',
            'ai_services': {
                'enabled': ai_enabled,
                'openai': getattr(self.ai_analyzer, 'openai', None) is not None,
                'perspective': True  # Verificare simplificată
            },
            'ml_models': {
                'enabled': ml_enabled,
                'sentence_transformer': self.ml_analyzer.sentence_model is not None,
                'mbert': self.ml_analyzer.classifier_model is not None,
                'traditional': self.ml_analyzer.traditional_model is not None
            },
            'supported_languages': getattr(self, 'SUPPORTED_LANGUAGES', ['ro', 'en', 'fr', 'es']),
            'timestamp': datetime.now().isoformat()
        }

    def get_analysis_statistics(self, analyses: List[Dict]) -> Dict:
        """Calculează statistici despre analizele efectuate"""
        
        if not analyses:
            return {"error": "Nu există analize pentru statistici"}
        
        total = len(analyses)
        fake_count = sum(1 for a in analyses if a.get('verdict') == 'fake')
        real_count = total - fake_count
        
        # Calculează confidența medie
        confidences = [a.get('confidence', 0) for a in analyses]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Calculează acordul AI-ML
        agreements = [a.get('ai_ml_agreement', False) for a in analyses]
        agreement_rate = sum(agreements) / len(agreements) if agreements else 0
        
        # Distribuția limbilor
        languages = [a.get('detected_language', 'unknown') for a in analyses]
        lang_dist = {lang: languages.count(lang) for lang in set(languages)}
        
        return {
            'total_analyses': total,
            'fake_news_detected': fake_count,
            'real_news_detected': real_count,
            'fake_percentage': (fake_count / total * 100) if total > 0 else 0,
            'average_confidence': avg_confidence,
            'ai_ml_agreement_rate': agreement_rate * 100,
            'language_distribution': lang_dist,
            'timestamp': datetime.now().isoformat()
        } 