"""
Modul pentru analiza fake news folosind modele de machine learning.
Implementeaza detectia cu Sentence Transformers, mBERT si modele traditionale.
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple
import logging
import pickle
import os
from datetime import datetime
import json

try:
    from config import *
except ImportError:
    SENTENCE_TRANSFORMER_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
    MULTILINGUAL_BERT_MODEL = "bert-base-multilingual-cased"
    ENABLE_ML_MODELS = True
    FAKE_NEWS_THRESHOLD = 0.7

class MLAnalyzer:
    """
    Clasa pentru analiza fake news folosind modele de machine learning.
    Combina Sentence Transformers, mBERT si modele traditionale pentru detectie avansata.
    """
    
    def __init__(self):
        """Initializeaza analizorul ML cu toate modelele disponibile."""
        self.logger = logging.getLogger(__name__)
        self.sentence_model = None
        self.classifier_model = None
        self.tokenizer = None
        self.vectorizer = None
        self.traditional_model = None
        
        if ENABLE_ML_MODELS:
            self._load_models()
        
        self._load_traditional_model()
        
        self.known_fake_news = [
            "Breaking news: The president was replaced by a robot.",
            "Scientists discovered a new species of flying pigs.", 
            "The moon is actually made of cheese, NASA confirms.",
            "Breaking: Aliens landed in New York City last night.",
            "The government is hiding the truth about COVID-19.",
            "Breaking: World War 3 has started in Europe.",
            "Scientists found a cure for all diseases.",
            "The stock market will crash tomorrow, insiders say.",
            "Breaking: The Earth is flat, new evidence shows.",
            
            "Experts agree this revolutionary method changes everything instantly.",
            "New research from prestigious institute proves remarkable breakthrough.",
            "Scientists baffled by incredible results that defy explanation.",
            "Authorities confirm shocking discovery that transforms understanding.",
            "Leading specialists announce unprecedented findings about common practice.",
            "International organization reveals hidden truth about everyday activity.",
            "Top researchers stunned by dramatic improvements using simple technique.",
            "Breakthrough study shows amazing benefits of controversial method.",
            "Renowned experts discover secret that changes lives immediately.",
            "Revolutionary findings prove what authorities don't want you to know.",
            
            "Sources close to the matter confirm shocking revelation.",
            "Insider information reveals government cover-up of major discovery.",
            "Anonymous expert shares secret method that guarantees success.",
            "Confidential report shows incredible results from new approach.",
            "Leaked documents prove authorities have been hiding the truth.",
            
            "Ultimă oră: Președintele a fost înlocuit cu un robot.",
            "Oamenii de știință au descoperit o nouă specie de porci zburători.",
            "Luna este de fapt făcută din brânză, confirmă NASA.",
            "Guvernul ascunde adevărul despre COVID-19.",
            "Experții confirmă această metodă revoluționară schimbă totul.",
            "Cercetare nouă de la institut prestigios dovedește descoperire remarcabilă.",
            "Specialiști de top anunță descoperiri fără precedent despre practică comună."
        ]
        
        self.known_real_news = [
            "Scientists discovered water on Mars.",
            "The stock market showed moderate growth today.",
            "New climate change report shows rising temperatures.",
            "Tech company announces new smartphone features.",
            "Local community raises funds for charity.",
            "Sports team wins championship after close game.",
            "New study shows benefits of regular exercise.",
            "City council approves new infrastructure project.",
            "Scientists develop new renewable energy technology.",
            "Education department announces new curriculum changes.",
            "Oamenii de știință au descoperit apă pe Marte.",
            "Piața de acțiuni a înregistrat o creștere moderată astăzi.",
            "Noul raport privind schimbările climatice arată temperaturi în creștere.",
            "Compania tech anunță noi funcții pentru smartphone.",
            "Comunitatea locală strânge fonduri pentru caritate."
        ]

    def _load_models(self):
        """Incarca modelele pre-antrenate pentru analiza ML."""
        try:
            self.logger.info("Încărcare Sentence Transformer...")
            self.sentence_model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
            
            self.logger.info("Încărcare mBERT pentru clasificare...")
            model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
            self.classifier_model = pipeline(
                "sentiment-analysis", 
                model=model_name,
                tokenizer=model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.logger.info("Modele ML încărcate cu succes!")
            
        except Exception as e:
            self.logger.error(f"Eroare la încărcarea modelelor ML: {e}")
            self.sentence_model = None
            self.classifier_model = None

    def _load_traditional_model(self):
        """Incarca modelul traditional existent sau fallback."""
        try:
            if os.path.exists("simple_large_dataset.json"):
                self.logger.info("📈 Folosesc modelul cu dataset mare (2000 articole)")
                classifier, metadata = load_simple_large_model()
                if classifier:
                    self.traditional_model = classifier
                    self.model_metadata = metadata
                    self.is_simple_model = True
                    self.logger.info(f"Model mare încărcat: {metadata['total_articles']} articole, acuratețe: {metadata['accuracy']:.3f}")
                    return
            
            with open("vectorizer.pkl", "rb") as f:
                self.vectorizer = pickle.load(f)
            with open("model.pkl", "rb") as f:
                self.traditional_model = pickle.load(f)
            self.is_simple_model = False
            self.logger.info("Model tradițional mic încărcat cu succes!")
        except Exception as e:
            self.logger.warning(f"Nu s-a putut încărca modelul tradițional: {e}")
            self.is_simple_model = False

    def analyze_with_sentence_transformer(self, text: str) -> Dict:
        """
        Analiza imbunatatita cu Sentence Transformers pentru detectarea pattern-urilor subtile.
        
        Args:
            text: Textul pentru analiza
            
        Returns:
            dict: Rezultatul analizei cu scor de similaritate si verdict
        """
        if not self.sentence_model:
            return {"error": "Sentence Transformer nu este disponibil"}

        try:
            text_embedding = self.sentence_model.encode([text])
            
            fake_embeddings = self.sentence_model.encode(self.known_fake_news)
            real_embeddings = self.sentence_model.encode(self.known_real_news)
            
            fake_similarities = cosine_similarity(text_embedding, fake_embeddings)[0]
            real_similarities = cosine_similarity(text_embedding, real_embeddings)[0]
            
            max_fake_sim = np.max(fake_similarities)
            max_real_sim = np.max(real_similarities)
            
            subtle_fake_indicators = self._detect_subtle_patterns(text)
            
            base_fake_score = max_fake_sim
            base_real_score = max_real_sim
            
            adjusted_fake_score = base_fake_score + (subtle_fake_indicators['fake_score'] * 0.7)
            adjusted_real_score = base_real_score + (subtle_fake_indicators['real_score'] * 0.2)
            
            is_fake = adjusted_fake_score > adjusted_real_score and adjusted_fake_score > 0.3
            
            if subtle_fake_indicators['pattern_details']['fake_science'] > 1:
                adjusted_fake_score += 0.15
            if subtle_fake_indicators['confidence_bonus'] > 0.08:
                adjusted_fake_score += 0.1
            
            score_difference = abs(adjusted_fake_score - adjusted_real_score)
            max_score = max(adjusted_fake_score, adjusted_real_score)
            
            base_confidence = min(max_score, 0.9)
            
            difference_bonus = min(score_difference * 0.2, 0.15)
            
            subtle_bonus = min(subtle_fake_indicators['confidence_bonus'], 0.1)
            
            final_confidence = min(base_confidence + difference_bonus + subtle_bonus, 0.95)
            final_confidence = max(final_confidence, 0.55)
            
            return {
                "is_fake": is_fake,
                "confidence": final_confidence,
                "fake_similarity": float(max_fake_sim),
                "real_similarity": float(max_real_sim),
                "adjusted_fake_score": float(adjusted_fake_score),
                "adjusted_real_score": float(adjusted_real_score),
                "subtle_indicators": subtle_fake_indicators,
                "most_similar_fake": self.known_fake_news[np.argmax(fake_similarities)],
                "most_similar_real": self.known_real_news[np.argmax(real_similarities)],
                "source": "sentence_transformer"
            }
            
        except Exception as e:
            self.logger.error(f"Eroare Sentence Transformer: {e}")
            return {"error": f"Eroare Sentence Transformer: {str(e)}"}

    def _detect_subtle_patterns(self, text: str) -> Dict:
        """Detectează pattern-uri subtile de fake news cu analiză îmbunătățită"""
        text_lower = text.lower()
        
        # ÎMBUNĂTĂȚIRE MAJORĂ: Pattern-uri pentru afirmații absurde cu aparență științifică
        absurd_scientific_claims = [
            # Afirmații medicale absurde
            'vindecă cancerul în', 'elimină complet diabetul', 'vindecă orice boală',
            'crește iq-ul cu', 'dezvoltă puteri', 'puteri telepatice', 'puteri supranaturale',
            'controlează vremea', 'controlează timpul', 'controlează gravitația',
            'să trăiască 200', 'să trăiască 150', 'să trăiască 100 de ani',
            'energie infinită', 'mișcare perpetuă', 'teleportare', 'citește gândurile',
            'vindecă în 3 zile', 'vindecă în 48 ore', 'vindecă instant',
            'elimină complet', 'vindecă 100%', 'funcționează 100%',
            'prelungește viața cu', 'crește viața cu', 'adaugă ani de viață',
            
            # Afirmații tehnologice absurde
            'cipuri microscopice', 'controlul mental', 'mind control',
            'cipuri în apă', 'cipuri în vaccin', 'tracking chips',
            'tehnologie secretă', 'arme secrete', 'experimente secrete',
            
            # Combinații absurde cu substanțe comune
            'bicarbonatul vindecă', 'oțetul vindecă', 'mierea vindecă totul',
            'apa vindecă', 'aerul vindecă', 'soarele vindecă',
            'berea crește', 'cafeaua vindecă', 'ceaiul elimină',
            'mirositul florilor', 'dormitul cu telefonul', 'privitul la',
            
            # Versiuni în engleză
            'cures cancer in', 'eliminates diabetes completely', 'increases iq by',
            'develops telepathic powers', 'live 200 years', 'live 150 years',
            'microscopic chips', 'mind control chips', 'secret technology'
        ]
        
        # Pattern-uri de exagerare (păstrate din versiunea anterioară)
        exaggeration_patterns = [
            'complet', 'total', 'absolut', 'perfect', 'exact', '100%', 'garantat',
            'revoluționar', 'incredibil', 'șocant', 'uimitor', 'fantastic',
            'completely', 'totally', 'absolutely', 'perfectly', 'guaranteed',
            'revolutionary', 'incredible', 'shocking', 'amazing', 'fantastic'
        ]
        
        # ÎMBUNĂTĂȚIRE: Surse false cu aparență credibilă
        fake_credible_sources = [
            # Instituții false care sună credibil
            'institutul internațional de', 'centrul mondial pentru', 'fundația globală',
            'organizația mondială de', 'institutul avansat de', 'centrul de cercetări avansate',
            'laboratorul secret', 'institutul secret', 'centrul confidențial',
            'international institute of', 'global center for', 'advanced research center',
            'world organization of', 'secret laboratory', 'confidential center',
            
            # Autorități vagi cu universități reale (red flag când e combinat cu afirmații absurde)
            'cercetătorii de la harvard', 'experții de la mit', 'oamenii de știință de la stanford',
            'researchers from harvard', 'experts from mit', 'scientists from stanford',
            
            # Pattern-uri de autoritate falsă
            'experții anonimi', 'surse anonime', 'informatori din interior',
            'doctorii ascund', 'medicii nu vor să știi', 'industria ascunde',
            'anonymous experts', 'anonymous sources', 'inside sources',
            'doctors hide', 'medical industry hides', 'big pharma blocks'
        ]
        
        # Pattern-uri de conspirație (îmbunătățite)
        conspiracy_patterns = [
            'big pharma', 'industria farmaceutică', 'industria medicală',
            'guvernul ascunde', 'guvernele interzic', 'mass-media refuză',
            'industria tech suprimă', 'companiile blochează', 'corporațiile ascund',
            'agenda ascunsă', 'complot mondial', 'conspirația medicală',
            'government hides', 'governments ban', 'mass media refuses',
            'tech industry suppresses', 'companies block', 'corporations hide',
            'hidden agenda', 'global conspiracy', 'medical conspiracy'
        ]
        
        # Pattern-uri de urgență artificială
        urgency_patterns = [
            'urgent!', 'breaking!', 'ultimă oră!', 'atenție!', 'alertă!',
            'acționează acum', 'nu aștepta', 'timpul se scurge', 'înainte să fie prea târziu',
            'urgent!', 'breaking!', 'attention!', 'alert!',
            'act now', 'don\'t wait', 'time running out', 'before it\'s too late'
        ]
        
        # ÎMBUNĂTĂȚIRE: Detectează știința falsă cu aparență credibilă
        fake_science_patterns = [
            # Combinații periculoase: instituție credibilă + afirmație absurdă
            'harvard.*vindecă', 'mit.*elimină', 'stanford.*crește',
            'universitatea.*puteri', 'cercetătorii.*secret', 'studiul.*ascuns',
            'journal.*vindecă', 'research.*elimină', 'scientists.*secret',
            
            # Afirmații medicale false cu aparență științifică
            'studiile dovedesc că.*vindecă', 'cercetarea confirmă că.*elimină',
            'analiza arată că.*crește', 'datele demonstrează că.*dezvoltă',
            'research proves.*cures', 'studies confirm.*eliminates',
            'analysis shows.*increases', 'data demonstrates.*develops',
            
            # Combinații de cuvinte științifice cu afirmații absurde
            'metodă științifică.*secret', 'descoperire medicală.*ascuns',
            'breakthrough.*hidden', 'discovery.*suppressed'
        ]
        
        # Calculează scorurile pentru fiecare categorie (îmbunătățit)
        absurd_score = sum(3 for pattern in absurd_scientific_claims if pattern in text_lower)  # Scor mare pentru absurdități
        exaggeration_score = sum(1 for pattern in exaggeration_patterns if pattern in text_lower)
        fake_credible_score = sum(2 for pattern in fake_credible_sources if pattern in text_lower)
        conspiracy_score = sum(1 for pattern in conspiracy_patterns if pattern in text_lower)
        urgency_score = sum(1 for pattern in urgency_patterns if pattern in text_lower)
        fake_science_score = sum(2 for pattern in fake_science_patterns if pattern in text_lower)
        
        # ÎMBUNĂTĂȚIRE: Detectează combinații generale suspecte de pattern-uri
        combination_bonus = 0
        
        # BONUS MAJOR: Afirmații absurde cu surse credibile (cel mai periculos pattern)
        if absurd_score > 0 and ('harvard' in text_lower or 'mit' in text_lower or 'stanford' in text_lower or 'cercetătorii' in text_lower):
            combination_bonus += 3.0  # Bonus foarte mare
            
        # Bonus pentru combinația autoritate vagă + afirmații exagerate
        if fake_science_score > 0 and exaggeration_score > 0:
            combination_bonus += 2.0
            
        # Bonus pentru urgență + autoritate falsă
        if urgency_score > 0 and fake_credible_score > 0:
            combination_bonus += 1.5
            
        # Bonus pentru conspirație + exagerare
        if conspiracy_score > 0 and exaggeration_score > 0:
            combination_bonus += 1.4
            
        # Bonus pentru pattern-uri multiple de exagerare
        if exaggeration_score >= 3:
            combination_bonus += 1.0
            
        # ÎMBUNĂTĂȚIRE: Calculează scorul total de suspiciune cu bonusuri
        total_fake_indicators = (
            absurd_score * 3.5 +            # Afirmațiile absurde sunt cel mai important indicator
            exaggeration_score * 1.8 +      # Exagerările sunt foarte suspecte
            fake_credible_score * 2.5 +     # Sursele false cu aparență credibilă
            urgency_score * 1.5 +           # Urgența artificială e suspectă
            conspiracy_score * 2.0 +        # Teoriile conspirației sunt foarte suspecte
            fake_science_score * 2.8 +      # Știința falsă e foarte suspectă
            combination_bonus               # Bonus pentru combinații periculoase
        )
        
        # Pattern-uri pentru credibilitate reală (îmbunătățite)
        credible_patterns = [
            # Surse oficiale concrete
            'ministerul', 'primăria', 'guvernul român', 'parlamentul',
            'comisia europeană', 'organizația mondială a sănătății',
            'ministry', 'government', 'parliament', 'european commission',
            'world health organization', 'official statement',
            
            # Limbaj științific real
            'conform studiului', 'potrivit cercetării', 'datele arată',
            'statisticile indică', 'analiza dezvăluie', 'raportul confirmă',
            'according to study', 'research indicates', 'data shows',
            'statistics indicate', 'analysis reveals', 'report confirms',
            
            # Contexte normale de știri
            'ieri', 'astăzi', 'săptămâna trecută', 'luna aceasta',
            'prețul', 'temperatura', 'traficul', 'lucrările',
            'yesterday', 'today', 'last week', 'this month',
            'price', 'temperature', 'traffic', 'construction'
        ]
        
        credible_score = sum(1 for pattern in credible_patterns if pattern in text_lower)
        
        # ÎMBUNĂTĂȚIRE: Calculează scorurile finale cu sensibilitate crescută pentru absurdități
        fake_score = min(total_fake_indicators / 12.0, 0.8)  # Normalizat la 0-0.8 (mai sensibil pentru absurdități)
        real_score = min(credible_score / 5.0, 0.3)  # Normalizat la 0-0.3
        
        # ÎMBUNĂTĂȚIRE: Calculează bonus de confidență îmbunătățit
        confidence_bonus = min(total_fake_indicators / 15.0, 0.2)  # Bonus mai mare pentru detectarea absurdităților
        
        # Bonus suplimentar pentru fake news foarte subtile cu afirmații absurde
        if absurd_score > 0:
            confidence_bonus += 0.1  # Bonus mare pentru absurdități
        if fake_science_score > 0 and exaggeration_score > 0:
            confidence_bonus += 0.08
        if combination_bonus > 2.0:  # Combinații foarte periculoase
            confidence_bonus += 0.12
        
        return {
            'fake_score': fake_score,
            'real_score': real_score,
            'confidence_bonus': confidence_bonus,
            'pattern_details': {
                'absurd_claims': absurd_score,
                'exaggeration': exaggeration_score,
                'fake_credible_sources': fake_credible_score,
                'artificial_urgency': urgency_score,
                'conspiracy': conspiracy_score,
                'fake_science': fake_science_score,
                'credible_indicators': credible_score,
                'combination_bonus': combination_bonus
            }
        }

    def analyze_with_mbert(self, text: str) -> Dict:
        """Analiză îmbunătățită cu mBERT pentru detectarea manipulării lingvistice"""
        if not self.classifier_model:
            return {"error": "mBERT classifier nu este disponibil"}

        try:
            # Analiză de sentiment de bază
            result = self.classifier_model(text[:512])  # Limită la 512 tokeni
            
            label = result[0]['label']
            score = result[0]['score']
            
            # ÎMBUNĂTĂȚIRE: Analiză lingvistică avansată
            linguistic_analysis = self._analyze_linguistic_manipulation(text)
            
            # Interpretează rezultatul sentiment combinat cu analiza lingvistică
            base_suspicion = 0.0
            reasoning_parts = []
            
            # Analiza sentimentului
            if label in ['POSITIVE', 'NEGATIVE'] and score > 0.9:
                base_suspicion += 0.3
                reasoning_parts.append(f"Sentiment extrem de {label.lower()} (scor: {score:.2f})")
            elif label in ['POSITIVE', 'NEGATIVE'] and score > 0.8:
                base_suspicion += 0.15
                reasoning_parts.append(f"Sentiment puternic {label.lower()} (scor: {score:.2f})")
            
            # Adaugă suspiciunea din analiza lingvistică
            base_suspicion += linguistic_analysis['manipulation_score']
            reasoning_parts.extend(linguistic_analysis['reasoning'])
            
            # Determină dacă e suspect
            is_suspicious = base_suspicion > 0.4
            
            # Calculează confidența finală
            confidence = min(base_suspicion + 0.5, 0.95) if is_suspicious else min(1.0 - base_suspicion, 0.9)
            confidence = max(confidence, 0.55)
            
            reasoning = "; ".join(reasoning_parts) if reasoning_parts else f"Tonul este {label.lower()} moderat"
            
            return {
                "is_suspicious": is_suspicious,
                "sentiment_label": label,
                "sentiment_score": float(score),
                "manipulation_score": linguistic_analysis['manipulation_score'],
                "linguistic_flags": linguistic_analysis['flags'],
                "confidence": float(confidence),
                "reasoning": reasoning,
                "source": "mbert"
            }
            
        except Exception as e:
            self.logger.error(f"Eroare mBERT: {e}")
            return {"error": f"Eroare mBERT: {str(e)}"}

    def _analyze_linguistic_manipulation(self, text: str) -> Dict:
        """Analizează manipularea lingvistică în text"""
        manipulation_score = 0.0
        flags = []
        reasoning = []
        
        # Verifică lungimea propozițiilor (propoziții foarte lungi pot indica manipulare)
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        if avg_sentence_length > 25:
            manipulation_score += 0.1
            flags.append('long_sentences')
            reasoning.append('Propoziții neobișnuit de lungi')
        
        # Verifică folosirea excesivă a adjectivelor superlative și de intensificare
        superlatives = ['best', 'worst', 'most', 'least', 'greatest', 'smallest', 'highest', 'lowest',
                       'only', 'perfect', 'ultimate', 'absolute', 'complete', 'total', 'entire',
                       'cel mai bun', 'cel mai rău', 'cel mai mare', 'cel mai mic', 'cel mai înalt',
                       'singurul', 'perfect', 'ultim', 'absolut', 'complet', 'total']
        superlative_count = sum(1 for word in superlatives if word in text.lower())
        
        if superlative_count > 2:  # Prag redus pentru mai multă sensibilitate
            manipulation_score += 0.18
            flags.append('excessive_superlatives')
            reasoning.append(f'Limbaj superlativ exagerat ({superlative_count} termeni)')
        
        # Verifică cuvinte emoționale puternice și de manipulare
        emotional_words = ['shocking', 'amazing', 'incredible', 'unbelievable', 'devastating', 'terrifying',
                          'stunning', 'mind-blowing', 'extraordinary', 'phenomenal', 'miraculous',
                          'outrageous', 'scandalous', 'explosive', 'bombshell', 'sensational',
                          'șocant', 'uimitor', 'incredibil', 'de necrezut', 'devastator', 'terifiant',
                          'extraordinar', 'fenomenal', 'miraculos', 'scandulos', 'senzațional']
        emotional_count = sum(1 for word in emotional_words if word in text.lower())
        
        if emotional_count > 1:  # Prag redus pentru mai multă sensibilitate
            manipulation_score += 0.15
            flags.append('emotional_manipulation')
            reasoning.append(f'Limbaj emoțional manipulativ ({emotional_count} cuvinte)')
            
        # Verifică adverbe de intensificare excesivă
        intensifiers = ['extremely', 'incredibly', 'absolutely', 'completely', 'totally', 'perfectly',
                       'dramatically', 'significantly', 'remarkably', 'extraordinarily', 'phenomenally',
                       'extrem de', 'incredibil de', 'absolut', 'complet', 'total', 'perfect',
                       'dramatic', 'semnificativ', 'remarcabil', 'extraordinar']
        intensifier_count = sum(1 for word in intensifiers if word in text.lower())
        
        if intensifier_count > 2:
            manipulation_score += 0.12
            flags.append('excessive_intensifiers')
            reasoning.append(f'Adverbe de intensificare excesive ({intensifier_count})')
        
        # Verifică folosirea excesivă a majusculelor
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.1:  # Peste 10% majuscule
            manipulation_score += 0.08
            flags.append('excessive_caps')
            reasoning.append('Folosire excesivă a majusculelor')
        
        # Verifică punctuația excesivă
        exclamation_count = text.count('!')
        question_count = text.count('?')
        
        if exclamation_count > 3 or question_count > 5:
            manipulation_score += 0.1
            flags.append('excessive_punctuation')
            reasoning.append('Punctuație excesivă pentru efect dramatic')
        
        return {
            'manipulation_score': min(manipulation_score, 0.5),
            'flags': flags,
            'reasoning': reasoning
        }

    def analyze_with_traditional_ml(self, text: str) -> Dict:
        """Analiză cu modelul tradițional existent"""
        if not self.traditional_model:
            return {"error": "Model tradițional nu este disponibil"}

        try:
            # Verifică dacă folosim modelul simplu mare
            if hasattr(self, 'is_simple_model') and self.is_simple_model:
                pred, confidence = self.traditional_model(text)
                is_fake = pred == 1
                
                return {
                    "is_fake": is_fake,
                    "confidence": float(confidence),
                    "fake_probability": float(confidence) if is_fake else float(1 - confidence),
                    "real_probability": float(1 - confidence) if is_fake else float(confidence),
                    "source": "traditional_ml_large",
                    "model_size": self.model_metadata.get('total_articles', 'unknown') if hasattr(self, 'model_metadata') else 'unknown'
                }
            
            # Folosește modelul tradițional sklearn
            if not self.vectorizer:
                return {"error": "Vectorizer nu este disponibil"}
                
            X = self.vectorizer.transform([text])
            pred = self.traditional_model.predict(X)[0]
            proba = self.traditional_model.predict_proba(X)[0]
            
            confidence = float(np.max(proba))
            is_fake = pred == 1
            
            return {
                "is_fake": is_fake,
                "confidence": confidence,
                "fake_probability": float(proba[1]) if len(proba) > 1 else 0.5,
                "real_probability": float(proba[0]) if len(proba) > 1 else 0.5,
                "source": "traditional_ml_small"
            }
            
        except Exception as e:
            self.logger.error(f"Eroare model tradițional: {e}")
            return {"error": f"Eroare model tradițional: {str(e)}"}

    def combine_ml_analyses(self, analyses: List[Dict]) -> Dict:
        """Combină rezultatele din toate modelele ML cu analiză îmbunătățită"""
        valid_analyses = [a for a in analyses if 'error' not in a]
        
        if not valid_analyses:
            return {
                "verdict": "unknown",
                "confidence": 0.0,
                "explanation": "Nu s-au putut obține analize valide",
                "source": "ml_combined"
            }
        
        # Extrage rezultatele din fiecare model
        sentence_results = next((a for a in valid_analyses if a.get('source') == 'sentence_transformer'), None)
        mbert_results = next((a for a in valid_analyses if a.get('source') == 'mbert'), None)
        traditional_results = next((a for a in valid_analyses if a.get('source') in ['traditional_ml_small', 'traditional_ml_large']), None)
        
        # Inițializează scorurile
        fake_votes = 0
        real_votes = 0
        confidence_sum = 0
        model_count = 0
        
        # Procesează rezultatele Sentence Transformer îmbunătățite (pondere mare)
        if sentence_results:
            weight = 2.0  # Pondere dublă pentru similaritate semantică
            if sentence_results.get('is_fake'):
                fake_votes += weight
                # ÎMBUNĂTĂȚIRE: Bonus mare pentru afirmații absurde detectate
                subtle_indicators = sentence_results.get('subtle_indicators', {})
                pattern_details = subtle_indicators.get('pattern_details', {})
                
                # Bonus foarte mare pentru afirmații absurde
                if pattern_details.get('absurd_claims', 0) > 0:
                    fake_votes += 2.0  # Bonus foarte mare pentru absurdități
                elif subtle_indicators.get('fake_score', 0) > 0.3:
                    fake_votes += 1.0  # Bonus pentru pattern-uri puternice
                elif subtle_indicators.get('fake_score', 0) > 0.2:
                    fake_votes += 0.5  # Bonus pentru pattern-uri moderate
            else:
                real_votes += weight
            confidence_sum += sentence_results['confidence'] * weight
            model_count += weight
        
        # Procesează rezultatele mBERT îmbunătățite (pondere normală)
        if mbert_results:
            weight = 1.0
            if mbert_results.get('is_suspicious'):
                fake_votes += weight
                # Bonus pentru manipulare lingvistică detectată
                manipulation_score = mbert_results.get('manipulation_score', 0)
                if manipulation_score > 0.3:
                    fake_votes += 0.3  # Bonus pentru manipulare puternică
            else:
                real_votes += weight
            confidence_sum += mbert_results['confidence'] * weight
            model_count += weight
        
        # Procesează rezultatele modelului tradițional (pondere redusă)
        if traditional_results:
            weight = 0.8  # Pondere mai mică pentru modelul tradițional
            if traditional_results.get('is_fake'):
                fake_votes += weight
            else:
                real_votes += weight
            confidence_sum += traditional_results['confidence'] * weight
            model_count += weight
        
        # Determină verdictul final
        is_fake = fake_votes > real_votes
        
        # Calculează confidența îmbunătățită cu noile metrici
        if model_count > 0:
            base_confidence = confidence_sum / model_count
            
            # Bonus pentru consens puternic
            vote_ratio = max(fake_votes, real_votes) / (fake_votes + real_votes) if (fake_votes + real_votes) > 0 else 0.5
            consensus_bonus = (vote_ratio - 0.5) * 0.4  # Până la +20% bonus
            
            # Bonus pentru multiple modele de acord
            model_agreement_bonus = 0.1 if model_count >= 3 else 0.05
            
            # Bonus pentru detectarea pattern-urilor subtile și absurdităților
            subtle_pattern_bonus = 0.0
            if sentence_results and sentence_results.get('subtle_indicators'):
                pattern_details = sentence_results['subtle_indicators'].get('pattern_details', {})
                pattern_strength = sentence_results['subtle_indicators'].get('fake_score', 0)
                
                # Bonus foarte mare pentru afirmații absurde
                if pattern_details.get('absurd_claims', 0) > 0:
                    subtle_pattern_bonus = 0.15  # Bonus foarte mare
                elif pattern_strength > 0.3:
                    subtle_pattern_bonus = 0.08
            
            # Bonus pentru manipulare lingvistică
            linguistic_bonus = 0.0
            if mbert_results and mbert_results.get('manipulation_score', 0) > 0.3:
                linguistic_bonus = 0.06
            
            final_confidence = min(
                base_confidence + consensus_bonus + model_agreement_bonus + 
                subtle_pattern_bonus + linguistic_bonus, 0.95
            )
            
            # Asigură-te că confidența nu e prea mică
            final_confidence = max(final_confidence, 0.65)
        else:
            final_confidence = 0.5
        
        # Construiește explicația îmbunătățită
        explanation_parts = []
        
        if sentence_results:
            base_sim = f"Similaritate: {sentence_results['fake_similarity']:.2f} fake vs {sentence_results['real_similarity']:.2f} real"
            if sentence_results.get('subtle_indicators'):
                patterns = sentence_results['subtle_indicators']['pattern_details']
                pattern_info = []
                
                # PRIORITIZEAZĂ afirmațiile absurde în explicație
                if patterns.get('absurd_claims', 0) > 0:
                    pattern_info.append(f"AFIRMAȚII ABSURDE: {patterns['absurd_claims']}")
                
                if patterns.get('exaggeration', 0) > 0:
                    pattern_info.append(f"exagerări: {patterns['exaggeration']}")
                if patterns.get('fake_credible_sources', 0) > 0:
                    pattern_info.append(f"surse false credibile: {patterns['fake_credible_sources']}")
                if patterns.get('conspiracy', 0) > 0:
                    pattern_info.append(f"conspirații: {patterns['conspiracy']}")
                if patterns.get('fake_science', 0) > 0:
                    pattern_info.append(f"știință falsă: {patterns['fake_science']}")
                
                if pattern_info:
                    base_sim += f" (pattern-uri: {', '.join(pattern_info)})"
            explanation_parts.append(base_sim)
        
        if mbert_results:
            mbert_info = f"mBERT: {mbert_results['reasoning']}"
            if mbert_results.get('linguistic_flags'):
                flags = mbert_results['linguistic_flags']
                if flags:
                    mbert_info += f" (indicatori: {', '.join(flags)})"
            explanation_parts.append(mbert_info)
        
        if traditional_results:
            explanation_parts.append(f"Model tradițional: {traditional_results.get('confidence', 0):.2f} confidență")
        
        explanation = "; ".join(explanation_parts)
        
        return {
            "verdict": "fake" if is_fake else "real",
            "confidence": final_confidence,
            "explanation": explanation,
            "source": "ml_combined",
            "individual_scores": {
                "fake_votes": fake_votes,
                "real_votes": real_votes,
                "consensus_strength": vote_ratio
            },
            "pattern_analysis": {
                "subtle_patterns_detected": sentence_results.get('subtle_indicators', {}).get('pattern_details', {}) if sentence_results else {},
                "linguistic_manipulation": mbert_results.get('linguistic_flags', []) if mbert_results else []
            }
        }

    def analyze_text(self, text: str) -> Dict:
        """Funcția principală de analiză ML care combină toate metodele"""
        analyses = []
        
        # Detectează limba textului
        detected_language = self._detect_language(text)
        
        # Analiză cu Sentence Transformer
        st_result = self.analyze_with_sentence_transformer(text)
        analyses.append(st_result)
        
        # Analiză cu mBERT
        mbert_result = self.analyze_with_mbert(text)
        analyses.append(mbert_result)
        
        # Analiză cu modelul tradițional
        traditional_result = self.analyze_with_traditional_ml(text)
        analyses.append(traditional_result)
        
        # Combină rezultatele
        final_result = self.combine_ml_analyses(analyses)
        
        # Adaugă limba detectată
        final_result['detected_language'] = detected_language
        
        return final_result
    
    def _detect_language(self, text: str) -> str:
        """Detectează limba textului folosind heuristici simple"""
        try:
            from langdetect import detect
            return detect(text)
        except:
            # Fallback la detecție heuristică
            text_lower = text.lower()
            
            # Cuvinte caracteristice românești
            ro_words = ['și', 'sau', 'este', 'sunt', 'pentru', 'cu', 'de', 'la', 'în', 'pe', 'că', 'să', 'nu', 'se', 'ce', 'mai', 'foarte', 'după', 'până', 'către', 'asupra', 'dintre', 'printre']
            
            # Cuvinte caracteristice engleze
            en_words = ['the', 'and', 'or', 'is', 'are', 'for', 'with', 'of', 'at', 'in', 'on', 'that', 'to', 'not', 'what', 'more', 'very', 'after', 'until', 'towards', 'among', 'between']
            
            ro_count = sum(1 for word in ro_words if word in text_lower)
            en_count = sum(1 for word in en_words if word in text_lower)
            
            if ro_count > en_count and ro_count > 2:
                return 'ro'
            elif en_count > ro_count and en_count > 2:
                return 'en'
            else:
                return 'unknown' 

    def analyze_news(self, text: str) -> Dict:
        """
        Funcția principală pentru analiza știrilor - interfață compatibilă cu aplicația
        
        Returns:
            Dict cu format standardizat: classification, confidence, language, fake_votes, real_votes
        """
        # Folosește analiza completă
        result = self.analyze_text(text)
        
        # Convertește la formatul așteptat de aplicație
        classification = "FAKE" if result.get('verdict') == 'fake' else "REAL"
        confidence = result.get('confidence', 0.5) * 100  # Convertește la procente
        language = result.get('detected_language', 'unknown')
        
        # Extrage voturile din scorurile individuale
        individual_scores = result.get('individual_scores', {})
        fake_votes = individual_scores.get('fake_votes', 0)
        real_votes = individual_scores.get('real_votes', 0)
        
        return {
            'classification': classification,
            'confidence': confidence,
            'language': language,
            'fake_votes': fake_votes,
            'real_votes': real_votes,
            'explanation': result.get('explanation', ''),
            'pattern_analysis': result.get('pattern_analysis', {}),
            'detailed_analysis': {
                'verdict': result.get('verdict'),
                'source': result.get('source'),
                'individual_scores': individual_scores
            }
        }

def load_traditional_model():
    """Încarcă modelul tradițional de ML"""
    try:
        # Încearcă să încărce modelul cu dataset mare
        if os.path.exists("simple_large_dataset.json"):
            print("📈 Folosesc modelul cu dataset mare (2000 articole)")
            return load_simple_large_model()
        
        # Fallback la modelul mic
        with open("vectorizer.pkl", "rb") as f:
            vectorizer = pickle.load(f)
        with open("model.pkl", "rb") as f:
            model = pickle.load(f)
        
        print("📊 Modelul tradițional ML încărcat (dataset mic)")
        return vectorizer, model
    except Exception as e:
        print(f"❌ Eroare la încărcarea modelului ML: {e}")
        return None, None

def load_simple_large_model():
    """Încarcă modelul simplu cu dataset mare"""
    try:
        with open("simple_large_dataset.json", "r", encoding='utf-8') as f:
            dataset = json.load(f)
        
        with open("simple_model_metadata.json", "r", encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"✅ Model mare încărcat: {metadata['total_articles']} articole, acuratețe: {metadata['accuracy']:.3f}")
        
        # Returnează funcția de clasificare îmbunătățită pentru detectarea subtilă
        def simple_classifier(text):
            # Încarcă cuvintele din fișierul de keywords
            try:
                with open("enhanced_keywords.json", "r", encoding='utf-8') as f:
                    keywords_data = json.load(f)
                
                fake_keywords = keywords_data['fake_keywords']
                real_keywords = keywords_data['real_keywords']
                
            except Exception as e:
                # Fallback la cuvinte de bază dacă fișierul nu există
                fake_keywords = [
                    'breaking', 'urgent', 'shocking', 'secret', 'conspiracy', 'hoax',
                    'ultimă oră fals', 'conspirație', 'minciună', 'fals'
                ]
                real_keywords = [
                    'research', 'study', 'analysis', 'experts', 'officials', 'data',
                    'cercetare', 'studiu', 'analiză', 'experți', 'oficiali', 'date'
                ]
            
            text_lower = text.lower()
            
            # ÎMBUNĂTĂȚIRE: Analiză mai sofisticată pentru fake news subtile
            
            # 1. Calculează scorurile de bază pentru keywords
            fake_score = 0
            real_score = 0
            
            # Scoruri ponderate pentru keywords
            for keyword in fake_keywords:
                if keyword in text_lower:
                    # Pondere mai mare pentru keywords mai specifici
                    if len(keyword) > 10:  # Keywords lungi sunt mai specifici
                        fake_score += 2
                    else:
                        fake_score += 1
            
            for keyword in real_keywords:
                if keyword in text_lower:
                    if len(keyword) > 10:
                        real_score += 2
                    else:
                        real_score += 1
            
            # 2. Detectează pattern-uri generale de exagerare și manipulare
            subtle_fake_patterns = [
                # Pattern-uri de exagerare generală
                'completely', 'totally', 'absolutely', 'perfectly', 'exactly',
                'instantly', 'immediately', 'suddenly', 'dramatically', 'massively',
                'revolutionary', 'groundbreaking', 'unprecedented', 'extraordinary', 'incredible',
                'shocking', 'stunning', 'amazing', 'remarkable', 'outstanding',
                'never seen before', 'first time ever', 'only solution', 'best ever',
                'guaranteed', 'proven', 'confirmed', 'established', 'demonstrated',
                
                # Pattern-uri de urgență artificială  
                'breaking', 'urgent', 'immediate', 'emergency', 'crisis',
                'act now', 'limited time', 'don\'t wait', 'hurry', 'quickly',
                'before it\'s too late', 'last chance', 'final warning', 'deadline',
                
                # Pattern-uri de autoritate falsă
                'experts agree', 'scientists confirm', 'studies prove', 'research shows',
                'according to experts', 'leading authorities', 'top specialists', 'renowned',
                'prestigious', 'leading', 'world-class', 'internationally recognized',
                
                # Pattern-uri de conspirație subtile
                'they don\'t want you to know', 'hidden truth', 'secret information',
                'cover up', 'suppressed', 'censored', 'banned', 'forbidden',
                'mainstream media won\'t tell you', 'government doesn\'t want',
                
                # Versiuni în română
                'complet', 'total', 'absolut', 'perfect', 'exact',
                'instant', 'imediat', 'brusc', 'dramatic', 'masiv',
                'revoluționar', 'revoluționar', 'fără precedent', 'extraordinar',
                'ultimă oră', 'urgent', 'imediat', 'criză', 'acționează',
                'experții confirmă', 'studiile dovedesc', 'cercetările arată'
            ]
            
            # 3. Detectează surse vagi și credibilitate suspectă
            dubious_sources = [
                # Surse anonime/vagi
                'anonymous source', 'unnamed expert', 'confidential report', 'insider information',
                'leaked documents', 'whistleblower reveals', 'off-the-record', 'sources say',
                'according to sources', 'reliable sources', 'inside sources', 'trusted sources',
                
                # Autorități vagi
                'experts', 'specialists', 'authorities', 'officials', 'insiders',
                'top people', 'those in the know', 'industry leaders', 'key figures',
                
                # Organizații vagi sau false
                'international organization', 'global foundation', 'research institute',
                'prestigious university', 'leading center', 'advanced facility',
                'renowned organization', 'world-class institute', 'top-rated center',
                
                # Pattern-uri de temporalitate suspectă
                'will soon reveal', 'about to announce', 'preparing to release',
                'plans to publish', 'expected to confirm', 'will shortly disclose',
                
                # Afirmații absolute fără dovezi
                'it\'s proven that', 'everyone knows', 'it\'s obvious that',
                'common knowledge', 'well established', 'widely accepted',
                
                # Versiuni în română
                'sursă anonimă', 'expert neidentificat', 'raport confidențial', 'informații din interior',
                'documente scurse', 'informator dezvăluie', 'organizație internațională',
                'institut de cercetare', 'universitate prestigioasă', 'centru de cercetare'
            ]
            
            # 4. Detectează urgență artificială
            artificial_urgency = [
                'breaking news', 'urgent', 'act now', 'don\'t wait', 'time running out',
                'limited time', 'exclusive offer', 'once in a lifetime',
                'ultimă oră', 'urgent', 'acționează acum', 'nu aștepta', 'timpul se scurge',
                'timp limitat', 'ofertă exclusivă', 'o dată în viață'
            ]
            
            # 5. Detectează conspirații
            conspiracy_indicators = [
                'government control', 'mind control', 'cover-up', 'suppresses truth', 'hidden agenda',
                'they don\'t want you to know', 'mainstream media', 'big pharma',
                'guvernul controlează', 'controlul minții', 'mușamalizare', 'suprimă adevărul',
                'agende ascunse', 'nu vor să știi', 'media mainstream'
            ]
            
            # Calculează scorurile pentru pattern-uri subtile
            subtle_score = sum(2 for pattern in subtle_fake_patterns if pattern in text_lower)
            dubious_score = sum(3 for pattern in dubious_sources if pattern in text_lower)  # Pondere mare
            urgency_score = sum(1.5 for pattern in artificial_urgency if pattern in text_lower)
            conspiracy_score = sum(2.5 for pattern in conspiracy_indicators if pattern in text_lower)
            
            # Adaugă scorurile subtile la scorul fake
            fake_score += subtle_score + dubious_score + urgency_score + conspiracy_score
            
            # 6. Detectează indicatori de credibilitate
            credibility_indicators = [
                'according to', 'data shows', 'statistics indicate', 'research suggests',
                'experts say', 'officials confirm', 'study finds', 'analysis reveals',
                'published in', 'peer-reviewed', 'university study', 'scientific journal',
                'conform cu', 'datele arată', 'statisticile indică', 'cercetarea sugerează',
                'experții spun', 'oficialii confirmă', 'studiul găsește', 'analiza dezvăluie',
                'publicat în', 'evaluat de colegi', 'studiu universitar', 'revistă științifică'
            ]
            
            credibility_score = sum(1.5 for indicator in credibility_indicators if indicator in text_lower)
            real_score += credibility_score
            
            # 7. Analiză lingvistică pentru manipulare
            manipulation_indicators = 0
            
            # Verifică folosirea excesivă a majusculelor
            caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
            if caps_ratio > 0.1:  # Peste 10% majuscule
                manipulation_indicators += 2
            
            # Verifică punctuația excesivă
            exclamation_count = text.count('!')
            if exclamation_count > 3:
                manipulation_indicators += 1.5
            
            # Verifică cuvinte emoționale puternice
            emotional_words = ['shocking', 'amazing', 'incredible', 'unbelievable', 'devastating',
                             'șocant', 'uimitor', 'incredibil', 'de necrezut', 'devastator']
            emotional_count = sum(1 for word in emotional_words if word in text_lower)
            if emotional_count > 2:
                manipulation_indicators += emotional_count
            
            fake_score += manipulation_indicators
            
            # 8. Calculează confidența îmbunătățită
            total_indicators = fake_score + real_score
            
            if fake_score > real_score:
                # Calculează confidența bazată pe diferența și puterea indicatorilor
                score_difference = fake_score - real_score
                base_confidence = min(0.5 + (score_difference / max(total_indicators, 1)) * 0.4, 0.95)
                
                # Bonus pentru pattern-uri multiple
                if subtle_score > 0 and dubious_score > 0:
                    base_confidence += 0.05
                if conspiracy_score > 0 and manipulation_indicators > 0:
                    base_confidence += 0.05
                
                confidence = max(0.65, min(0.95, base_confidence))
                return 1, confidence  # fake
                
            elif real_score > fake_score:
                score_difference = real_score - fake_score
                base_confidence = min(0.5 + (score_difference / max(total_indicators, 1)) * 0.4, 0.95)
                
                # Bonus pentru indicatori de credibilitate multipli
                if credibility_score > 3:
                    base_confidence += 0.05
                
                confidence = max(0.65, min(0.95, base_confidence))
                return 0, confidence  # real
                
            else:
                # Heuristici îmbunătățite pentru egalitate
                if manipulation_indicators > 2:
                    return 1, 0.70  # fake (manipulare detectată)
                elif credibility_score > 0:
                    return 0, 0.75  # real (indicatori de credibilitate)
                elif len(text) > 200 and any(word in text_lower for word in ['study', 'research', 'analysis', 'studiu', 'cercetare', 'analiză']):
                    return 0, 0.70  # real (conținut academic lung)
                elif any(word in text_lower for word in ['breaking', 'urgent', 'shocking', 'ultimă oră']):
                    return 1, 0.68  # fake (limbaj senzațional)
                else:
                    return 0, 0.65  # real (default conservativ)
        
        return simple_classifier, metadata
        
    except Exception as e:
        print(f"❌ Eroare la încărcarea modelului mare: {e}")
        return None, None 