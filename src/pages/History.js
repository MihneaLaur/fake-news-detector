/**
 * Componenta React pentru afisarea istoricului analizelor utilizatorului.
 * Gestioneaza incarcarea, sortarea si afisarea analizelor din baza de date.
 * Suporta actualizari in timp real si preview video.
 */

import React, { useEffect, useState } from "react";
import { useAuth } from "../AuthContext";
import { useNotifications } from "../NotificationContext";

export default function History() {
  const { user, checkAuth, forceLogout } = useAuth();
  const { showDisconnectionAlert, showError } = useNotifications();
  const [analize, setAnalize] = useState([]);
  
  // 🆕 ÎMBUNĂTĂȚIRI NOI
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [sortBy, setSortBy] = useState('data');
  const [sortOrder, setSortOrder] = useState('desc');
  const [showSortMenu, setShowSortMenu] = useState(false);
  const [expandedVideo, setExpandedVideo] = useState(null);

  /**
   * Initializeaza componenta si seteaza listenerii pentru actualizari.
   */
  useEffect(() => {
    // Verifică autentificarea înainte de a încărca datele
    const initializeHistory = async () => {
      await checkAuth();
      loadHistoryData();
    };
    
    initializeHistory();
    
    /**
     * Handler pentru evenimentul de analiza completata - actualizeaza lista.
     * @param {CustomEvent} event - Evenimentul cu detaliile analizei noi
     */
    const handleAnalysisCompleted = (event) => {
      console.log('📜 History: Nouă analiză completată!', event.detail);
      setLastUpdate(new Date().toLocaleTimeString());
      setIsRefreshing(true);
      
      // Actualizează datele după o scurtă întârziere pentru animație
      setTimeout(() => {
        loadHistoryData();
        setIsRefreshing(false);
      }, 500);
    };

    window.addEventListener('analysisCompleted', handleAnalysisCompleted);
    
    return () => {
      window.removeEventListener('analysisCompleted', handleAnalysisCompleted);
    };
  }, [user]);

  /**
   * Gestioneaza inchiderea meniului de sortare la click in afara.
   */
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showSortMenu && !event.target.closest('[data-sort-menu]')) {
        setShowSortMenu(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showSortMenu]);

  /**
   * Incarca datele din baza de date si aplica sortarea.
   * Se conecteaza la API-ul backend pentru separarea utilizatorilor.
   */
  const loadHistoryData = async () => {
    if (!user?.username) {
      console.log('📜 History: Nu există utilizator autentificat');
      setAnalize([]);
      setError(null);
      return;
    }

    try {
      console.log(`📜 History: Încărcare istoric din baza de date pentru ${user.username}`);
      
      // Încarcă din API în loc de localStorage
      const response = await fetch('http://localhost:5000/user-history', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

             if (response.ok) {
        const data = await response.json();
        let userAnalyses = data.analyses || [];
        
        console.log(`📜 History: Încărcat ${userAnalyses.length} analize din baza de date`);
        
        // Sortare
        const sortedData = [...userAnalyses].sort((a, b) => {
          let valueA, valueB;
          
          switch (sortBy) {
            case 'data':
              valueA = new Date(a.data || a.created_at);
              valueB = new Date(b.data || b.created_at);
              break;
            case 'confidence':
              valueA = a.confidence || 0;
              valueB = b.confidence || 0;
              break;
            case 'rezultat':
              valueA = a.rezultat || a.verdict;
              valueB = b.rezultat || b.verdict;
              break;
            default:
              valueA = a[sortBy];
              valueB = b[sortBy];
          }
          
          if (sortOrder === 'asc') {
            return valueA > valueB ? 1 : -1;
          } else {
            return valueA < valueB ? 1 : -1;
          }
        });
        
        setAnalize(sortedData);
        setError(null);
        
      } else if (response.status === 401) {
        console.warn('📜 History: Utilizator neautentificat - 401 Unauthorized');
        showDisconnectionAlert();
        forceLogout("Sesiunea a expirat");
        return;
        
      } else {
        console.error('📜 History: Eroare la încărcarea din API:', response.status);
        showError('Eroare la încărcarea istoricului');
        loadHistoryDataFromLocalStorage();
      }
      
    } catch (error) {
      console.error('📜 History: Eroare la conectarea la API:', error);
      loadHistoryDataFromLocalStorage();
    }
  };

  /**
   * Fallback pentru incarcarea din localStorage cand API-ul nu e disponibil.
   * Folosit doar pentru cazuri de eroare de conectare.
   */
  const loadHistoryDataFromLocalStorage = () => {
    try {
      const userAnalysesKey = `analize_${user?.username || "guest"}`;
      const userAnalize = JSON.parse(localStorage.getItem(userAnalysesKey) || "[]");
      
      console.log(`📜 History: Fallback localStorage - ${userAnalize.length} analize pentru ${user?.username}`);
      
      // Sortare
      const sortedData = [...userAnalize].sort((a, b) => {
        let valueA, valueB;
        
        switch (sortBy) {
          case 'data':
            valueA = new Date(a.data);
            valueB = new Date(b.data);
            break;
          case 'confidence':
            valueA = a.confidence || 0;
            valueB = b.confidence || 0;
            break;
          case 'rezultat':
            valueA = a.rezultat;
            valueB = b.rezultat;
            break;
          default:
            valueA = a[sortBy];
            valueB = b[sortBy];
        }
        
        if (sortOrder === 'asc') {
          return valueA > valueB ? 1 : -1;
        } else {
          return valueA < valueB ? 1 : -1;
        }
      });
      
      setAnalize(sortedData);
      setError(null);
    } catch (err) {
      console.error('📜 History: Eroare la fallback localStorage:', err);
      setError('Eroare la încărcarea istoricului: ' + err.message);
      setAnalize([]);
    }
  };

  /**
   * Gestioneaza sortarea pe o coloana specificata.
   * @param {string} column - Coloana pentru sortare
   * @param {string|null} order - Ordinea de sortare (null pentru toggle)
   */
  const handleSort = (column, order = null) => {
    if (column === sortBy && !order) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder(order || 'desc');
    }
    setShowSortMenu(false);
  };

  /**
   * Reincarca datele cand se schimba criteriile de sortare.
   */
  useEffect(() => {
    if (analize.length > 0) {
      loadHistoryData();
    }
  }, [sortBy, sortOrder]);

  /**
   * Returneaza iconita corespunzatoare pentru sortare pe o coloana.
   * @param {string} column - Coloana verificata
   * @returns {string} Iconita de sortare
   */
  const getSortIcon = (column) => {
    if (sortBy !== column) return '↕️';
    return sortOrder === 'asc' ? '↑' : '↓';
  };

  /**
   * Returneaza formatarea pentru afisarea verdictului analizei.
   * @param {string} verdict - Verdictul analizei
   * @returns {Object} Obiect cu text si culoare pentru verdict
   */
  const getVerdictDisplay = (verdict) => {
    switch (verdict) {
      case 'fake':
        return { text: '🚨 FAKE NEWS', color: '#e11d48' };
      case 'real':
        return { text: '✅ ȘTIRE REALĂ', color: '#22c55e' };
      case 'deepfake':
        return { text: '🎬 DEEPFAKE', color: '#dc2626' };
      case 'authentic':
        return { text: '✅ VIDEO AUTENTIC', color: '#16a34a' };
      case 'inconclusive':
        return { text: '❓ NECONCLUDENT', color: '#f59e0b' };
      default:
        return { text: verdict.toUpperCase(), color: '#6b7280' };
    }
  };

  /**
   * Componenta pentru afisarea barei de confidenta.
   * @param {Object} props - Proprietatile componentei
   * @param {number} props.confidence - Valoarea confidentei (0-1)
   * @returns {JSX.Element} Bara de confidenta
   */
  const ConfidenceBar = ({ confidence }) => {
    if (!confidence) return <span style={{ color: '#6b7280' }}>N/A</span>;
    
    const percentage = confidence * 100;
    const color = percentage > 70 ? '#22c55e' : percentage > 40 ? '#f59e0b' : '#e11d48';
    
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <div style={{
          width: '60px',
          height: '6px',
          backgroundColor: '#e5e7eb',
          borderRadius: '3px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${percentage}%`,
            height: '100%',
            backgroundColor: color,
            transition: 'width 0.3s ease'
          }}></div>
        </div>
        <span style={{ fontSize: '0.8rem', color: '#6b7280' }}>
          {percentage.toFixed(1)}%
        </span>
      </div>
    );
  };

  /**
   * Componenta pentru preview-ul video cu limitare la 30 secunde.
   * @param {Object} props - Proprietatile componentei
   * @param {Object} props.analysis - Obiectul analizei video
   * @returns {JSX.Element|null} Preview video sau null
   */
  const VideoPreview = ({ analysis }) => {
    const permanentFilename = analysis.technical_details?.permanent_filename;
    
    if (!permanentFilename || analysis.tip !== 'video') {
      return null;
    }

    return (
      <div style={{
        marginTop: '0.5rem',
        padding: '0.5rem',
        backgroundColor: '#f8fafc',
        borderRadius: '0.5rem',
        border: '1px solid #e2e8f0'
      }}>
        <div style={{ 
          fontSize: '0.8rem', 
          color: '#6b7280', 
          marginBottom: '0.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          🎬 Preview video (primele 30 secunde)
          <button
            onClick={() => setExpandedVideo(expandedVideo === analysis.id ? null : analysis.id)}
            style={{
              background: 'none',
              border: 'none',
              color: '#4f46e5',
              cursor: 'pointer',
              fontSize: '0.8rem',
              textDecoration: 'underline'
            }}
          >
            {expandedVideo === analysis.id ? 'Ascunde' : 'Afișează'}
          </button>
        </div>
        
        {expandedVideo === analysis.id && (
          <video
            controls
            style={{
              width: '100%',
              maxWidth: '400px',
              height: 'auto',
              borderRadius: '0.3rem'
            }}
            onLoadedMetadata={(e) => {
              // Limitează la primele 30 secunde
              e.target.addEventListener('timeupdate', function() {
                if (this.currentTime > 30) {
                  this.pause();
                  this.currentTime = 30;
                }
              });
            }}
          >
            <source 
              src={`http://localhost:5000/video/${permanentFilename}`} 
              type="video/mp4" 
            />
            <source 
              src={`http://localhost:5000/video/${permanentFilename}`} 
              type="video/webm" 
            />
            <source 
              src={`http://localhost:5000/video/${permanentFilename}`} 
              type="video/ogg" 
            />
            Browserul tău nu suportă redarea video.
          </video>
        )}
      </div>
    );
  };

  /**
   * Optiunile disponibile pentru sortarea datelor.
   */
  const sortOptions = [
    { key: 'data', label: 'Data', icon: '📅' },
    { key: 'tip', label: 'Tip conținut', icon: '📄' },
    { key: 'rezultat', label: 'Verdict', icon: '⚖️' },
    { key: 'confidence', label: 'Confidență', icon: '📊' },
    { key: 'analysisMode', label: 'Mod analiză', icon: '🔧' },
    { key: 'detectedLanguage', label: 'Limba', icon: '🌐' }
  ];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h2 style={{ color: "#4f46e5" }}>Istoric analize</h2>
        
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          {/* 🆕 SORT MENU */}
          <div style={{ position: "relative" }} data-sort-menu>
            <button
              onClick={() => setShowSortMenu(!showSortMenu)}
              style={{
                background: "#4f46e5",
                color: "white",
                border: "none",
                padding: "0.5rem 1rem",
                borderRadius: "0.5rem",
                cursor: "pointer",
                fontSize: "0.9rem",
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
                boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
              }}
            >
              📊 Sortare {showSortMenu ? '▲' : '▼'}
            </button>
            
            {showSortMenu && (
              <div style={{
                position: "absolute",
                top: "100%",
                right: "0",
                background: "white",
                border: "1px solid #e2e8f0",
                borderRadius: "0.5rem",
                boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                zIndex: 1000,
                minWidth: "200px",
                marginTop: "0.25rem"
              }}>
                <div style={{ padding: "0.5rem", borderBottom: "1px solid #e2e8f0", fontSize: "0.8rem", color: "#6b7280", fontWeight: "600" }}>
                  Sortează după:
                </div>
                {sortOptions.map(option => (
                  <div key={option.key}>
                    <button
                      onClick={() => handleSort(option.key, 'desc')}
                      style={{
                        width: "100%",
                        padding: "0.5rem 0.75rem",
                        border: "none",
                        background: sortBy === option.key && sortOrder === 'desc' ? "#f0f9ff" : "transparent",
                        color: sortBy === option.key && sortOrder === 'desc' ? "#4f46e5" : "#374151",
                        cursor: "pointer",
                        fontSize: "0.9rem",
                        textAlign: "left",
                        display: "flex",
                        alignItems: "center",
                        gap: "0.5rem"
                      }}
                    >
                      {option.icon} {option.label} ↓
                    </button>
                    <button
                      onClick={() => handleSort(option.key, 'asc')}
                      style={{
                        width: "100%",
                        padding: "0.5rem 0.75rem",
                        border: "none",
                        background: sortBy === option.key && sortOrder === 'asc' ? "#f0f9ff" : "transparent",
                        color: sortBy === option.key && sortOrder === 'asc' ? "#4f46e5" : "#374151",
                        cursor: "pointer",
                        fontSize: "0.9rem",
                        textAlign: "left",
                        display: "flex",
                        alignItems: "center",
                        gap: "0.5rem",
                        borderBottom: option.key === sortOptions[sortOptions.length - 1].key ? "none" : "1px solid #f3f4f6"
                      }}
                    >
                      {option.icon} {option.label} ↑
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* 🆕 REAL-TIME UPDATE INDICATOR */}
          <div style={{ fontSize: "0.8rem", color: "#6b7280" }}>
            {lastUpdate && (
              <span style={{ 
                background: isRefreshing ? "#fef3c7" : "#dcfce7", 
                padding: "0.2rem 0.5rem", 
                borderRadius: "0.3rem",
                border: `1px solid ${isRefreshing ? "#f59e0b" : "#22c55e"}`
              }}>
                {isRefreshing ? "🔄 Actualizare..." : `✅ Actualizat: ${lastUpdate}`}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* 🆕 ERROR DISPLAY */}
      {error && (
        <div style={{
          background: "#fef2f2",
          border: "1px solid #fca5a5",
          borderRadius: "0.5rem",
          padding: "1rem",
          marginBottom: "1.5rem",
          color: "#dc2626"
        }}>
          <strong>⚠️ Eroare:</strong> {error}
          <button 
            onClick={() => setError(null)}
            style={{ 
              float: "right", 
              background: "transparent", 
              border: "none", 
              color: "#dc2626", 
              cursor: "pointer",
              fontSize: "1.2rem"
            }}
          >
            ✕
          </button>
        </div>
      )}

      {analize.length === 0 && !error ? (
        <div style={{
          background: "#f0f9ff",
          border: "1px solid #bfdbfe",
          borderRadius: "0.5rem",
          padding: "2rem",
          textAlign: "center",
          color: "#1e40af"
        }}>
          <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>📊</div>
          <div style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>Nu ai efectuat încă nicio analiză</div>
          <div style={{ fontSize: "0.9rem", color: "#6b7280" }}>
            Mergi la pagina de analiză pentru a începe să detectezi fake news!
          </div>
        </div>
      ) : (
        <div style={{ 
          opacity: isRefreshing ? 0.7 : 1,
          transition: "opacity 0.3s ease"
        }}>
          {/* 🆕 STATISTICS SUMMARY */}
          <div style={{
            background: "#f8fafc",
            borderRadius: "0.5rem",
            padding: "1rem",
            marginBottom: "1.5rem",
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
            gap: "1rem"
          }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#4f46e5" }}>
                {analize.length}
              </div>
              <div style={{ fontSize: "0.8rem", color: "#6b7280" }}>Total analize</div>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#e11d48" }}>
                {analize.filter(a => a.rezultat === 'fake' || a.rezultat === 'deepfake').length}
              </div>
              <div style={{ fontSize: "0.8rem", color: "#6b7280" }}>Fake News/Deepfake</div>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#22c55e" }}>
                {analize.filter(a => a.rezultat === 'real' || a.rezultat === 'authentic').length}
              </div>
              <div style={{ fontSize: "0.8rem", color: "#6b7280" }}>Conținut autentic</div>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#8b5cf6" }}>
                {analize.filter(a => a.confidence).length > 0 ? 
                  (analize.filter(a => a.confidence).reduce((sum, a) => sum + a.confidence, 0) / analize.filter(a => a.confidence).length * 100).toFixed(1) + '%' : 
                  'N/A'
                }
              </div>
              <div style={{ fontSize: "0.8rem", color: "#6b7280" }}>Confidență medie</div>
            </div>
          </div>

          {/* 🆕 STRUCTURED TABLE */}
          <div style={{ 
            overflowX: "auto", 
            borderRadius: "0.5rem",
            border: "1px solid #e2e8f0",
            background: "#fff"
          }}>
            <table style={{ 
              width: "100%", 
              borderCollapse: "collapse",
              fontSize: "0.9rem"
            }}>
              <thead>
                <tr style={{ backgroundColor: "#f8fafc", borderBottom: "2px solid #e2e8f0" }}>
                  <th style={{ 
                    padding: "0.75rem", 
                    textAlign: "left", 
                    fontWeight: "600",
                    color: "#374151",
                    cursor: "pointer",
                    userSelect: "none"
                  }} onClick={() => handleSort('data')}>
                    Data {getSortIcon('data')}
                  </th>
                  <th style={{ 
                    padding: "0.75rem", 
                    textAlign: "left", 
                    fontWeight: "600",
                    color: "#374151",
                    cursor: "pointer",
                    userSelect: "none"
                  }} onClick={() => handleSort('tip')}>
                    Tip {getSortIcon('tip')}
                  </th>
                  <th style={{ 
                    padding: "0.75rem", 
                    textAlign: "left", 
                    fontWeight: "600",
                    color: "#374151",
                    cursor: "pointer",
                    userSelect: "none"
                  }} onClick={() => handleSort('rezultat')}>
                    Verdict {getSortIcon('rezultat')}
                  </th>
                  <th style={{ 
                    padding: "0.75rem", 
                    textAlign: "left", 
                    fontWeight: "600",
                    color: "#374151",
                    cursor: "pointer",
                    userSelect: "none"
                  }} onClick={() => handleSort('confidence')}>
                    Confidență {getSortIcon('confidence')}
                  </th>
                  <th style={{ 
                    padding: "0.75rem", 
                    textAlign: "left", 
                    fontWeight: "600",
                    color: "#374151",
                    cursor: "pointer",
                    userSelect: "none"
                  }} onClick={() => handleSort('analysisMode')}>
                    Mod Analiză {getSortIcon('analysisMode')}
                  </th>
                  <th style={{ 
                    padding: "0.75rem", 
                    textAlign: "left", 
                    fontWeight: "600",
                    color: "#374151",
                    cursor: "pointer",
                    userSelect: "none"
                  }} onClick={() => handleSort('detectedLanguage')}>
                    Limba {getSortIcon('detectedLanguage')}
                  </th>
                  <th style={{ 
                    padding: "0.75rem", 
                    textAlign: "left", 
                    fontWeight: "600",
                    color: "#374151"
                  }}>
                    Titlu
                  </th>
                </tr>
              </thead>
              <tbody>
                {analize.map((a, idx) => {
                  const verdict = getVerdictDisplay(a.rezultat);
                  const isNew = lastUpdate && idx === 0; // Presupunem că cea mai nouă este prima după sortare
                  
                  return (
                    <tr key={idx} style={{
                      borderBottom: "1px solid #e2e8f0",
                      backgroundColor: isNew ? "#f0fdf4" : (idx % 2 === 0 ? "#fff" : "#f9fafb"),
                      transition: "background-color 0.3s ease"
                    }}>
                      <td style={{ padding: "0.75rem", color: "#374151" }}>
                        {new Date(a.data).toLocaleDateString('ro-RO', {
                          day: '2-digit',
                          month: '2-digit',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </td>
                      <td style={{ padding: "0.75rem", color: "#6b7280" }}>
                        {a.tip}
                      </td>
                      <td style={{ padding: "0.75rem" }}>
                        <span style={{ 
                          color: verdict.color,
                          fontWeight: "600",
                          fontSize: "0.9rem"
                        }}>
                          {verdict.text}
                        </span>
                      </td>
                      <td style={{ padding: "0.75rem" }}>
                        <ConfidenceBar confidence={a.confidence} />
                      </td>
                      <td style={{ padding: "0.75rem", color: "#6b7280" }}>
                        {a.analysisMode || 'N/A'}
                      </td>
                      <td style={{ padding: "0.75rem", color: "#6b7280" }}>
                        {a.detectedLanguage || 'N/A'}
                      </td>
                      <td style={{ 
                        padding: "0.75rem", 
                        color: "#374151",
                        maxWidth: "200px"
                      }}>
                        <div>
                          <div style={{
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap"
                          }}>
                            <span title={a.titlu}>{a.titlu}</span>
                            {isNew && (
                              <span style={{
                                marginLeft: "0.5rem",
                                background: "#22c55e",
                                color: "white",
                                fontSize: "0.7rem",
                                padding: "0.1rem 0.3rem",
                                borderRadius: "0.2rem"
                              }}>
                                NEW
                              </span>
                            )}
                          </div>
                          <VideoPreview analysis={a} />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}