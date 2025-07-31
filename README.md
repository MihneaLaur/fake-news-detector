# Fake News Detector - Sistem Hibrid AI+ML

## Lucrare de Licență

Sistem hibrid pentru detectarea automată a știrilor false, folosind inteligență artificială și machine learning.

## Caracteristici

- **4 moduri de analiză**: Hibrid, AI, ML, Tradițional
- **Suport multilingv**: 6+ limbi (română, engleză, franceză, etc.)
- **Analiză multimodală**: Text și video
- **Interfață modernă**: React.js cu dashboard interactiv
- **Arhitectură hibridă**: Combină AI (OpenAI, Perspective API) cu ML (BERT, Sentence Transformers)

## Tehnologii

### Frontend
- React.js, HTML, CSS, JavaScript
- Chart.js pentru vizualizări
- Responsive design

### Backend
- Flask (Python)
- SQLite cu SQLAlchemy
- Multiple API-uri externe

### Machine Learning & AI
- scikit-learn pentru modele tradiționale
- Transformers (BERT, Sentence Transformers)
- OpenAI GPT API
- Google Perspective API

## Instalare și Rulare

### Cerințe
- Python 3.8+
- Node.js 14+
- npm sau yarn

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
npm install
npm start
```

### Configurare API Keys (Opțional)
Pentru funcționalitate completă, copiază `config_example.py` ca `config.py` și completează cu cheile tale:
- OpenAI API Key
- Google Perspective API Key

## Structura Proiectului
├── backend/ # Server Flask și logica ML
│ ├── app.py # API principal
│ ├── hybrid_analyzer.py # Sistem hibrid AI+ML
│ ├── ml_analyzer.py # Modele ML
│ ├── ai_analyzer.py # Integrare AI APIs
│ └── models.py # Modele baza de date
├── src/ # Frontend React
│ ├── pages/ # Pagini principale
│ ├── components/ # Componente reutilizabile
│ └── utils/ # Utilitare
└── docs/ # Documentație

## Rezultate

- **Acuratețe hibridă**: 85-95%
- **Suport limbi**: 6+ (română, engleză, franceză, etc.)
- **Timp răspuns**: <5 secunde pentru text, <30 secunde pentru video

## Contribuții Academice

1. **Arhitectură hibridă inovatoare** pentru detectarea fake news
2. **Integrare multimodală** text + video
3. **Sistem de ensemble** cu multiple metodologii
4. **Analiză multilingvă** adaptivă
5. **Framework scalabil** pentru producție

## Autor

[Dănilă Mihnea Laur] - Lucrare de Licență 2024-2025

## Licență

Acest proiect este dezvoltat în cadrul lucrării de licență și este destinat în scopuri academice.
