/**
 * Componenta React pentru upload si analiza continutului (text, fisiere, linkuri, video).
 * Suporta multiple moduri de analiza: traditional, hibrid, AI-only, ML-only.
 * Gestioneaza conectarea la backend si fallback la demo mode.
 */

import React, { useState, useEffect } from "react";
import { useAuth } from "../AuthContext";
import { useNotifications } from "../NotificationContext";

export default function Upload() {
  const { user, forceLogout } = useAuth();
  const { showDisconnectionAlert, showError } = useNotifications();
  /**
   * State pentru tipul de continut selectat (text, file, link, video).
   */
  const [tip, setTip] = useState("text");
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [link, setLink] = useState("");
  const [result, setResult] = useState(null);
  const [analysisMode, setAnalysisMode] = useState("traditional");
  
  /**
   * State pentru modurile de analiza disponibile si configurarile lor.
   */
  const [availableModes, setAvailableModes] = useState({
    'traditional': {
      'name': 'Model Tradițional',
      'description': 'TF-IDF + Logistic Regression - Rapid și eficient',
      'accuracy': 'Medie',
      'speed': 'Foarte rapidă',
      'languages': ['en', 'parțial multilingv']
    },
    'hybrid': {
      'name': 'Analiză Hibridă (DEMO)',
      'description': 'Combină AI și ML - Necesită configurare avansată',
      'accuracy': 'Foarte mare',
      'speed': 'Medie',
      'languages': ['ro', 'en', 'fr', 'es', 'de', 'it']
    },
    'ai_only': {
      'name': 'Doar AI (DEMO)',
      'description': 'OpenAI GPT + Google Perspective - Necesită API keys',
      'accuracy': 'Mare',
      'speed': 'Rapidă',
      'languages': ['6+ limbi majore']
    },
    'ml_only': {
      'name': 'Doar ML (DEMO)', 
      'description': 'mBERT + Sentence Transformers - Necesită modele pre-antrenate',
      'accuracy': 'Mare',
      'speed': 'Rapidă',
      'languages': ['ro', 'en', 'fr', 'es', 'de', 'it']
    }
  });
  /**
   * State pentru statusul sistemului si disponibilitatea serviciilor.
   */
  const [systemStatus, setSystemStatus] = useState({
    'system_status': 'checking',
    'ai_services': { 'enabled': false },
    'ml_models': { 'enabled': false, 'traditional': false }
  });
  const [isLoading, setIsLoading] = useState(false);
  const [backendAvailable, setBackendAvailable] = useState(false);
  
  /**
   * State pentru gestionarea erorilor si progresului upload-ului.
   */
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [systemHealth, setSystemHealth] = useState({
    backend: 'checking',
    ai_services: 'checking',
    ml_models: 'checking',
    response_time: null,
    last_check: null
  });

  /**
   * State pentru preferințele utilizatorului
   */
  const [userPreferences, setUserPreferences] = useState({
    defaultAnalysisMode: 'traditional',
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
          console.log(`🎯 Încărcat mod implicit: ${preferences.defaultAnalysisMode} pentru ${user.username}`);
        }
        
        console.log(`⚙️ Preferințe încărcate:`, preferences);
      }
    } catch (error) {
      console.error('Eroare la încărcarea preferințelor:', error);
    }
  };

  /**
   * Initializeaza componenta si verifica disponibilitatea backend-ului.
   */
  useEffect(() => {
    checkBackendAvailability();
    loadUserPreferences();
  }, [user]);

  /**
   * Verifica disponibilitatea backend-ului si incarca modurile de analiza.
   * Masoara timpul de raspuns si actualizeaza statusul sanatatii sistemului.
   */
  const checkBackendAvailability = async () => {
    const startTime = Date.now();
    try {
      setSystemHealth(prev => ({ ...prev, backend: 'checking' }));
      
      const response = await fetch('http://localhost:5000/system-status');
      const responseTime = Date.now() - startTime;
      
      if (response.ok) {
        const status = await response.json();
        setSystemStatus(status);
        setBackendAvailable(true);
        setError(null); // Clear any previous errors
        
        setSystemHealth({
          backend: 'operational',
          ai_services: status.ai_services?.enabled ? 'operational' : 'limited',
          ml_models: status.ml_models?.enabled ? 'operational' : 'limited',
          response_time: responseTime,
          last_check: new Date().toLocaleTimeString()
        });
        
        console.log('✅ Backend operațional:', status);
        
        // Încarcă și modurile de analiză
        const modesResponse = await fetch('http://localhost:5000/analysis-modes');
        if (modesResponse.ok) {
          const modes = await modesResponse.json();
          setAvailableModes(modes);
          console.log('✅ Moduri de analiză încărcate:', modes);
        }
      }
    } catch (err) {
      const responseTime = Date.now() - startTime;
      console.warn('❌ Backend nu este disponibil, folosesc demo mode:', err.message);
      setBackendAvailable(false);
      setError('Backend indisponibil: ' + err.message);
      
      setSystemHealth({
        backend: 'error',
        ai_services: 'error',
        ml_models: 'error',
        response_time: responseTime,
        last_check: new Date().toLocaleTimeString()
      });
      
      setSystemStatus({
        'system_status': 'demo_mode',
        'ai_services': { 'enabled': false },
        'ml_models': { 'enabled': false, 'traditional': false }
      });
    }
  };

  /**
   * Gestioneaza submit-ul formularului si directioneaza spre functia corespunzatoare.
   * @param {Event} e - Evenimentul de submit al formularului
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    let content = "";
    
    setError(null);
    setUploadProgress(0);

    if (tip === "text") {
      if (text.trim() === "") {
        setError("Introdu textul articolului!");
        return;
      }
      content = text;
      await detectFakeNews(content, "Articol text (scris manual)", text);
          } else if (tip === "file") {
        if (!file) {
          setError("Încarcă un fișier!");
          return;
        }
        const reader = new FileReader();
        reader.onload = async (ev) => {
          content = ev.target.result;
          await detectFakeNews(content, "Articol text (fișier)", file.name);
        };
        reader.readAsText(file);
        return;
      } else if (tip === "link") {
        if (!link.trim()) {
          setError("Introdu un link!");
          return;
        }
        await detectFakeNews(link, "Articol text (link)", link, true);
      } else if (tip === "video") {
        if (!file) {
          setError("Încarcă un fișier video!");
          return;
        }
        if (!file.type.startsWith('video/')) {
          setError("Fișierul selectat nu este un video valid!");
          return;
        }
        if (file.size > 100 * 1024 * 1024) {
          setError("Fișierul video este prea mare! Mărimea maximă este 100MB.");
          return;
        }
        await analyzeVideo(file);
        return;
      }
    };

  /**
   * Simuleaza progresul upload-ului pentru feedback vizual utilizator.
   * @returns {number} Intervalul pentru oprirea simularii
   */
  const simulateProgress = () => {
    setUploadProgress(0);
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(interval);
          return 90; // Keep at 90% until real completion
        }
        return prev + Math.random() * 15;
      });
    }, 200);
    return interval;
  };

  /**
   * Analizeaza un fisier video pentru detectia deepfake si manipulari.
   * @param {File} videoFile - Fisierul video pentru analiza
   */
  const analyzeVideo = async (videoFile) => {
    setIsLoading(true);
    setError(null);
    
    // 🆕 START PROGRESS SIMULATION
    const progressInterval = simulateProgress();
    
    try {
      // Creează FormData pentru upload video
      const formData = new FormData();
      formData.append('video', videoFile);
      formData.append('mode', analysisMode);
      formData.append('analysis_type', 'video');

      console.log('📹 Începe analiza video:', videoFile.name);

      // Încearcă backend-ul real pentru video
      const response = await fetch('http://localhost:5000/analyze-video', {
        method: 'POST',
        body: formData,
        credentials: "include"
      });

      // 🆕 COMPLETE PROGRESS
      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Analiza video completă:', data);
        setResult(data);
        setError(null);
        
        // ✅ ANALIZA VIDEO SE SALVEAZĂ AUTOMAT ÎN BAZA DE DATE DE CĂTRE BACKEND
        // Nu mai salvez în localStorage - backend-ul salvează automat în baza de date
        console.log('✅ Analiză video salvată automat în baza de date de către backend');
        
        // Creez obiectul pentru event-ul de actualizare (fără salvare în localStorage)
        const user = JSON.parse(localStorage.getItem("loggedUser"));
        const newAnalysis = {
          username: user?.username || "guest",
          tip: "Video Deep Fake Detection",
          titlu: videoFile.name,
          rezultat: data.verdict,
          confidence: data.confidence,
          explanation: data.explanation,
          analysisMode: data.analysis_mode || 'video_ai',
          detectedLanguage: data.detected_language || 'visual',
          processingTime: data.processing_time,
          videoMetadata: data.video_metadata,
          data: new Date().toLocaleString()
        };
        
        // 🆕 REAL-TIME UPDATES - Emit event pentru alte componente
        window.dispatchEvent(new CustomEvent('analysisCompleted', {
          detail: {
            analysis: newAnalysis,
            result: data,
            timestamp: new Date().toISOString()
          }
        }));
        
      } else if (response.status === 401) {
        // 🚪 DECONECTARE DETECTATĂ
        console.warn('🚪 Utilizator deconectat - 401 Unauthorized');
        showDisconnectionAlert();
        forceLogout("Sesiunea a expirat în timpul analizei video");
        return;
      } else if (response.status === 404) {
        // Backend-ul nu suportă analiza video - folosește DEMO
        console.warn('⚠️ Backend nu suportă analiza video, folosesc demo mode');
        const demoResult = generateDemoVideoResult(videoFile);
        setResult(demoResult);
        
        // ⚠️ DEMO MODE - Salvez doar în localStorage pentru demo (nu în baza de date)
        const user = JSON.parse(localStorage.getItem("loggedUser"));
        const userAnalysesKey = `analize_${user?.username || "guest"}`;
        const userAnalize = JSON.parse(localStorage.getItem(userAnalysesKey) || "[]");
        const newAnalysis = {
          username: user?.username || "guest",
          tip: "Video Deep Fake Detection (DEMO)",
          titlu: videoFile.name,
          rezultat: demoResult.verdict,
          confidence: demoResult.confidence,
          explanation: demoResult.explanation,
          analysisMode: 'video_demo',
          detectedLanguage: 'visual',
          processingTime: demoResult.processing_time,
          data: new Date().toLocaleString()
        };
        userAnalize.push(newAnalysis);
        localStorage.setItem(userAnalysesKey, JSON.stringify(userAnalize));
        
        console.log('⚠️ Analiză demo salvată doar în localStorage (nu în baza de date)');
        
        // 🆕 REAL-TIME UPDATES
        window.dispatchEvent(new CustomEvent('analysisCompleted', {
          detail: {
            analysis: newAnalysis,
            result: demoResult,
            timestamp: new Date().toISOString()
          }
        }));
        
      } else {
        const errorData = await response.json();
        console.error('❌ Eroare la analiza video:', errorData);
        showError('Eroare la analiza video: ' + (errorData.error || 'Eroare necunoscută'));
        setError('Eroare la analiza video: ' + (errorData.error || 'Eroare necunoscută'));
      }
    } catch (err) {
      clearInterval(progressInterval);
      setUploadProgress(0);
      console.error('❌ Eroare completă la analiza video:', err);
      
      // În caz de eroare, folosește demo mode
      console.log('🎬 Folosesc demo mode pentru video analysis');
      const demoResult = generateDemoVideoResult(videoFile);
      setResult(demoResult);
      setError(null);
      
      // ⚠️ DEMO MODE - Salvez doar în localStorage pentru demo (nu în baza de date)
      const user = JSON.parse(localStorage.getItem("loggedUser"));
      const userAnalysesKey = `analize_${user?.username || "guest"}`;
      const userAnalize = JSON.parse(localStorage.getItem(userAnalysesKey) || "[]");
      const newAnalysis = {
        username: user?.username || "guest",
        tip: "Video Deep Fake Detection (DEMO)",
        titlu: videoFile.name,
        rezultat: demoResult.verdict,
        confidence: demoResult.confidence,
        explanation: demoResult.explanation,
        analysisMode: 'video_demo',
        detectedLanguage: 'visual',
        processingTime: demoResult.processing_time,
        data: new Date().toLocaleString()
      };
      userAnalize.push(newAnalysis);
      localStorage.setItem(userAnalysesKey, JSON.stringify(userAnalize));
      
      console.log('⚠️ Analiză demo salvată doar în localStorage (nu în baza de date)');
      
      // 🆕 REAL-TIME UPDATES
      window.dispatchEvent(new CustomEvent('analysisCompleted', {
        detail: {
          analysis: newAnalysis,
          result: demoResult,
          timestamp: new Date().toISOString()
        }
      }));
    } finally {
      setIsLoading(false);
      setTimeout(() => setUploadProgress(0), 2000); // Reset progress after 2s
    }
  };

  /**
   * Analizeaza continutul text pentru detectia fake news.
   * @param {string} content - Continutul pentru analiza
   * @param {string} tipArticol - Tipul articolului (text, fisier, link)
   * @param {string} titluArticol - Titlul sau numele fisierului
   * @param {boolean} isUrl - Daca continutul este un URL
   */
  const detectFakeNews = async (content, tipArticol, titluArticol, isUrl = false) => {
    setIsLoading(true);
    setError(null);
    
    const progressInterval = simulateProgress();
    
    try {
      const requestBody = {
        mode: analysisMode
      };
      
      if (isUrl) {
        requestBody.url = content;
      } else {
        requestBody.text = content;
      }

      // Încearcă backend-ul real cu timeout din preferințe
      const timeoutMs = userPreferences.analysisTimeout * 1000;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...requestBody,
          userPreferences: {
            confidenceThreshold: userPreferences.confidenceThreshold,
            analysisTimeout: userPreferences.analysisTimeout,
            defaultAnalysisMode: userPreferences.defaultAnalysisMode
          }
        }),
        credentials: "include",
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      // 🆕 COMPLETE PROGRESS
      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Predicție de la backend real:', data);
        
        // Verifică pragul de confidență din preferințe
        const confidenceThreshold = userPreferences.confidenceThreshold / 100;
        if (data.confidence < confidenceThreshold) {
          data.verdict = 'neconcludent';
          data.explanation = `⚠️ REZULTAT NECONCLUDENT\n\nConfidența (${(data.confidence * 100).toFixed(1)}%) este sub pragul setat (${userPreferences.confidenceThreshold}%).\n\nExplicația originală:\n${data.explanation}`;
          console.log(`⚠️ Rezultat marcat ca neconcludent: ${(data.confidence * 100).toFixed(1)}% < ${userPreferences.confidenceThreshold}%`);
        }
        
        setResult(data);
        setError(null);
        
        // ✅ ANALIZA SE SALVEAZĂ AUTOMAT ÎN BAZA DE DATE DE CĂTRE BACKEND
        // Nu mai salvez în localStorage - backend-ul salvează automat în baza de date
        console.log('✅ Analiză salvată automat în baza de date de către backend');
        
        // Creez obiectul pentru event-ul de actualizare (fără salvare în localStorage)
        const user = JSON.parse(localStorage.getItem("loggedUser"));
        const newAnalysis = {
          username: user?.username || "guest",
          tip: tipArticol,
          titlu: titluArticol,
          rezultat: data.verdict,
          confidence: data.confidence,
          explanation: data.explanation,
          analysisMode: data.analysis_mode,
          detectedLanguage: data.detected_language,
          processingTime: data.processing_time,
          data: new Date().toLocaleString()
        };
        
        // 🆕 REAL-TIME UPDATES - Emit event pentru alte componente
        window.dispatchEvent(new CustomEvent('analysisCompleted', {
          detail: {
            analysis: newAnalysis,
            result: data,
            timestamp: new Date().toISOString()
          }
        }));
        
      } else if (response.status === 401) {
        // 🚪 DECONECTARE DETECTATĂ
        console.warn('🚪 Utilizator deconectat - 401 Unauthorized');
        showDisconnectionAlert();
        forceLogout("Sesiunea a expirat în timpul analizei");
        return;
      } else {
        const errorData = await response.json();
        console.error('❌ Eroare de la backend:', errorData);
        showError('Eroare la analiză: ' + (errorData.error || 'Eroare necunoscută'));
        setError('Eroare la analiză: ' + (errorData.error || 'Eroare necunoscută'));
      }
    } catch (err) {
      clearInterval(progressInterval);
      setUploadProgress(0);
      console.error('❌ Eroare completă:', err);
      
      // 🆕 DETAILED ERROR HANDLING
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError('Nu se poate conecta la server. Verifică dacă backend-ul rulează pe localhost:5000.');
      } else if (err.message.includes('timeout')) {
        setError('Timeout: Serverul nu răspunde în timp util. Încearcă din nou.');
      } else {
        setError('Eroare la conectarea la server: ' + err.message);
      }
    } finally {
      setIsLoading(false);
      setTimeout(() => setUploadProgress(0), 2000); // Reset progress after 2s
    }
  };

  /**
   * Genereaza un rezultat demo pentru analiza video bazat pe numele fisierului.
   * @param {File} videoFile - Fisierul video pentru care se genereaza rezultatul demo
   * @returns {Object} Obiectul cu rezultatul analizei demo
   */
  const generateDemoVideoResult = (videoFile) => {
    // Analizează numele fișierului și mărimea pentru a genera un rezultat realist
    const fileName = videoFile.name.toLowerCase();
    const fileSize = videoFile.size;
    const filetype = videoFile.type;
    const deepfakeKeywords = ['deepfake', 'synthetic', 'generated', 'ai_generated', 'artificial', 'manipulated'];
    const authenticKeywords = ['original', 'raw', 'authentic', 'real', 'genuine', 'unedited', 'camera', 'phone'];
    
    const deepfakeScore = deepfakeKeywords.filter(keyword => fileName.includes(keyword)).length;
    const authenticScore = authenticKeywords.filter(keyword => fileName.includes(keyword)).length;
    let isDeepfake = false;
    let baseConfidence = 0.75 + Math.random() * 0.2;
    
    if (deepfakeScore > 0) {
      isDeepfake = true;
      baseConfidence = 0.85 + Math.random() * 0.1;
          } else if (authenticScore > 0) {
        isDeepfake = false;
        baseConfidence = 0.80 + Math.random() * 0.15;
      } else {
        isDeepfake = Math.random() < 0.2;
        baseConfidence = isDeepfake ? 0.70 + Math.random() * 0.15 : 0.75 + Math.random() * 0.2;
      }
    
    const confidence = Math.min(baseConfidence, 0.95);
    const frameRate = [24, 30, 60][Math.floor(Math.random() * 3)];
    const resolution = ['720p', '1080p', '4K'][Math.floor(Math.random() * 3)];
    const duration = Math.random() * 300 + 10; // 10-310 secunde
    
    const detectionMethods = [
      'Temporal Inconsistency Analysis',
      'Facial Landmark Detection',
      'Pixel-level Artifact Detection',
      'Frame Interpolation Analysis',
      'Audio-Visual Synchronization Check',
      'Compression Artifact Analysis'
    ];
    
    const flaggedMethods = detectionMethods.slice(0, Math.floor(Math.random() * 3) + 2);
    const verdictText = isDeepfake ? 'DEEPFAKE DETECTAT' : 'VIDEO AUTENTIC';
    const riskDescription = isDeepfake ? 
      'conține semne de manipulare digitală sau deepfake' : 
      'pare să fie un video autentic, nemanipulat';
    
          return {
        verdict: isDeepfake ? 'deepfake' : 'authentic',
      confidence: confidence,
      explanation: `🎬 ANALIZĂ DEEPFAKE DETECTION (DEMO):\n\n` +
        `Algoritmi de detecție aplicați:\n` +
        `${flaggedMethods.map(method => `• ${method}: ${isDeepfake ? '⚠️ Anomalii detectate' : '✅ Normal'}`).join('\n')}\n\n` +
        `📊 REZULTAT: ${verdictText}\n` +
        `Video ${riskDescription}.\n` +
        `Nivel de confidență: ${(confidence * 100).toFixed(1)}%\n\n` +
        `🔍 Detalii tehnice:\n` +
        `• Frame-uri analizate: ${Math.floor(duration * frameRate)}\n` +
        `• Frame-uri suspecte: ${isDeepfake ? Math.floor(Math.random() * 50) + 10 : Math.floor(Math.random() * 5)}\n` +
        `• Calitate video: ${(Math.random() * 0.3 + 0.7).toFixed(2)}\n\n` +
        `⚠️ NOTA: Aceasta este o analiză demo. Pentru detecție precisă de deepfake sunt necesari algoritmi specializați de video forensics.`,
      analysis_mode: 'video_demo',
      detected_language: 'visual',
      processing_time: 15.3 + Math.random() * 10,
      video_metadata: {
        filename: videoFile.name,
        size_mb: (fileSize / 1024 / 1024).toFixed(2),
        type: filetype,
        estimated_duration: duration.toFixed(1) + 's',
        estimated_resolution: resolution,
        estimated_fps: frameRate,
        detected_codec: ['H.264', 'H.265', 'VP9'][Math.floor(Math.random() * 3)]
      },
      detection_details: {
        methods_used: flaggedMethods,
        total_frames_analyzed: Math.floor(duration * frameRate),
        suspicious_frames: isDeepfake ? Math.floor(Math.random() * 50) + 10 : Math.floor(Math.random() * 5),
        quality_score: Math.random() * 0.3 + 0.7
      },
      risk_level: isDeepfake ? 'high' : 'low',
      recommendations: isDeepfake ? [
        '🔍 Verifică sursa originală a videoclipului',
        '🌐 Caută videoclipul pe platforme multiple',
        '📅 Verifică contextul și data publicării originale',
        '🛠️ Folosește tool-uri suplimentare de deepfake detection',
        '👥 Consultă experți în video forensics pentru confirmare'
      ] : [
        '✅ Videoclipul pare autentic',
        '📋 Continuă cu verificarea contextului și sursei',
        '🔗 Verifică credibilitatea sursei originale',
        '📱 Videoclipul poate fi utilizat cu încredere'
      ]
    };
  };

  /**
   * Genereaza un rezultat demo pentru analiza text bazat pe continut si mod.
   * @param {string} content - Continutul textual pentru analiza
   * @param {string} mode - Modul de analiza (traditional, hybrid, ai_only, ml_only)
   * @returns {Object} Obiectul cu rezultatul analizei demo
   */
  const generateDemoResult = (content, mode) => {
    // Analizează textul pentru a genera un rezultat realist
    const text = content.toLowerCase();
    const fakeKeywords = ['breaking', 'urgent', 'secret', 'hidden', 'conspiracy', 'robot', 'alien', 'fake', 'hoax', 'scandal'];
    const realKeywords = ['study', 'research', 'university', 'published', 'scientists', 'data', 'analysis', 'evidence'];
    
    const fakeScore = fakeKeywords.filter(keyword => text.includes(keyword)).length;
    const realScore = realKeywords.filter(keyword => text.includes(keyword)).length;
    
    const isFake = fakeScore > realScore || text.includes('breaking news');
    const confidence = Math.min(0.6 + Math.random() * 0.3, 0.95); // Între 0.6 și 0.95
    
    const demoResultsByMode = {
      'traditional': {
        verdict: isFake ? 'fake' : 'real',
        confidence: confidence,
        explanation: `Model tradițional (DEMO): Detectat ${fakeScore} indicatori de fake news și ${realScore} indicatori de știri reale. Algoritmul TF-IDF + Logistic Regression indică o probabilitate de ${(confidence * 100).toFixed(1)}% pentru ${isFake ? 'fake news' : 'știre reală'}.`,
        analysis_mode: 'traditional',
        detected_language: 'auto',
        processing_time: 0.05
      },
      'hybrid': {
        verdict: isFake ? 'fake' : 'real',
        confidence: Math.min(confidence + 0.1, 0.98),
        explanation: `Analiza hibridă (DEMO): Consensul între AI și ML confirmă ${isFake ? 'fake news' : 'știre reală'}. Sistemele de verificare au identificat ${fakeScore} semnale de alarmă în conținut.`,
        analysis_mode: 'hybrid',
        detected_language: 'ro',
        processing_time: 2.3,
        risk_level: isFake ? 'high' : 'low',
        ai_ml_agreement: true,
        consensus_strength: 'strong',
        individual_verdicts: {
          ai: isFake ? 'fake' : 'real',
          ml: isFake ? 'fake' : 'real'
        }
      },
      'ai_only': {
        verdict: isFake ? 'fake' : 'real',
        confidence: Math.min(confidence + 0.05, 0.96),
        explanation: `AI Analysis (DEMO): OpenAI GPT a detectat ${isFake ? 'limbaj manipulativ și afirmații false' : 'conținut factual și tonul neutru'}. Google Perspective a evaluat toxicitatea ca fiind ${isFake ? 'ridicată' : 'scăzută'}.`,
        analysis_mode: 'ai_only',
        detected_language: 'en',
        processing_time: 1.8
      },
      'ml_only': {
        verdict: isFake ? 'fake' : 'real',
        confidence: confidence,
        explanation: `ML Analysis (DEMO): mBERT indică sentiment ${isFake ? 'extrem' : 'neutru'}, Sentence Transformers găsește similaritate ${isFake ? 'ridicată' : 'scăzută'} cu știri false cunoscute.`,
        analysis_mode: 'ml_only',
        detected_language: 'ro',
        processing_time: 1.2
      }
    };
    
    return demoResultsByMode[mode] || demoResultsByMode['traditional'];
  };

  /**
   * Returneaza culoarea corespunzatoare pentru afisarea verdictului.
   * @param {string} verdict - Verdictul analizei
   * @returns {string} Codul culorii hex
   */
  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case 'fake': return '#e11d48';
      case 'real': return '#22c55e';
      case 'deepfake': return '#dc2626';
      case 'authentic': return '#16a34a';
      case 'inconclusive': 
    case 'neconcludent': return '#f59e0b';
      default: return '#f59e0b';
    }
  };

  /**
   * Genereaza o bara de confidenta vizuala pentru rezultatul analizei.
   * @param {number} confidence - Valoarea confidentei (0-1)
   * @returns {JSX.Element} Componenta bara de confidenta
   */
  const getConfidenceBar = (confidence) => {
    const percentage = confidence * 100;
    const color = percentage > 70 ? '#22c55e' : percentage > 40 ? '#f59e0b' : '#e11d48';
    
    return (
      <div style={{ marginTop: '10px' }}>
        <div style={{ fontSize: '0.9rem', marginBottom: '5px' }}>
          Confidența: {percentage.toFixed(1)}%
        </div>
        <div style={{
          width: '100%',
          height: '8px',
          backgroundColor: '#e5e7eb',
          borderRadius: '4px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${percentage}%`,
            height: '100%',
            backgroundColor: color,
            transition: 'width 0.3s ease'
          }}></div>
        </div>
      </div>
    );
  };

  /**
   * Formateaza explicatia rezultatului pentru afisare cu randuri separate.
   * @param {string} explanation - Textul explicatiei
   * @returns {JSX.Element[]} Array de elemente div cu randurile explicatiei
   */
  const formatExplanation = (explanation) => {
    return explanation.split('\n').map((line, i) => (
      <div key={i} style={{ marginBottom: '8px' }}>
        {line}
      </div>
    ));
  };

  /**
   * Returneaza culoarea pentru statusul sanatatii sistemului.
   * @param {string} status - Statusul sistemului (operational, limited, checking, error)
   * @returns {string} Codul culorii hex
   */
  const getHealthStatusColor = (status) => {
    switch (status) {
      case 'operational': return '#22c55e';
      case 'limited': return '#f59e0b';
      case 'checking': return '#6366f1';
      case 'error': return '#e11d48';
      default: return '#6b7280';
    }
  };

  return (
    <div>
      <h2 style={{ color: "#4f46e5", marginBottom: "1.5rem" }}>
        Analiză Avansată Fake News - AI + ML
      </h2>
      <div style={{
        background: backendAvailable ? "#d1fae5" : "#fff3cd",
        border: `1px solid ${backendAvailable ? '#22c55e' : '#ffd700'}`,
        borderRadius: "0.5rem",
        padding: "1rem",
        marginBottom: "1.5rem",
        fontSize: "0.9rem"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
          <strong>
            {backendAvailable ? '✅ SISTEM HIBRID AI+ML OPERAȚIONAL' : '🔄 MODUL DEMO'}
          </strong>
          {systemHealth.response_time && (
            <span style={{ fontSize: "0.8rem", color: "#6b7280" }}>
              Timp răspuns: {systemHealth.response_time}ms | Ultima verificare: {systemHealth.last_check}
            </span>
          )}
        </div>
        
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "0.5rem", marginTop: "0.5rem" }}>
          <div>
            <span style={{ color: getHealthStatusColor(systemHealth.backend) }}>
              Backend: {systemHealth.backend === 'operational' ? '✅' : systemHealth.backend === 'checking' ? '🔄' : '❌'} {systemHealth.backend}
            </span>
          </div>
          <div>
            <span style={{ color: getHealthStatusColor(systemHealth.ai_services) }}>
              AI Services: {systemHealth.ai_services === 'operational' ? '✅' : systemHealth.ai_services === 'checking' ? '🔄' : '❌'} {systemHealth.ai_services}
            </span>
          </div>
          <div>
            <span style={{ color: getHealthStatusColor(systemHealth.ml_models) }}>
              ML Models: {systemHealth.ml_models === 'operational' ? '✅' : systemHealth.ml_models === 'checking' ? '🔄' : '❌'} {systemHealth.ml_models}
            </span>
          </div>
        </div>
        
        {backendAvailable ? (
          <div style={{ fontSize: "0.8rem", color: "#065f46", marginTop: "0.5rem" }}>
            🎉 Sistemul hibrid AI+ML funcționează complet cu modele reale!
          </div>
        ) : (
          <div style={{ fontSize: "0.8rem", color: "#856404", marginTop: "0.5rem" }}>
            💡 Pentru funcționalitate completă, pornește backend-ul cu: cd backend && python app.py
            <button 
              onClick={checkBackendAvailability}
              style={{ 
                marginLeft: "1rem", 
                padding: "0.2rem 0.5rem", 
                fontSize: "0.8rem",
                border: "1px solid #f59e0b",
                borderRadius: "0.3rem",
                background: "transparent",
                color: "#f59e0b",
                cursor: "pointer"
              }}
            >
              🔄 Reîncearcă
            </button>
          </div>
        )}
      </div>
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

      <form className="upload-form" onSubmit={handleSubmit}>
        <label>
          <span>Mod de analiză:</span>
          <select 
            value={analysisMode} 
            onChange={e => setAnalysisMode(e.target.value)}
            style={{ 
              padding: "0.7rem", 
              borderRadius: "0.7rem", 
              border: "1px solid #c7d2fe",
              background: "#f1f5f9",
              fontSize: "1rem"
            }}
          >
            {Object.entries(availableModes).map(([key, mode]) => (
              <option key={key} value={key}>
                {mode.name} - {mode.accuracy} acuratețe, {mode.speed} viteză
              </option>
            ))}
          </select>
          {availableModes[analysisMode] && (
            <div style={{ fontSize: "0.85rem", color: "#6b7280", marginTop: "0.5rem" }}>
              {availableModes[analysisMode].description}
              <br />
              Limbile suportate: {availableModes[analysisMode].languages.join(", ")}
            </div>
          )}
        </label>

        <label>
          <span>Tip conținut:</span>
          <select value={tip} onChange={e => setTip(e.target.value)}>
            <option value="text">Articol text (scris manual)</option>
            <option value="file">Articol text (fișier)</option>
            <option value="link">Link către articol</option>
            <option value="video">Video (AI Deep Fake Detection)</option>
          </select>
        </label>

        {tip === "text" && (
          <label>
            <span>Introdu textul articolului:</span>
            <textarea
              rows={7}
              value={text}
              onChange={e => setText(e.target.value)}
              placeholder="Scrie sau lipește aici articolul..."
              style={{ 
                resize: "vertical", 
                fontSize: "1rem", 
                padding: "0.7rem", 
                borderRadius: "0.7rem", 
                border: "1px solid #c7d2fe", 
                background: "#f1f5f9" 
              }}
            />
          </label>
        )}

        {tip === "file" && (
          <label>
            <span>Încarcă fișier text:</span>
            <input type="file" accept=".txt" onChange={e => setFile(e.target.files[0])} />
          </label>
        )}

        {tip === "link" && (
          <label>
            <span>Introdu linkul articolului:</span>
            <input
              type="url"
              value={link}
              onChange={e => setLink(e.target.value)}
              placeholder="https://exemplu.ro/articol"
            />
          </label>
        )}

        {tip === "video" && (
          <label>
            <span>Încarcă fișier video:</span>
            <input 
              type="file" 
              accept="video/*" 
              onChange={e => setFile(e.target.files[0])}
              style={{ marginBottom: "0.5rem" }}
            />
            {file && (
              <div style={{ 
                fontSize: "0.9rem", 
                color: "#6b7280", 
                background: "#f1f5f9",
                padding: "0.5rem",
                borderRadius: "0.5rem",
                marginTop: "0.5rem"
              }}>
                <strong>Fișier selectat:</strong> {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                <br />
                <strong>Tip:</strong> {file.type}
                <br />
                <em>🎬 Analiză AI pentru deepfake detection, manipulare video și verificare autenticitate</em>
              </div>
            )}
          </label>
        )}


        {(isLoading && uploadProgress > 0) && (
          <div style={{ margin: "1rem 0" }}>
            <div style={{ fontSize: "0.9rem", marginBottom: "0.5rem" }}>
              Se procesează... {uploadProgress.toFixed(0)}%
            </div>
            <div style={{
              width: "100%",
              height: "10px",
              backgroundColor: "#e5e7eb",
              borderRadius: "5px",
              overflow: "hidden"
            }}>
              <div style={{
                width: `${uploadProgress}%`,
                height: "100%",
                backgroundColor: "#4f46e5",
                transition: "width 0.3s ease",
                borderRadius: "5px"
              }}></div>
            </div>
          </div>
        )}

        <button 
          type="submit" 
          className="main-btn" 
          disabled={isLoading}
          style={{ opacity: isLoading ? 0.7 : 1 }}
        >
          {isLoading ? "Se analizează..." : "Trimite spre analiză"}
        </button>
      </form>
      {result && !result.error && (
        <div style={{
          marginTop: "2rem",
          background: "#e0e7ff",
          borderRadius: "1rem",
          padding: "1.5rem",
          border: `3px solid ${getVerdictColor(result.verdict)}`
        }}>
          <div style={{
            textAlign: "center",
            color: getVerdictColor(result.verdict),
            fontWeight: 600,
            fontSize: "1.4rem",
            marginBottom: "1rem"
          }}>
            {result.verdict === 'fake' ? '🚨 FAKE NEWS DETECTAT!' : 
             result.verdict === 'real' ? '✅ ARTICOL AUTENTIC' : 
             result.verdict === 'deepfake' ? '🎬 DEEPFAKE DETECTAT' :
             result.verdict === 'authentic' ? '✅ VIDEO AUTENTIC' :
             (result.verdict === 'inconclusive' || result.verdict === 'neconcludent') ? '⚠️ REZULTAT NECONCLUDENT' :
             '⚠️ REZULTAT NECONCLUDENT'}
          </div>

          {getConfidenceBar(result.confidence)}

          <div style={{ marginTop: "1rem", fontSize: "1rem" }}>
            <strong>Explicație:</strong>
            <div style={{ marginTop: "0.5rem", lineHeight: "1.5" }}>
              {formatExplanation(result.explanation)}
            </div>
          </div>


          {result.analysis_mode === 'hybrid' && (
            <div style={{ marginTop: "1rem", fontSize: "0.9rem" }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginTop: "1rem" }}>
                <div>
                  <strong>Nivel risc:</strong> {result.risk_level}
                </div>
                <div>
                  <strong>Consens AI-ML:</strong> {result.ai_ml_agreement ? "✅ Acord" : "⚠️ Dezacord"}
                </div>
                <div>
                  <strong>Puterea consensului:</strong> {result.consensus_strength}
                </div>
                <div>
                  <strong>Verdict AI:</strong> {result.individual_verdicts?.ai || 'N/A'}
                </div>
                <div>
                  <strong>Verdict ML:</strong> {result.individual_verdicts?.ml || 'N/A'}
                </div>
                <div>
                  <strong>Limba detectată:</strong> {result.detected_language}
                </div>
              </div>
            </div>
          )}


          {(result.analysis_mode === 'video_demo' || result.analysis_mode === 'video_ai') && result.video_metadata && (
            <div style={{ marginTop: "1.5rem" }}>
              <h4 style={{ color: "#6366f1", marginBottom: "1rem" }}>📹 Metadata Video</h4>
              <div style={{ 
                background: "#f8fafc", 
                borderRadius: "0.5rem", 
                padding: "1rem",
                display: "grid", 
                gridTemplateColumns: "1fr 1fr", 
                gap: "0.5rem",
                fontSize: "0.9rem" 
              }}>
                <div><strong>Fișier:</strong> {result.video_metadata.filename}</div>
                <div><strong>Mărime:</strong> {result.video_metadata.size_mb} MB</div>
                <div><strong>Tip:</strong> {result.video_metadata.type}</div>
                <div><strong>Durată estimată:</strong> {result.video_metadata.estimated_duration}</div>
                <div><strong>Rezoluție:</strong> {result.video_metadata.estimated_resolution}</div>
                <div><strong>FPS:</strong> {result.video_metadata.estimated_fps}</div>
                <div><strong>Codec:</strong> {result.video_metadata.detected_codec}</div>
                <div><strong>Calitate:</strong> {result.detection_details?.quality_score ? (result.detection_details.quality_score * 100).toFixed(1) + '%' : 'N/A'}</div>
              </div>
              
              {result.detection_details && (
                <div style={{ marginTop: "1rem" }}>
                  <h5 style={{ color: "#6366f1", marginBottom: "0.5rem" }}>🔍 Detalii Analiză</h5>
                  <div style={{ 
                    background: "#f1f5f9", 
                    borderRadius: "0.5rem", 
                    padding: "1rem",
                    fontSize: "0.9rem" 
                  }}>
                    <div style={{ marginBottom: "0.5rem" }}>
                      <strong>Frame-uri analizate:</strong> {result.detection_details.total_frames_analyzed}
                    </div>
                    <div style={{ marginBottom: "0.5rem" }}>
                      <strong>Frame-uri suspecte:</strong> {result.detection_details.suspicious_frames}
                    </div>
                    <div style={{ marginBottom: "0.5rem" }}>
                      <strong>Metode folosite:</strong> {result.detection_details.methods_used.join(', ')}
                    </div>
                  </div>
                </div>
              )}
              
              {result.recommendations && (
                <div style={{ marginTop: "1rem" }}>
                  <h5 style={{ color: "#6366f1", marginBottom: "0.5rem" }}>💡 Recomandări</h5>
                  <ul style={{ 
                    background: "#fef3c7", 
                    borderRadius: "0.5rem", 
                    padding: "1rem",
                    marginLeft: "0",
                    fontSize: "0.9rem" 
                  }}>
                    {result.recommendations.map((rec, idx) => (
                      <li key={idx} style={{ marginBottom: "0.3rem" }}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          <div style={{ 
            marginTop: "1rem", 
            fontSize: "0.85rem", 
            color: "#6b7280",
            borderTop: "1px solid #c7d2fe",
            paddingTop: "0.5rem"
          }}>
            Mod analiză: {result.analysis_mode} | 
            Timp procesare: {result.processing_time?.toFixed(2)}s | 
            Limba: {result.detected_language}
          </div>
        </div>
              )}
      {result && result.error && (
        <div style={{
          marginTop: "2rem",
          background: "#fef2f2",
          borderRadius: "1rem",
          padding: "1.2rem",
          textAlign: "center",
          color: "#e11d48",
          fontWeight: 600,
          fontSize: "1.2rem",
          border: "2px solid #fca5a5"
        }}>
          ❌ {result.error}
        </div>
      )}
    </div>
  );
}