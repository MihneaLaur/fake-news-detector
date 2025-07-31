/**
 * Componenta Dashboard pentru afisarea statisticilor utilizatorului.
 * Arata analizele recente, grafice si metrici de performanta.
 */

import React, { useEffect, useState } from "react";
import { useAuth } from "../AuthContext";
import { useNotifications } from "../NotificationContext";
import { Pie, Bar } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from "chart.js";
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

/**
 * Componenta principala Dashboard.
 * @returns {JSX.Element} Interface-ul dashboard-ului cu statistici si grafice
 */
export default function Dashboard() {
  const { user, checkAuth, forceLogout } = useAuth();
  const { showDisconnectionAlert, showError } = useNotifications();
  const [analize, setAnalize] = useState([]);
  const [lastAnalysis, setLastAnalysis] = useState(null);
  const [systemStats, setSystemStats] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  
  // 🆕 REAL-TIME UPDATES STATE
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  /**
   * Initializeaza dashboard-ul si configureaza actualizarile in timp real.
   */
  useEffect(() => {
    // Verifică autentificarea înainte de a încărca datele
    const initializeDashboard = async () => {
      await checkAuth();
      loadDashboardData();
      fetchSystemStats();
      fetchSystemStatus();
    };
    
    initializeDashboard();
    
    // 🆕 REAL-TIME UPDATES - Ascultă evenimentele de analiză
    const handleAnalysisCompleted = (event) => {
      console.log('📊 Dashboard: Nouă analiză completată!', event.detail);
      setLastUpdate(new Date().toLocaleTimeString());
      setIsRefreshing(true);
      
      // Actualizează datele după o scurtă întârziere pentru animație
      setTimeout(() => {
        loadDashboardData();
        fetchSystemStats();
        setIsRefreshing(false);
      }, 500);
    };

    window.addEventListener('analysisCompleted', handleAnalysisCompleted);
    
    return () => {
      window.removeEventListener('analysisCompleted', handleAnalysisCompleted);
    };
  }, [user]);

  /**
   * Incarca datele analizelor din baza de date.
   */
  const loadDashboardData = async () => {
    if (!user?.username) {
      console.log('📊 Dashboard: Nu există utilizator autentificat');
      setAnalize([]);
      setLastAnalysis(null);
      return;
    }

    try {
      console.log(`📊 Dashboard: Încărcare analize din baza de date pentru ${user.username}`);
      
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
        const userAnalyses = data.analyses || [];
        
        console.log(`📊 Dashboard: Încărcat ${userAnalyses.length} analize din baza de date`);
        setAnalize(userAnalyses);
        setLastAnalysis(userAnalyses.length > 0 ? userAnalyses[0] : null); // Prima analiză (cea mai recentă)
        
      } else if (response.status === 401) {
        console.warn('📊 Dashboard: Utilizator neautentificat - 401 Unauthorized');
        showDisconnectionAlert();
        forceLogout("Sesiunea a expirat");
        return;
        
      } else {
        console.error('📊 Dashboard: Eroare la încărcarea din API:', response.status);
        // Fallback la localStorage în caz de eroare
        loadDashboardDataFromLocalStorage();
      }
      
    } catch (error) {
      console.error('📊 Dashboard: Eroare la conectarea la API:', error);
      // Fallback la localStorage în caz de eroare de rețea
      loadDashboardDataFromLocalStorage();
    }
  };

  /**
   * Fallback pentru incarcarea din localStorage in caz de eroare.
   */
  const loadDashboardDataFromLocalStorage = () => {
    const userAnalysesKey = `analize_${user?.username || "guest"}`;
    const userAnalize = JSON.parse(localStorage.getItem(userAnalysesKey) || "[]");
    
    console.log(`📊 Dashboard: Fallback localStorage - ${userAnalize.length} analize pentru ${user?.username}`);
    setAnalize(userAnalize);
    setLastAnalysis(userAnalize.length > 0 ? userAnalize[userAnalize.length - 1] : null);
  };

  /**
   * Preia statisticile utilizatorului din baza de date.
   */
  const fetchSystemStats = async () => {
    if (!user?.username) {
      console.log('📊 Dashboard: Nu există utilizator pentru statistici');
      return;
    }

    try {
      console.log(`📊 Dashboard: Încărcare statistici din baza de date pentru ${user.username}`);
      
      const response = await fetch('http://localhost:5000/user-stats', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const stats = await response.json();
        console.log('📊 Dashboard: Statistici încărcate din baza de date:', stats);
        setSystemStats(stats);
      } else if (response.status === 401) {
        console.warn('📊 Dashboard: Utilizator neautentificat pentru statistici - 401 Unauthorized');
        showDisconnectionAlert();
        forceLogout("Sesiunea a expirat");
        return;
      } else {
        console.error('📊 Dashboard: Eroare la încărcarea statisticilor:', response.status);
        setSystemStats(null);
      }
    } catch (err) {
      console.error('📊 Dashboard: Eroare la conectarea pentru statistici:', err);
      setSystemStats(null);
    }
  };

  /**
   * Preia status-ul sistemului de la server.
   */
  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/system-status');
      if (response.ok) {
        const status = await response.json();
        setSystemStatus(status);
      }
    } catch (err) {
      console.error('Eroare la verificarea status-ului:', err);
    }
  };

  // Statistici din localStorage (pentru compatibilitate)
  const total = analize.length;
  const fake = analize.filter(a => a.rezultat === "fake" || a.rezultat === "deepfake").length;
  const real = analize.filter(a => a.rezultat === "real" || a.rezultat === "authentic").length;

  // Statistici avansate
  const avgConfidence = systemStats ? systemStats.average_confidence : 
    analize.filter(a => a.confidence).reduce((sum, a) => sum + a.confidence, 0) / analize.filter(a => a.confidence).length || 0;

  // Pie chart data îmbunătățit
  const pieData = {
    labels: ['Conținut Fals/Deepfake', 'Conținut Autentic'],
    datasets: [
      {
        data: [fake, real],
        backgroundColor: ['#e11d48', '#22c55e'],
        borderColor: ['#fff', '#fff'],
        borderWidth: 2,
      },
    ],
  };

  // Grafic pentru distribuția limbilor
  const languageData = systemStats?.language_distribution || {};
  const langChartData = {
    labels: Object.keys(languageData).map(lang => {
      const langMap = {'ro': 'Română', 'en': 'Engleză', 'fr': 'Franceză', 'es': 'Spaniolă', 'de': 'Germană'};
      return langMap[lang] || lang;
    }),
    datasets: [{
      label: 'Analize pe limbă',
      data: Object.values(languageData),
      backgroundColor: ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'],
      borderRadius: 4,
    }]
  };

  // Grafic pentru moduri de analiză
  const modeData = systemStats?.analysis_mode_distribution || {};
  const modeChartData = {
    labels: Object.keys(modeData).map(mode => {
      const modeMap = {
        'hybrid': 'Hibrid', 
        'ai_only': 'Doar AI', 
        'ml_only': 'Doar ML', 
        'traditional': 'Tradițional'
      };
      return modeMap[mode] || mode;
    }),
    datasets: [{
      label: 'Utilizare moduri analiză',
      data: Object.values(modeData),
      backgroundColor: ['#4f46e5', '#059669', '#dc2626', '#7c3aed'],
      borderRadius: 4,
    }]
  };

  // Tips anti-fake news îmbunătățiți
  const tips = [
    "🔍 Verifică mereu sursa știrii și reputația autorului!",
    "📊 Caută aceeași informație pe mai multe site-uri de încredere.",
    "⚠️ Fii atent la titlurile senzaționale și limbajul emoțional.",
    "📅 Verifică data publicării - știrile vechi pot fi scoase din context.",
    "🚫 Nu distribui înainte să verifici cu sistemul nostru AI+ML!",
    "🤖 Folosește modul hibrid pentru cea mai bună acuratețe.",
    "🌍 Textele în limbi străine beneficiază de analiza multilingvă AI."
  ];
  const tip = tips[Math.floor(Math.random() * tips.length)];

  // 🆕 DEBUG FUNCTION pentru a verifica analizele din localStorage
  const debugLocalStorage = () => {
    const all = JSON.parse(localStorage.getItem("analize") || "[]");
    const byUser = {};
    
    all.forEach(analiza => {
      const username = analiza.username || "UNKNOWN";
      if (!byUser[username]) byUser[username] = [];
      byUser[username].push(analiza);
    });
    
    console.log("🔍 DEBUG localStorage analize:");
    console.log("Total analize:", all.length);
    console.log("Analize pe utilizatori:", byUser);
    console.log("Utilizator curent:", user?.username);
    
    // Calculează statistici detaliate
    const validAnalyses = all.filter(a => a.username && a.username !== "guest" && a.username !== "UNKNOWN").length;
    const invalidAnalyses = all.length - validAnalyses;
    
    const info = Object.keys(byUser).map(username => 
      `  📊 ${username}: ${byUser[username].length} analize`
    ).join('\n');
    
    const debugInfo = `🔍 DEBUG STORAGE ADMINISTRATIV\n\n` +
      `📈 STATISTICI GENERALE:\n` +
      `  • Total analize: ${all.length}\n` +
      `  • Analize valide: ${validAnalyses}\n` +
      `  • Analize invalide: ${invalidAnalyses}\n` +
      `  • Utilizator curent: ${user?.username}\n\n` +
      `👥 DISTRIBUȚIE PE UTILIZATORI:\n${info}\n\n` +
      `💡 TIP: Folosește "Curăță Storage" pentru a elimina analizele invalide.`;
    
    alert(debugInfo);
  };

  // 🆕 CLEAN ORPHANED ANALYSES pentru admin
  const cleanOrphanedAnalyses = () => {
    const all = JSON.parse(localStorage.getItem("analize") || "[]");
    const validAnalyses = all.filter(analiza => analiza.username && analiza.username !== "guest" && analiza.username !== "UNKNOWN");
    
    const removedCount = all.length - validAnalyses.length;
    
    if (removedCount > 0) {
      localStorage.setItem("analize", JSON.stringify(validAnalyses));
      alert(`🧹 CURĂȚARE ADMINISTRATIVĂ COMPLETĂ!\n\n✅ Șters: ${removedCount} analize invalide\n📊 Rămas: ${validAnalyses.length} analize valide\n\n💡 Analizele utilizatorilor autentificați au fost păstrate.`);
      
      // Reîncarcă datele
      loadDashboardData();
      fetchSystemStats();
    } else {
      alert("🎉 STORAGE CURAT!\n\n✅ Nu există analize de curățat\n📊 Toate analizele sunt valide și asociate utilizatorilor\n\n💡 Sistemul funcționează optim!");
    }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h2 style={{ color: "#4f46e5" }}>
          Bine ai venit, {user?.username}! 
          <span style={{ fontSize: "1rem", color: "#a21caf", marginLeft: "0.5rem" }}>
            ({user?.role})
          </span>
        </h2>
        
        {/* 🆕 REAL-TIME UPDATE INDICATOR */}
        <div style={{ fontSize: "0.8rem", color: "#6b7280" }}>
          {lastUpdate && (
            <span style={{ 
              background: isRefreshing ? "#fef3c7" : "#dcfce7", 
              padding: "0.2rem 0.5rem", 
              borderRadius: "0.3rem",
              border: `1px solid ${isRefreshing ? "#f59e0b" : "#22c55e"}`
            }}>
              {isRefreshing ? "🔄 Actualizare..." : `✅ Ultima actualizare: ${lastUpdate}`}
            </span>
          )}
          
          {/* 🆕 DEBUG BUTTON */}
          {user?.role === "admin" && (
            <button 
              onClick={debugLocalStorage}
              style={{
                marginLeft: "1rem",
                background: "#fbbf24",
                color: "#92400e",
                border: "1px solid #f59e0b",
                borderRadius: "0.3rem",
                padding: "0.2rem 0.5rem",
                fontSize: "0.7rem",
                cursor: "pointer"
              }}
            >
              🔍 Debug Storage
            </button>
          )}
          
          {/* 🆕 CLEAN BUTTON */}
          {user?.role === "admin" && (
            <button 
              onClick={cleanOrphanedAnalyses}
              style={{
                marginLeft: "0.5rem",
                background: "#ef4444",
                color: "#ffffff",
                border: "1px solid #dc2626",
                borderRadius: "0.3rem",
                padding: "0.2rem 0.5rem",
                fontSize: "0.7rem",
                cursor: "pointer"
              }}
            >
              🧹 Curăță Storage
            </button>
          )}
        </div>
      </div>

      {/* Status sistem */}
      {systemStatus && (
        <div style={{
          background: "#f0f9ff",
          border: "2px solid #0ea5e9",
          borderRadius: "1rem",
          padding: "1rem",
          marginBottom: "2rem",
          textAlign: "center",
          // 🆕 REFRESH ANIMATION
          opacity: isRefreshing ? 0.7 : 1,
          transition: "opacity 0.3s ease"
        }}>
          <h3 style={{ color: "#0369a1", margin: "0 0 0.5rem 0" }}>🤖 Sistem Hibrid AI + ML</h3>
          <div style={{ fontSize: "0.9rem" }}>
            <span style={{ color: systemStatus.ai_services?.enabled ? "#059669" : "#dc2626" }}>
              AI Services: {systemStatus.ai_services?.enabled ? "✅ Activ" : "❌ Inactiv"}
            </span>
            {" | "}
            <span style={{ color: systemStatus.ml_models?.enabled ? "#059669" : "#dc2626" }}>
              ML Models: {systemStatus.ml_models?.enabled ? "✅ Activ" : "❌ Inactiv"}
            </span>
          </div>
          <div style={{ fontSize: "0.8rem", color: "#6b7280", marginTop: "0.5rem" }}>
            Limbi suportate: {systemStatus.supported_languages?.join(", ")}
          </div>
        </div>
      )}

      {/* Statistici principale */}
      <div style={{
        display: "grid", 
        gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", 
        gap: "1rem", 
        margin: "2rem 0",
        // 🆕 REFRESH ANIMATION
        opacity: isRefreshing ? 0.7 : 1,
        transition: "opacity 0.3s ease"
      }}>
        <div className="stat-card">
          <div className="stat-number">{systemStats?.total || total}</div>
          <div className="stat-label">Analize efectuate</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: "#e11d48" }}>
            {systemStats?.fake || fake}
          </div>
          <div className="stat-label">Conținut fals</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: "#22c55e" }}>
            {systemStats?.real || real}
          </div>
          <div className="stat-label">Conținut autentic</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: "#8b5cf6" }}>
            {(avgConfidence * 100).toFixed(1)}%
          </div>
          <div className="stat-label">Confidență medie</div>
        </div>
        {systemStats?.fake_percentage !== undefined && (
          <div className="stat-card">
            <div className="stat-number" style={{ color: "#f59e0b" }}>
              {systemStats.fake_percentage.toFixed(1)}%
            </div>
            <div className="stat-label">Rata fake news</div>
          </div>
        )}
      </div>

      {/* Grafice */}
      <div style={{ 
        display: "grid", 
        gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", 
        gap: "2rem", 
        margin: "2rem 0",
        // 🆕 REFRESH ANIMATION
        opacity: isRefreshing ? 0.7 : 1,
        transition: "opacity 0.3s ease"
      }}>
        {/* Graficul principal */}
        <div style={{ textAlign: "center" }}>
          <h3 style={{ color: "#6366f1" }}>Distribuția analizelor</h3>
          <div style={{ maxWidth: 300, margin: "0 auto" }}>
            <Pie data={pieData} />
          </div>
        </div>

        {/* Grafic limbile */}
        {Object.keys(languageData).length > 0 && (
          <div style={{ textAlign: "center" }}>
            <h3 style={{ color: "#6366f1" }}>Analize pe limbi</h3>
            <Bar 
              data={langChartData} 
              options={{
                scales: { y: { beginAtZero: true } },
                plugins: { legend: { display: false } }
              }} 
            />
          </div>
        )}

        {/* Grafic moduri analiză */}
        {Object.keys(modeData).length > 0 && (
          <div style={{ textAlign: "center" }}>
            <h3 style={{ color: "#6366f1" }}>Moduri de analiză folosite</h3>
            <Bar 
              data={modeChartData} 
              options={{
                scales: { y: { beginAtZero: true } },
                plugins: { legend: { display: false } }
              }} 
            />
          </div>
        )}
      </div>

      {/* 🆕 MINI-TIMELINE cu ultimele 5 analize - MOVED AFTER CHARTS */}
      {analize.length > 0 && (
        <div style={{
          background: "#fff",
          borderRadius: "1rem",
          padding: "1.5rem",
          marginBottom: "2rem",
          boxShadow: "0 2px 8px rgba(79,70,229,0.08)",
          border: "1px solid #e2e8f0"
        }}>
          <h3 style={{ color: "#4f46e5", marginBottom: "1rem", fontSize: "1.1rem" }}>
            📈 Activitate Recentă
          </h3>
          <div style={{ display: "grid", gap: "0.75rem" }}>
            {analize.slice(0, 5).map((analiza, index) => {
              const verdict = analiza.rezultat === 'fake' || analiza.rezultat === 'deepfake' ? 
                { icon: '🚨', color: '#e11d48', text: 'FAKE' } :
                analiza.rezultat === 'real' || analiza.rezultat === 'authentic' ?
                { icon: '✅', color: '#22c55e', text: 'REAL' } :
                { icon: '❓', color: '#f59e0b', text: 'NECONCLUDENT' };
              
              const timeAgo = new Date(analiza.data);
              const now = new Date();
              const diffMinutes = Math.floor((now - timeAgo) / (1000 * 60));
              const timeText = diffMinutes < 1 ? 'Acum' :
                             diffMinutes < 60 ? `Acum ${diffMinutes} min` :
                             diffMinutes < 1440 ? `Acum ${Math.floor(diffMinutes / 60)} ore` :
                             `Acum ${Math.floor(diffMinutes / 1440)} zile`;

              return (
                <div key={index} style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "1rem",
                  padding: "0.75rem",
                  borderRadius: "0.5rem",
                  background: index === 0 && lastUpdate ? "#f0fdf4" : "#f8fafc",
                  border: index === 0 && lastUpdate ? "1px solid #bbf7d0" : "1px solid #e2e8f0",
                  transition: "all 0.2s ease"
                }}>
                  <div style={{ 
                    fontSize: "1.2rem",
                    minWidth: "2rem",
                    textAlign: "center"
                  }}>
                    {verdict.icon}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ 
                      fontWeight: "500", 
                      color: "#374151",
                      fontSize: "0.9rem",
                      marginBottom: "0.25rem"
                    }}>
                      {analiza.titlu.length > 50 ? analiza.titlu.substring(0, 50) + '...' : analiza.titlu}
                    </div>
                    <div style={{ 
                      fontSize: "0.8rem", 
                      color: "#6b7280",
                      display: "flex",
                      gap: "1rem"
                    }}>
                      <span>{timeText}</span>
                      <span>•</span>
                      <span style={{ color: verdict.color, fontWeight: "500" }}>
                        {verdict.text}
                      </span>
                      {analiza.confidence && (
                        <>
                          <span>•</span>
                          <span>{(analiza.confidence * 100).toFixed(0)}% confidență</span>
                        </>
                      )}
                    </div>
                  </div>
                  {index === 0 && lastUpdate && (
                    <div style={{
                      background: "#22c55e",
                      color: "white",
                      fontSize: "0.7rem",
                      padding: "0.2rem 0.5rem",
                      borderRadius: "0.3rem",
                      fontWeight: "500"
                    }}>
                      NOU
                    </div>
                  )}
                </div>
              );
            })}
          </div>
          {analize.length > 5 && (
            <div style={{ textAlign: "center", marginTop: "1rem" }}>
              <a 
                href="/history" 
                style={{
                  color: "#4f46e5",
                  textDecoration: "none",
                  fontSize: "0.9rem",
                  fontWeight: "500"
                }}
              >
                Vezi toate analizele ({analize.length}) →
              </a>
            </div>
          )}
        </div>
      )}

      {/* Tip anti-fake news */}
      <div style={{
        background: "linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%)", 
        borderRadius: "1rem", 
        padding: "1.5rem", 
        textAlign: "center", 
        marginTop: "2rem",
        border: "2px solid #a5b4fc"
      }}>
        <h4 style={{ color: "#4338ca", margin: "0 0 0.5rem 0" }}>💡 Tip Anti-Fake News</h4>
        <div style={{ fontSize: "1.1rem", color: "#1e1b4b" }}>{tip}</div>
      </div>

      {/* Surse de încredere îmbunătățite */}
      <div style={{ 
        marginTop: "2rem", 
        textAlign: "center",
        background: "#f8fafc",
        borderRadius: "1rem",
        padding: "1.5rem"
      }}>
        <h4 style={{ color: "#4338ca", marginBottom: "1rem" }}>🔗 Surse de verificare recomandate</h4>
        <div style={{ 
          display: "grid", 
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", 
          gap: "1rem" 
        }}>
          <a href="https://www.snopes.com/" target="_blank" rel="noopener noreferrer" 
             style={{ color: "#059669", textDecoration: "none", fontWeight: "500" }}>
            📊 Snopes.com (International)
          </a>
          <a href="https://www.factcheck.org/" target="_blank" rel="noopener noreferrer"
             style={{ color: "#059669", textDecoration: "none", fontWeight: "500" }}>
            ✅ FactCheck.org (SUA)
          </a>
          <a href="https://www.veridica.ro/" target="_blank" rel="noopener noreferrer"
             style={{ color: "#059669", textDecoration: "none", fontWeight: "500" }}>
            🇷🇴 Veridica.ro (România)
          </a>
          <a href="https://www.politifact.com/" target="_blank" rel="noopener noreferrer"
             style={{ color: "#059669", textDecoration: "none", fontWeight: "500" }}>
            🏛️ PolitiFact (Politic)
          </a>
        </div>
      </div>
    </div>
  );
}