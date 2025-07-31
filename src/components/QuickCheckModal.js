import React, { useState, useEffect } from "react";
import { useAuth } from "../AuthContext";
import { useNotifications } from "../NotificationContext";

export default function QuickCheckModal({ isOpen, onClose }) {
  const { user, forceLogout } = useAuth();
  const { showError, showSuccess, showDisconnectionAlert } = useNotifications();
  
  const [text, setText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [analysisMode, setAnalysisMode] = useState("hybrid");
  
  /**
   * State pentru preferințele utilizatorului
   */
  const [userPreferences, setUserPreferences] = useState({
    defaultAnalysisMode: 'hybrid',
    analysisTimeout: 30,
    confidenceThreshold: 70
  });

  /**
   * Încarcă preferințele utilizatorului din localStorage.
   */
  const loadUserPreferences = () => {
    if (!user?.username) return;
    
    try {
      const savedPreferences = localStorage.getItem(`preferences_${user.username}`);
      if (savedPreferences) {
        const preferences = JSON.parse(savedPreferences);
        
        // Actualizează state-ul cu preferințele
        setUserPreferences(preferences);
        
        // Setează modul de analiză implicit
        if (preferences.defaultAnalysisMode) {
          setAnalysisMode(preferences.defaultAnalysisMode);
          console.log(`🎯 QuickCheck: Încărcat mod implicit: ${preferences.defaultAnalysisMode} pentru ${user.username}`);
        }
        
        console.log(`⚙️ QuickCheck preferințe încărcate:`, preferences);
      }
    } catch (error) {
      console.error('Eroare la încărcarea preferințelor QuickCheck:', error);
    }
  };

  // Închide modal cu ESC
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Focus pe input când se deschide modal-ul
  useEffect(() => {
    if (isOpen) {
      const input = document.getElementById('quickCheckInput');
      if (input) {
        setTimeout(() => input.focus(), 100);
      }
    }
  }, [isOpen]);

  // Încarcă preferințele când se schimbă utilizatorul
  useEffect(() => {
    loadUserPreferences();
  }, [user]);

  // Reset când se închide modal-ul
  useEffect(() => {
    if (!isOpen) {
      setText("");
      setResult(null);
      setIsLoading(false);
    }
  }, [isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!text.trim()) {
      showError("Introdu textul pentru verificare!");
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      // Detectează automat dacă este URL
      const isUrl = text.trim().startsWith('http://') || text.trim().startsWith('https://');
      
      // Implementează timeout din preferințe
      const timeoutMs = userPreferences.analysisTimeout * 1000;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: isUrl ? '' : text,
          url: isUrl ? text : '',
          mode: analysisMode,
          userPreferences: {
            confidenceThreshold: userPreferences.confidenceThreshold,
            analysisTimeout: userPreferences.analysisTimeout,
            defaultAnalysisMode: userPreferences.defaultAnalysisMode
          }
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        
        // Verifică pragul de confidență din preferințe
        const confidenceThreshold = userPreferences.confidenceThreshold / 100;
        if (data.confidence < confidenceThreshold) {
          data.verdict = 'neconcludent';
          data.explanation = `⚠️ REZULTAT NECONCLUDENT\n\nConfidența (${(data.confidence * 100).toFixed(1)}%) este sub pragul setat (${userPreferences.confidenceThreshold}%).\n\nExplicația originală:\n${data.explanation}`;
          console.log(`⚠️ QuickCheck marcat ca neconcludent: ${(data.confidence * 100).toFixed(1)}% < ${userPreferences.confidenceThreshold}%`);
        }
        
        setResult(data);
        
        // Dispatch event pentru actualizarea dashboard-ului
        window.dispatchEvent(new CustomEvent('analysisCompleted', {
          detail: { type: 'quick_check', result: data }
        }));
        
      } else if (response.status === 401) {
        showDisconnectionAlert();
        forceLogout("Sesiunea a expirat");
        onClose();
        return;
      } else {
        const errorData = await response.json();
        showError(errorData.error || 'Eroare la analiză');
      }
    } catch (error) {
      console.error('Eroare Quick Check:', error);
      showError('Eroare de conexiune: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasteFromClipboard = async () => {
    try {
      const clipboardText = await navigator.clipboard.readText();
      setText(clipboardText);
      showSuccess("Text încărcat din clipboard!");
    } catch (error) {
      showError("Nu s-a putut accesa clipboard-ul");
    }
  };

  const getVerdictDisplay = (verdict) => {
    switch (verdict) {
      case 'fake':
        return { text: '🚨 FAKE NEWS', color: '#e11d48', bg: '#fef2f2' };
      case 'real':
        return { text: '✅ ȘTIRE REALĂ', color: '#22c55e', bg: '#f0fdf4' };
      case 'deepfake':
        return { text: '🎬 DEEPFAKE', color: '#dc2626', bg: '#fef2f2' };
      case 'authentic':
        return { text: '✅ AUTENTIC', color: '#16a34a', bg: '#f0fdf4' };
      case 'inconclusive':
      case 'neconcludent':
        return { text: '❓ NECONCLUDENT', color: '#f59e0b', bg: '#fffbeb' };
      default:
        return { text: verdict?.toUpperCase() || 'NECUNOSCUT', color: '#6b7280', bg: '#f9fafb' };
    }
  };

  const shareResult = () => {
    const verdict = getVerdictDisplay(result.verdict);
    const shareText = `🔍 Quick Check Result:\n${verdict.text} (${(result.confidence * 100).toFixed(1)}% confidență)\n\nVerificat cu Fake News Detector`;
    
    if (navigator.share) {
      navigator.share({
        title: 'Rezultat Quick Check',
        text: shareText
      });
    } else {
      navigator.clipboard.writeText(shareText);
      showSuccess("Rezultat copiat în clipboard!");
    }
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.7)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1rem'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '1rem',
        padding: '2rem',
        maxWidth: '600px',
        width: '100%',
        maxHeight: '80vh',
        overflowY: 'auto',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        {/* Header */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          marginBottom: '1.5rem',
          width: '100%'
        }}>
          <h2 style={{ 
            color: '#4f46e5', 
            margin: 0,
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            🚀 Quick Check
          </h2>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '1.5rem',
              cursor: 'pointer',
              color: '#6b7280',
              padding: '0.25rem',
              borderRadius: '0.25rem',
              transition: 'color 0.2s ease'
            }}
            onMouseEnter={(e) => e.target.style.color = '#374151'}
            onMouseLeave={(e) => e.target.style.color = '#6b7280'}
          >
            ✕
          </button>
        </div>

        {/* Quick Actions */}
        <div style={{ 
          display: 'flex', 
          gap: '0.5rem', 
          marginBottom: '1rem',
          flexWrap: 'wrap',
          width: '100%',
          justifyContent: 'center'
        }}>
          <button
            onClick={handlePasteFromClipboard}
            style={{
              background: '#e0e7ff',
              color: '#4f46e5',
              border: '1px solid #c7d2fe',
              borderRadius: '0.5rem',
              padding: '0.5rem 1rem',
              cursor: 'pointer',
              fontSize: '0.9rem',
              fontWeight: '500',
              transition: 'all 0.2s ease'
            }}
          >
            📋 Paste din Clipboard
          </button>
          
          <select
            value={analysisMode}
            onChange={(e) => setAnalysisMode(e.target.value)}
            style={{
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '0.5rem',
              padding: '0.5rem',
              fontSize: '0.9rem',
              color: '#374151',
              minWidth: '200px'
            }}
          >
            <option value="hybrid">🤖 Hibrid</option>
            <option value="traditional">⚡ Tradițional</option>
            <option value="ai_only">🧠 Doar AI</option>
            <option value="ml_only">🔬 Doar ML</option>
          </select>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} style={{ width: '100%' }}>
          <textarea
            id="quickCheckInput"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Introdu textul sau link-ul pentru verificare rapidă..."
            style={{
              width: '100%',
              minHeight: '120px',
              padding: '1rem',
              borderRadius: '0.5rem',
              border: '2px solid #e2e8f0',
              fontSize: '1rem',
              resize: 'vertical',
              fontFamily: 'inherit',
              marginBottom: '1rem'
            }}
            onFocus={(e) => e.target.style.borderColor = '#4f46e5'}
            onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
          />
          
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', justifyContent: 'center' }}>
            <button
              type="submit"
              disabled={isLoading || !text.trim()}
              style={{
                background: isLoading || !text.trim() ? '#9ca3af' : '#4f46e5',
                color: 'white',
                border: 'none',
                borderRadius: '0.5rem',
                padding: '0.75rem 2rem',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: isLoading || !text.trim() ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                flex: 1,
                maxWidth: '300px'
              }}
            >
              {isLoading ? '🔄 Verificare...' : '🔍 Check Now'}
            </button>
          </div>
        </form>

        {/* Results */}
        {result && (
          <div style={{
            marginTop: '1.5rem',
            padding: '1.5rem',
            borderRadius: '0.75rem',
            border: '2px solid #e2e8f0',
            background: getVerdictDisplay(result.verdict).bg
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1rem'
            }}>
              <div style={{
                fontSize: '1.2rem',
                fontWeight: 'bold',
                color: getVerdictDisplay(result.verdict).color
              }}>
                {getVerdictDisplay(result.verdict).text}
              </div>
              <div style={{
                fontSize: '1rem',
                fontWeight: '600',
                color: '#374151'
              }}>
                {(result.confidence * 100).toFixed(1)}% confidență
              </div>
            </div>

            {/* Confidence Bar */}
            <div style={{ marginBottom: '1rem' }}>
              <div style={{
                width: '100%',
                height: '8px',
                backgroundColor: '#e5e7eb',
                borderRadius: '4px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${result.confidence * 100}%`,
                  height: '100%',
                  backgroundColor: getVerdictDisplay(result.verdict).color,
                  transition: 'width 0.5s ease'
                }}></div>
              </div>
            </div>

            {/* Action Buttons */}
            <div style={{ 
              display: 'flex', 
              gap: '0.5rem', 
              flexWrap: 'wrap',
              marginTop: '1rem'
            }}>
              <button
                onClick={() => {
                  setText("");
                  setResult(null);
                  document.getElementById('quickCheckInput')?.focus();
                }}
                style={{
                  background: '#f3f4f6',
                  color: '#374151',
                  border: '1px solid #d1d5db',
                  borderRadius: '0.5rem',
                  padding: '0.5rem 1rem',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  fontWeight: '500'
                }}
              >
                🔄 Check altul
              </button>
              
              <button
                onClick={shareResult}
                style={{
                  background: '#e0e7ff',
                  color: '#4f46e5',
                  border: '1px solid #c7d2fe',
                  borderRadius: '0.5rem',
                  padding: '0.5rem 1rem',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  fontWeight: '500'
                }}
              >
                📤 Share
              </button>
              
              <button
                onClick={() => {
                  // Salvează în istoric (se face automat prin API)
                  showSuccess("Salvat în istoric!");
                }}
                style={{
                  background: '#dcfce7',
                  color: '#16a34a',
                  border: '1px solid #bbf7d0',
                  borderRadius: '0.5rem',
                  padding: '0.5rem 1rem',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  fontWeight: '500'
                }}
              >
                💾 Salvat în istoric
              </button>
            </div>
          </div>
        )}

        {/* Tips */}
        <div style={{
          marginTop: '1.5rem',
          padding: '1rem',
          background: '#f8fafc',
          borderRadius: '0.5rem',
          border: '1px solid #e2e8f0'
        }}>
          <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>
            💡 <strong>Tips:</strong> Poți introduce text direct sau link-uri. 
            Folosește Ctrl+K pentru a deschide Quick Check de oriunde!
          </div>
        </div>
      </div>
    </div>
  );
} 