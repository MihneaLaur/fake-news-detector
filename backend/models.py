from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """
    Model pentru utilizatorii sistemului de detectie fake news.
    
    Atribute:
        username: Numele de utilizator unic
        password: Parola hash-uita
        role: Rolul utilizatorului (user/admin)
        created_at: Data crearii contului
        last_login: Data ultimei autentificari
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relația cu analizele
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        """Reprezentare string pentru obiectul User."""
        return f'<User {self.username}>'
    
    def to_dict(self):
        """
        Converteste obiectul User intr-un dictionar.
        
        Returns:
            dict: Datele utilizatorului serializate
        """
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'total_analyses': len(self.analyses)
        }

class Analysis(db.Model):
    """
    Model pentru stocarea rezultatelor analizelor de fake news.
    
    Atribute:
        content_type: Tipul continutului analizat (text/video/url)
        verdict: Rezultatul analizei (fake/real/deepfake/authentic)
        confidence: Scorul de incredere (0-1)
        analysis_mode: Modul de analiza folosit
    """
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Informații de bază
    content_type = db.Column(db.String(20), nullable=False)  # 'text', 'video', 'url'
    title = db.Column(db.String(200))
    content_preview = db.Column(db.Text)  # Primele 500 caractere
    
    # Rezultate analiză
    verdict = db.Column(db.String(20), nullable=False)  # 'fake', 'real', 'deepfake', 'authentic', 'inconclusive'
    confidence = db.Column(db.Float, nullable=False)
    explanation = db.Column(db.Text)
    
    # Metadata tehnică
    analysis_mode = db.Column(db.String(20), default='traditional')  # 'hybrid', 'ai_only', 'ml_only', 'traditional'
    detected_language = db.Column(db.String(10), default='unknown')
    processing_time = db.Column(db.Float, default=0.0)
    
    # Detalii suplimentare (JSON)
    technical_details = db.Column(db.Text)  # JSON cu detalii tehnice
    risk_level = db.Column(db.String(20))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        """Reprezentare string pentru obiectul Analysis."""
        return f'<Analysis {self.id}: {self.verdict} ({self.confidence:.2f})>'
    
    def to_dict(self):
        """
        Converteste obiectul Analysis intr-un dictionar.
        
        Returns:
            dict: Datele analizei serializate pentru frontend
        """
        return {
            'id': self.id,
            'username': self.user.username,
            'content_type': self.content_type,
            'title': self.title,
            'content_preview': self.content_preview,
            'verdict': self.verdict,
            'confidence': self.confidence,
            'explanation': self.explanation,
            'analysis_mode': self.analysis_mode,
            'detected_language': self.detected_language,
            'processing_time': self.processing_time,
            'technical_details': json.loads(self.technical_details) if self.technical_details else {},
            'risk_level': self.risk_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            # Pentru compatibilitate cu frontend-ul existent
            'tip': self.content_type,
            'titlu': self.title,
            'rezultat': self.verdict,
            'analysisMode': self.analysis_mode,
            'detectedLanguage': self.detected_language,
            'processingTime': self.processing_time,
            'data': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
    def set_technical_details(self, details_dict):
        """
        Salveaza detaliile tehnice ca JSON.
        
        Args:
            details_dict: Dictionarul cu detalii tehnice
        """
        self.technical_details = json.dumps(details_dict) if details_dict else None
    
    def get_technical_details(self):
        """
        Returneaza detaliile tehnice ca dictionar.
        
        Returns:
            dict: Detaliile tehnice deserializate
        """
        return json.loads(self.technical_details) if self.technical_details else {}

class SystemStats(db.Model):
    """
    Model pentru statisticile sistemului pe zi.
    
    Atribute:
        date: Data pentru care sunt statisticile
        total_analyses: Numarul total de analize
        fake_count: Numarul de stiri false detectate
        real_count: Numarul de stiri reale detectate
    """
    __tablename__ = 'system_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow().date, unique=True)
    
    # Statistici zilnice
    total_analyses = db.Column(db.Integer, default=0)
    fake_count = db.Column(db.Integer, default=0)
    real_count = db.Column(db.Integer, default=0)
    deepfake_count = db.Column(db.Integer, default=0)
    authentic_count = db.Column(db.Integer, default=0)
    inconclusive_count = db.Column(db.Integer, default=0)
    
    # Statistici pe moduri
    hybrid_count = db.Column(db.Integer, default=0)
    ai_only_count = db.Column(db.Integer, default=0)
    ml_only_count = db.Column(db.Integer, default=0)
    traditional_count = db.Column(db.Integer, default=0)
    
    # Statistici pe limbă (JSON)
    language_stats = db.Column(db.Text)  # JSON cu distribuția limbilor
    
    # Performanță
    avg_processing_time = db.Column(db.Float, default=0.0)
    avg_confidence = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """
        Converteste obiectul SystemStats intr-un dictionar.
        
        Returns:
            dict: Statisticile serializate
        """
        return {
            'date': self.date.isoformat(),
            'total_analyses': self.total_analyses,
            'fake_count': self.fake_count,
            'real_count': self.real_count,
            'deepfake_count': self.deepfake_count,
            'authentic_count': self.authentic_count,
            'inconclusive_count': self.inconclusive_count,
            'hybrid_count': self.hybrid_count,
            'ai_only_count': self.ai_only_count,
            'ml_only_count': self.ml_only_count,
            'traditional_count': self.traditional_count,
            'language_stats': json.loads(self.language_stats) if self.language_stats else {},
            'avg_processing_time': self.avg_processing_time,
            'avg_confidence': self.avg_confidence
        } 