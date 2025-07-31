"""
Fisier de configurare exemplu pentru sistemul de detectie fake news.
Copiaza acest fisier ca 'config.py' si completeaza cu chei API reale.
"""

# API Keys pentru serviciile AI
OPENAI_API_KEY = "sk-your-openai-api-key-here"
"""str: Cheia API pentru serviciul OpenAI GPT. Obtine de la platform.openai.com"""

ANTHROPIC_API_KEY = "sk-ant-your-anthropic-api-key-here"
"""str: Cheia API pentru serviciul Anthropic Claude. Obtine de la console.anthropic.com"""

GOOGLE_API_KEY = "your-google-api-key-here"
"""str: Cheia API pentru serviciile Google (Perspective API). Obtine de la cloud.google.com"""

# Configurari optionale
DEFAULT_MODEL = "gpt-3.5-turbo"
"""str: Modelul implicit pentru analiza AI (recomandat: gpt-3.5-turbo pentru cost-eficienta)"""

ENABLE_OPENAI = True
"""bool: Activeaza serviciile OpenAI pentru analiza AI avansata"""

ENABLE_ANTHROPIC = False
"""bool: Activeaza serviciile Anthropic Claude (necesita plata)"""

ENABLE_PERSPECTIVE = True
"""bool: Activeaza Google Perspective API pentru detectia toxicitatii"""

ENABLE_ML_MODELS = True
"""bool: Activeaza modelele ML locale (Sentence Transformers, mBERT)"""

# Praguri pentru clasificare
FAKE_NEWS_THRESHOLD = 0.7
"""float: Pragul de confidenta pentru clasificarea fake news (0.0-1.0)"""

TOXICITY_THRESHOLD = 0.6
"""float: Pragul de toxicitate pentru Google Perspective API (0.0-1.0)"""

# Limbi suportate
SUPPORTED_LANGUAGES = ['ro', 'en', 'fr', 'es', 'de', 'it']
"""list: Lista limbilor suportate de sistemul de analiza"""

# Configurari modele
SENTENCE_TRANSFORMER_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
"""str: Modelul Sentence Transformers pentru analiza semantica multilingva"""

MULTILINGUAL_BERT_MODEL = "bert-base-multilingual-cased"
"""str: Modelul mBERT pentru analiza contextuala multilingva""" 