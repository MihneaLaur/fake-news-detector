/**
 * Componenta React pentru gestionarea setarilor utilizatorului.
 * Permite configurarea profilului, preferintelor de analiza si temei aplicatiei.
 * Toate setarile sunt salvate in localStorage.
 */

import React, { useState, useEffect } from "react";
import { useAuth } from "../AuthContext";
import { useNotifications } from "../NotificationContext";

export default function Settings() {
  const { user, checkAuth, forceLogout } = useAuth();
  const { showSuccess, showError, showDisconnectionAlert } = useNotifications();
  
  /**
   * State pentru datele profilului utilizatorului.
   */
  const [profileData, setProfileData] = useState({
    username: '',
    email: '',
    profilePicture: null,
    profilePicturePreview: null
  });
  
  /**
   * State pentru preferintele de analiza ale utilizatorului.
   */
  const [preferences, setPreferences] = useState({
    defaultAnalysisMode: 'hybrid',
    preferredLanguages: ['ro', 'en'],
    analysisTimeout: 30,
    detailLevel: 'complete',
    confidenceThreshold: 70
  });
  
  /**
   * State pentru setarile de tema si aspect.
   */
  const [theme, setTheme] = useState({
    mode: 'light',
    accentColor: 'blue',
    compactMode: false,
    fontSize: 'normal',
    animations: true
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');

  /**
   * Initializeaza componenta si incarca setarile utilizatorului.
   */
  useEffect(() => {
    checkAuth();
    loadUserSettings();
  }, [user]);

  /**
   * Incarca setarile salvate din localStorage pentru utilizatorul curent.
   */
  const loadUserSettings = async () => {
    if (!user?.username) return;
    
    try {
      const savedPreferences = localStorage.getItem(`preferences_${user.username}`);
      const savedTheme = localStorage.getItem(`theme_${user.username}`);
      const savedProfilePic = localStorage.getItem(`profilePic_${user.username}`);
      
      if (savedPreferences) {
        setPreferences(JSON.parse(savedPreferences));
      }
      
      if (savedTheme) {
        setTheme(JSON.parse(savedTheme));
      }
      
      setProfileData({
        username: user.username,
        email: user.email || '',
        profilePicture: null,
        profilePicturePreview: savedProfilePic || null
      });
      
    } catch (error) {
      console.error('Eroare la încărcarea setărilor:', error);
    }
  };

  /**
   * Gestioneaza schimbarea pozei de profil cu validari.
   * @param {Event} e - Evenimentul de schimbare a fisierului
   */
  const handleProfilePictureChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        showError('Te rog selectează o imagine validă!');
        return;
      }
      
      if (file.size > 5 * 1024 * 1024) {
        showError('Imaginea este prea mare! Mărimea maximă este 5MB.');
        return;
      }
      
      const reader = new FileReader();
      reader.onload = (e) => {
        setProfileData(prev => ({
          ...prev,
          profilePicture: file,
          profilePicturePreview: e.target.result
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  /**
   * Salveaza setarile profilului in localStorage.
   */
  const saveProfileSettings = async () => {
    setIsLoading(true);
    try {
      if (profileData.profilePicturePreview) {
        localStorage.setItem(`profilePic_${user.username}`, profileData.profilePicturePreview);
      }
      
      showSuccess('Profilul a fost actualizat cu succes!');
    } catch (error) {
      showError('Eroare la salvarea profilului: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Salveaza preferintele de analiza in localStorage.
   */
  const savePreferences = async () => {
    setIsLoading(true);
    try {
      localStorage.setItem(`preferences_${user.username}`, JSON.stringify(preferences));
      showSuccess('Preferințele au fost salvate!');
    } catch (error) {
      showError('Eroare la salvarea preferințelor: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Salveaza setarile de tema si le aplica imediat.
   */
  const saveTheme = async () => {
    setIsLoading(true);
    try {
      localStorage.setItem(`theme_${user.username}`, JSON.stringify(theme));
      
      document.body.className = theme.mode === 'dark' ? 'dark-theme' : '';
      
      showSuccess('Tema a fost aplicată!');
    } catch (error) {
      showError('Eroare la salvarea temei: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Toggle pentru limba in lista de limbi preferate.
   * @param {string} lang - Codul limbii
   */
  const handleLanguageToggle = (lang) => {
    setPreferences(prev => ({
      ...prev,
      preferredLanguages: prev.preferredLanguages.includes(lang)
        ? prev.preferredLanguages.filter(l => l !== lang)
        : [...prev.preferredLanguages, lang]
    }));
  };

  /**
   * Componenta pentru butoanele de navigare intre tab-uri.
   * @param {Object} props - Proprietatile componentei
   * @param {string} props.id - ID-ul tab-ului
   * @param {string} props.label - Eticheta afisata
   * @param {string} props.icon - Iconita tab-ului
   * @param {boolean} props.isActive - Daca tab-ul este activ
   * @param {Function} props.onClick - Functia de click
   * @returns {JSX.Element} Butonul de tab
   */
  const TabButton = ({ id, label, icon, isActive, onClick }) => (
    <button
      onClick={() => onClick(id)}
      style={{
        background: isActive ? '#4f46e5' : 'transparent',
        color: isActive ? 'white' : '#4f46e5',
        border: '2px solid #4f46e5',
        borderRadius: '0.5rem',
        padding: '0.75rem 1.5rem',
        cursor: 'pointer',
        fontSize: '0.9rem',
        fontWeight: '500',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        transition: 'all 0.2s ease'
      }}
    >
      {icon} {label}
    </button>
  );

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ color: '#4f46e5', marginBottom: '0.5rem' }}>⚙️ Setări</h2>
        <p style={{ color: '#6b7280', margin: 0 }}>
          Configurează-ți profilul și preferințele pentru o experiență personalizată
        </p>
      </div>

      <div style={{ 
        display: 'flex', 
        gap: '1rem', 
        marginBottom: '2rem',
        flexWrap: 'wrap'
      }}>
        <TabButton
          id="profile"
          label="Profil"
          icon="👤"
          isActive={activeTab === 'profile'}
          onClick={setActiveTab}
        />
        <TabButton
          id="preferences"
          label="Preferințe Analiză"
          icon="🔧"
          isActive={activeTab === 'preferences'}
          onClick={setActiveTab}
        />
        <TabButton
          id="theme"
          label="Aspect"
          icon="🎨"
          isActive={activeTab === 'theme'}
          onClick={setActiveTab}
        />
      </div>

      {activeTab === 'profile' && (
        <div style={{
          background: '#fff',
          borderRadius: '1rem',
          padding: '2rem',
          boxShadow: '0 2px 8px rgba(79,70,229,0.08)',
          border: '1px solid #e2e8f0'
        }}>
          <h3 style={{ color: '#4f46e5', marginBottom: '1.5rem' }}>👤 Informații Profil</h3>
          
          <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
            <div style={{ marginBottom: '1rem' }}>
              {profileData.profilePicturePreview ? (
                <img
                  src={profileData.profilePicturePreview}
                  alt="Profile"
                  style={{
                    width: '120px',
                    height: '120px',
                    borderRadius: '50%',
                    objectFit: 'cover',
                    border: '4px solid #4f46e5',
                    boxShadow: '0 4px 12px rgba(79,70,229,0.2)'
                  }}
                />
              ) : (
                <div style={{
                  width: '120px',
                  height: '120px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #4f46e5, #7c3aed)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '3rem',
                  color: 'white',
                  margin: '0 auto',
                  boxShadow: '0 4px 12px rgba(79,70,229,0.2)'
                }}>
                  {user?.username?.charAt(0).toUpperCase() || '👤'}
                </div>
              )}
            </div>
            
            <input
              type="file"
              accept="image/*"
              onChange={handleProfilePictureChange}
              style={{ display: 'none' }}
              id="profilePictureInput"
            />
            <label
              htmlFor="profilePictureInput"
              style={{
                background: '#e0e7ff',
                color: '#4f46e5',
                border: '2px solid #4f46e5',
                borderRadius: '0.5rem',
                padding: '0.5rem 1rem',
                cursor: 'pointer',
                fontSize: '0.9rem',
                fontWeight: '500',
                display: 'inline-block',
                transition: 'all 0.2s ease'
              }}
            >
              📷 Schimbă poza de profil
            </label>
            <div style={{ fontSize: '0.8rem', color: '#6b7280', marginTop: '0.5rem' }}>
              Formate acceptate: JPG, PNG, GIF (max 5MB)
            </div>
          </div>

          <div style={{ display: 'grid', gap: '1.5rem' }}>
            <div>
              <label style={{ 
                display: 'block', 
                marginBottom: '0.5rem', 
                fontWeight: '500', 
                color: '#374151' 
              }}>
                👤 Nume utilizator
              </label>
              <input
                type="text"
                value={profileData.username}
                disabled
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  borderRadius: '0.5rem',
                  border: '1px solid #d1d5db',
                  background: '#f9fafb',
                  color: '#6b7280',
                  fontSize: '1rem'
                }}
              />
              <div style={{ fontSize: '0.8rem', color: '#6b7280', marginTop: '0.25rem' }}>
                Numele de utilizator nu poate fi modificat
              </div>
            </div>

            <div>
              <label style={{ 
                display: 'block', 
                marginBottom: '0.5rem', 
                fontWeight: '500', 
                color: '#374151' 
              }}>
                📧 Email (opțional)
              </label>
              <input
                type="email"
                value={profileData.email}
                onChange={(e) => setProfileData(prev => ({ ...prev, email: e.target.value }))}
                placeholder="exemplu@email.com"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  borderRadius: '0.5rem',
                  border: '1px solid #d1d5db',
                  fontSize: '1rem'
                }}
              />
            </div>
          </div>

          <button
            onClick={saveProfileSettings}
            disabled={isLoading}
            style={{
              background: '#4f46e5',
              color: 'white',
              border: 'none',
              borderRadius: '0.5rem',
              padding: '0.75rem 2rem',
              fontSize: '1rem',
              fontWeight: '500',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              marginTop: '2rem',
              opacity: isLoading ? 0.7 : 1,
              transition: 'all 0.2s ease'
            }}
          >
            {isLoading ? '💾 Salvez...' : '💾 Salvează Profil'}
          </button>
        </div>
      )}

      {activeTab === 'preferences' && (
        <div style={{
          background: '#fff',
          borderRadius: '1rem',
          padding: '2rem',
          boxShadow: '0 2px 8px rgba(79,70,229,0.08)',
          border: '1px solid #e2e8f0'
        }}>
          <h3 style={{ color: '#4f46e5', marginBottom: '1.5rem' }}>🔧 Preferințe Analiză</h3>
          
          <div style={{ display: 'grid', gap: '2rem' }}>
            <div>
              <label style={{ 
                display: 'block', 
                marginBottom: '1rem', 
                fontWeight: '500', 
                color: '#374151' 
              }}>
                🤖 Mod de analiză implicit
              </label>
              <div style={{ display: 'grid', gap: '0.5rem' }}>
                {[
                  { value: 'traditional', label: 'Tradițional', desc: 'Rapid și eficient' },
                  { value: 'hybrid', label: 'Hibrid', desc: 'Combină AI și ML (recomandat)' },
                  { value: 'ai_only', label: 'Doar AI', desc: 'Analiză avansată cu AI' },
                  { value: 'ml_only', label: 'Doar ML', desc: 'Machine Learning specializat' }
                ].map(mode => (
                  <label key={mode.value} style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.75rem',
                    padding: '0.75rem',
                    borderRadius: '0.5rem',
                    border: preferences.defaultAnalysisMode === mode.value ? '2px solid #4f46e5' : '1px solid #e5e7eb',
                    background: preferences.defaultAnalysisMode === mode.value ? '#f0f9ff' : '#fff',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}>
                    <input
                      type="radio"
                      name="analysisMode"
                      value={mode.value}
                      checked={preferences.defaultAnalysisMode === mode.value}
                      onChange={(e) => setPreferences(prev => ({ ...prev, defaultAnalysisMode: e.target.value }))}
                      style={{ margin: 0 }}
                    />
                    <div>
                      <div style={{ fontWeight: '500', color: '#374151' }}>{mode.label}</div>
                      <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>{mode.desc}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label style={{ 
                display: 'block', 
                marginBottom: '1rem', 
                fontWeight: '500', 
                color: '#374151' 
              }}>
                🌍 Limbi preferate
              </label>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {[
                  { code: 'ro', name: 'Română', flag: '🇷🇴' },
                  { code: 'en', name: 'Engleză', flag: '🇺🇸' },
                  { code: 'fr', name: 'Franceză', flag: '🇫🇷' },
                  { code: 'es', name: 'Spaniolă', flag: '🇪🇸' },
                  { code: 'de', name: 'Germană', flag: '🇩🇪' }
                ].map(lang => (
                  <button
                    key={lang.code}
                    onClick={() => handleLanguageToggle(lang.code)}
                    style={{
                      background: preferences.preferredLanguages.includes(lang.code) ? '#4f46e5' : '#f3f4f6',
                      color: preferences.preferredLanguages.includes(lang.code) ? 'white' : '#374151',
                      border: 'none',
                      borderRadius: '0.5rem',
                      padding: '0.5rem 1rem',
                      cursor: 'pointer',
                      fontSize: '0.9rem',
                      fontWeight: '500',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    {lang.flag} {lang.name}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label style={{ 
                display: 'block', 
                marginBottom: '1rem', 
                fontWeight: '500', 
                color: '#374151' 
              }}>
                ⏱️ Timeout analiză: {preferences.analysisTimeout} secunde
              </label>
              <input
                type="range"
                min="10"
                max="120"
                value={preferences.analysisTimeout}
                onChange={(e) => setPreferences(prev => ({ ...prev, analysisTimeout: parseInt(e.target.value) }))}
                style={{ width: '100%' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#6b7280' }}>
                <span>10s (rapid)</span>
                <span>120s (detaliat)</span>
              </div>
            </div>

            <div>
              <label style={{ 
                display: 'block', 
                marginBottom: '1rem', 
                fontWeight: '500', 
                color: '#374151' 
              }}>
                🎯 Prag confidență: {preferences.confidenceThreshold}%
              </label>
              <input
                type="range"
                min="50"
                max="95"
                value={preferences.confidenceThreshold}
                onChange={(e) => setPreferences(prev => ({ ...prev, confidenceThreshold: parseInt(e.target.value) }))}
                style={{ width: '100%' }}
              />
              <div style={{ fontSize: '0.8rem', color: '#6b7280', marginTop: '0.5rem' }}>
                Sub acest prag, rezultatul va fi marcat ca "neconcludent"
              </div>
            </div>
          </div>

          <button
            onClick={savePreferences}
            disabled={isLoading}
            style={{
              background: '#4f46e5',
              color: 'white',
              border: 'none',
              borderRadius: '0.5rem',
              padding: '0.75rem 2rem',
              fontSize: '1rem',
              fontWeight: '500',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              marginTop: '2rem',
              opacity: isLoading ? 0.7 : 1,
              transition: 'all 0.2s ease'
            }}
          >
            {isLoading ? '💾 Salvez...' : '💾 Salvează Preferințe'}
          </button>
        </div>
      )}

      {activeTab === 'theme' && (
        <div style={{
          background: '#fff',
          borderRadius: '1rem',
          padding: '2rem',
          boxShadow: '0 2px 8px rgba(79,70,229,0.08)',
          border: '1px solid #e2e8f0'
        }}>
          <h3 style={{ color: '#4f46e5', marginBottom: '1.5rem' }}>🎨 Aspect și Comportament</h3>
          
          <div style={{ display: 'grid', gap: '2rem' }}>
            <div>
              <label style={{ 
                display: 'block', 
                marginBottom: '1rem', 
                fontWeight: '500', 
                color: '#374151' 
              }}>
                🌓 Temă
              </label>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {[
                  { value: 'light', label: '☀️ Light', desc: 'Tema luminoasă' },
                  { value: 'dark', label: '🌙 Dark', desc: 'Tema întunecată' },
                  { value: 'auto', label: '🔄 Auto', desc: 'Urmează sistemul' }
                ].map(mode => (
                  <button
                    key={mode.value}
                    onClick={() => setTheme(prev => ({ ...prev, mode: mode.value }))}
                    style={{
                      background: theme.mode === mode.value ? '#4f46e5' : '#f3f4f6',
                      color: theme.mode === mode.value ? 'white' : '#374151',
                      border: 'none',
                      borderRadius: '0.5rem',
                      padding: '1rem',
                      cursor: 'pointer',
                      fontSize: '0.9rem',
                      fontWeight: '500',
                      textAlign: 'center',
                      flex: 1,
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <div>{mode.label}</div>
                    <div style={{ fontSize: '0.7rem', opacity: 0.8, marginTop: '0.25rem' }}>
                      {mode.desc}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label style={{ 
                display: 'block', 
                marginBottom: '1rem', 
                fontWeight: '500', 
                color: '#374151' 
              }}>
                🌈 Culoare accent
              </label>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {[
                  { value: 'blue', color: '#4f46e5', name: 'Albastru' },
                  { value: 'green', color: '#059669', name: 'Verde' },
                  { value: 'purple', color: '#7c3aed', name: 'Mov' },
                  { value: 'red', color: '#dc2626', name: 'Roșu' },
                  { value: 'orange', color: '#ea580c', name: 'Portocaliu' }
                ].map(color => (
                  <button
                    key={color.value}
                    onClick={() => setTheme(prev => ({ ...prev, accentColor: color.value }))}
                    style={{
                      width: '60px',
                      height: '60px',
                      borderRadius: '50%',
                      background: color.color,
                      border: theme.accentColor === color.value ? '4px solid #374151' : '2px solid #e5e7eb',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      position: 'relative'
                    }}
                    title={color.name}
                  >
                    {theme.accentColor === color.value && (
                      <div style={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        color: 'white',
                        fontSize: '1.5rem'
                      }}>
                        ✓
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: 'grid', gap: '1rem' }}>
              <label style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '0.75rem',
                cursor: 'pointer'
              }}>
                <input
                  type="checkbox"
                  checked={theme.animations}
                  onChange={(e) => setTheme(prev => ({ ...prev, animations: e.target.checked }))}
                />
                <span style={{ fontWeight: '500', color: '#374151' }}>⚡ Activează animațiile</span>
              </label>

              <label style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '0.75rem',
                cursor: 'pointer'
              }}>
                <input
                  type="checkbox"
                  checked={theme.compactMode}
                  onChange={(e) => setTheme(prev => ({ ...prev, compactMode: e.target.checked }))}
                />
                <span style={{ fontWeight: '500', color: '#374151' }}>📱 Mod compact</span>
              </label>
            </div>
          </div>

          <button
            onClick={saveTheme}
            disabled={isLoading}
            style={{
              background: '#4f46e5',
              color: 'white',
              border: 'none',
              borderRadius: '0.5rem',
              padding: '0.75rem 2rem',
              fontSize: '1rem',
              fontWeight: '500',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              marginTop: '2rem',
              opacity: isLoading ? 0.7 : 1,
              transition: 'all 0.2s ease'
            }}
          >
            {isLoading ? '🎨 Aplicez...' : '🎨 Aplică Tema'}
          </button>
        </div>
      )}
    </div>
  );
} 