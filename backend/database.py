import os
import json
from datetime import datetime, date
from models import db, User, Analysis, SystemStats
from werkzeug.security import generate_password_hash

def init_database(app):
    """
    Initializeaza baza de date cu aplicatia Flask.
    
    Args:
        app: Instanta aplicatiei Flask
    """
    db.init_app(app)
    
    with app.app_context():
        # Creează toate tabelele
        db.create_all()
        print("✅ Baza de date a fost inițializată cu succes!")
        
        # Migrează datele existente dacă există
        migrate_existing_data()

def migrate_existing_data():
    """
    Migreaza datele din users.json in baza de date.
    Proceseaza utilizatorii existenti si analizele lor.
    """
    users_file = 'users.json'
    
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            
            print(f"📦 Găsit fișier users.json cu {len(old_data)} utilizatori")
            
            migrated_users = 0
            migrated_analyses = 0
            
            for username, user_data in old_data.items():
                # Verifică dacă utilizatorul există deja
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    print(f"⚠️  Utilizatorul {username} există deja în baza de date")
                    continue
                
                # Creează utilizatorul nou
                new_user = User(
                    username=username,
                    password=user_data.get('password', ''),
                    role=user_data.get('role', 'user'),
                    created_at=datetime.utcnow()
                )
                
                db.session.add(new_user)
                db.session.flush()  # Pentru a obține ID-ul
                
                # Migrează analizele utilizatorului
                analyses = user_data.get('analize', [])
                for analysis_data in analyses:
                    new_analysis = Analysis(
                        user_id=new_user.id,
                        content_type=analysis_data.get('tip', 'text'),
                        title=analysis_data.get('titlu', 'Fără titlu'),
                        content_preview=analysis_data.get('continut', '')[:500] if analysis_data.get('continut') else '',
                        verdict=analysis_data.get('rezultat', 'unknown'),
                        confidence=float(analysis_data.get('confidence', 0.5)),
                        explanation=analysis_data.get('explanation', ''),
                        analysis_mode=analysis_data.get('analysisMode', 'traditional'),
                        detected_language=analysis_data.get('detectedLanguage', 'unknown'),
                        processing_time=float(analysis_data.get('processingTime', 0.0)),
                        created_at=datetime.strptime(analysis_data.get('data', datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S') if analysis_data.get('data') else datetime.utcnow()
                    )
                    
                    # Adaugă detalii tehnice dacă există
                    if 'technicalDetails' in analysis_data:
                        new_analysis.set_technical_details(analysis_data['technicalDetails'])
                    
                    db.session.add(new_analysis)
                    migrated_analyses += 1
                
                migrated_users += 1
                print(f"✅ Migrat utilizatorul {username} cu {len(analyses)} analize")
            
            db.session.commit()
            
            print(f"🎉 Migrare completă: {migrated_users} utilizatori, {migrated_analyses} analize")
            
            # Creează backup și șterge fișierul vechi
            backup_file = f'users_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            os.rename(users_file, backup_file)
            print(f"📁 Fișierul vechi a fost redenumit în {backup_file}")
            
        except Exception as e:
            print(f"❌ Eroare la migrarea datelor: {e}")
            db.session.rollback()
    else:
        print("ℹ️  Nu există fișier users.json pentru migrare")

def create_admin_user():
    """
    Creaza un utilizator admin implicit daca nu exista.
    Username: admin, password: admin123
    """
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='admin',
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Utilizator admin creat (username: admin, password: admin123)")
    else:
        print("ℹ️  Utilizatorul admin există deja")

def get_user_stats(username):
    """
    Obtine statisticile unui utilizator.
    
    Args:
        username: Numele utilizatorului
        
    Returns:
        dict: Statisticile utilizatorului sau None daca nu exista
    """
    user = User.query.filter_by(username=username).first()
    if not user:
        return None
    
    analyses = Analysis.query.filter_by(user_id=user.id).all()
    
    stats = {
        'totalAnalyses': len(analyses),
        'fakeCount': len([a for a in analyses if a.verdict in ['fake', 'deepfake']]),
        'realCount': len([a for a in analyses if a.verdict in ['real', 'authentic']]),
        'inconclusiveCount': len([a for a in analyses if a.verdict == 'inconclusive']),
        'avgConfidence': sum(a.confidence for a in analyses) / len(analyses) if analyses else 0,
        'recentAnalyses': len([a for a in analyses if (datetime.utcnow() - a.created_at).days <= 7]),
        'analysisTypes': {
            'text': len([a for a in analyses if a.content_type == 'text']),
            'video': len([a for a in analyses if a.content_type == 'video']),
            'url': len([a for a in analyses if a.content_type == 'url'])
        }
    }
    
    return stats

def get_system_stats():
    """
    Obtine statisticile generale ale sistemului.
    
    Returns:
        dict: Statistici despre utilizatori si analize
    """
    total_users = User.query.count()
    total_analyses = Analysis.query.count()
    
    # Statistici pe verdictele
    fake_count = Analysis.query.filter(Analysis.verdict.in_(['fake', 'deepfake'])).count()
    real_count = Analysis.query.filter(Analysis.verdict.in_(['real', 'authentic'])).count()
    inconclusive_count = Analysis.query.filter_by(verdict='inconclusive').count()
    
    # Statistici recente (ultima săptămână)
    week_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = week_ago.replace(day=week_ago.day - 7)
    recent_analyses = Analysis.query.filter(Analysis.created_at >= week_ago).count()
    
    # Utilizatori activi (cu analize în ultima săptămână)
    active_users = db.session.query(User).join(Analysis).filter(Analysis.created_at >= week_ago).distinct().count()
    
    return {
        'totalUsers': total_users,
        'totalAnalyses': total_analyses,
        'fakeCount': fake_count,
        'realCount': real_count,
        'inconclusiveCount': inconclusive_count,
        'recentAnalyses': recent_analyses,
        'activeUsers': active_users,
        'avgAnalysesPerUser': total_analyses / total_users if total_users > 0 else 0
    }

def cleanup_old_analyses(days=30):
    """
    Sterge analizele mai vechi de X zile.
    
    Args:
        days: Numarul de zile (default 30)
        
    Returns:
        int: Numarul de analize sterse
    """
    cutoff_date = datetime.utcnow().replace(day=datetime.utcnow().day - days)
    old_analyses = Analysis.query.filter(Analysis.created_at < cutoff_date).all()
    
    count = len(old_analyses)
    for analysis in old_analyses:
        db.session.delete(analysis)
    
    db.session.commit()
    print(f"🧹 Șterse {count} analize mai vechi de {days} zile")
    
    return count

def backup_database():
    """
    Creaza un backup JSON al bazei de date.
    
    Returns:
        str: Numele fisierului de backup creat
    """
    backup_data = {
        'users': [],
        'analyses': [],
        'created_at': datetime.utcnow().isoformat()
    }
    
    # Exportă utilizatorii
    users = User.query.all()
    for user in users:
        user_data = user.to_dict()
        user_data['analyses'] = [analysis.to_dict() for analysis in user.analyses]
        backup_data['users'].append(user_data)
    
    # Salvează backup-ul
    backup_filename = f'database_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(backup_filename, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Backup creat: {backup_filename}")
    return backup_filename 