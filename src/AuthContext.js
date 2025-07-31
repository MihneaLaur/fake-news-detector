/**
 * Context pentru gestionarea autentificarii utilizatorilor.
 * Gestioneaza login, logout, register si sincronizarea cu backend-ul.
 */

import React, { createContext, useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { migrateUserAnalyses } from "./utils/userDataMigration";

const AuthContext = createContext();

/**
 * Provider pentru context-ul de autentificare.
 * @param {Object} props - Props cu children
 * @returns {JSX.Element} Provider cu functiile de autentificare
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("loggedUser");
    return saved ? JSON.parse(saved) : null;
  });

  /**
   * Verifica autentificarea cu backend-ul.
   * @param {boolean} showNotifications - Daca sa arate notificarile
   * @returns {Promise<Object>} Status-ul autentificarii si datele utilizatorului
   */
  const checkAuth = async (showNotifications = false) => {
    try {
      const response = await fetch('http://localhost:5000/check-auth', {
        method: 'GET',
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.authenticated) {
          // Sincronizează utilizatorul din backend cu localStorage
          const userObj = { 
            username: data.username, 
            role: data.is_admin ? "admin" : "user" 
          };
          
          // Verifică dacă utilizatorul din backend diferă de cel din localStorage
          const localUser = JSON.parse(localStorage.getItem("loggedUser") || "null");
          if (!localUser || localUser.username !== data.username) {
            console.log(`🔄 Sincronizare utilizator: ${localUser?.username || 'null'} -> ${data.username}`);
            setUser(userObj);
            localStorage.setItem("loggedUser", JSON.stringify(userObj));
          }
          
          return { authenticated: true, user: userObj };
        }
      }
      
      // Utilizatorul nu este autentificat în backend
      if (user) {
        console.log('🚪 Utilizator deautentificat din backend, curăț localStorage');
        setUser(null);
        localStorage.removeItem("loggedUser");
        
        // Afișează notificare și redirectează doar dacă este solicitat
        if (showNotifications) {
          // Folosim window.location pentru a evita hook-ul useNavigate în context
          setTimeout(() => {
            window.location.href = '/login';
          }, 2000);
        }
      }
      
      return { authenticated: false, user: null };
    } catch (error) {
      console.error('❌ Eroare la verificarea autentificării:', error);
      return { authenticated: false, user: null };
    }
  };

  /**
   * Functie pentru deconectare fortata cu notificare.
   * @param {string} reason - Motivul deconectarii
   */
  const forceLogout = (reason = "Sesiunea a expirat") => {
    console.log(`🚪 Deconectare forțată: ${reason}`);
    setUser(null);
    localStorage.removeItem("loggedUser");
    
    // Redirectează la login după o scurtă întârziere
    setTimeout(() => {
      window.location.href = '/login';
    }, 2000);
  };

  /**
   * Login cu backend Flask.
   * @param {string} username - Numele de utilizator
   * @param {string} password - Parola utilizatorului
   * @returns {Promise<Object>} Rezultatul operatiunii de login
   */
  const login = async (username, password) => {
    const response = await fetch('http://localhost:5000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
      credentials: "include"
    });
    const data = await response.json();
    if (!data.error) {
      const userObj = { username: data.username, role: data.is_admin ? "admin" : "user" };
      setUser(userObj);
      localStorage.setItem("loggedUser", JSON.stringify(userObj));
      
      // Migrează analizele utilizatorului la noul format
      setTimeout(() => {
        migrateUserAnalyses(data.username);
      }, 100);
      
      return { success: true, role: userObj.role };
    }
    return { success: false, message: data.error };
  };

  /**
   * Register cu backend Flask.
   * @param {string} username - Numele de utilizator
   * @param {string} password - Parola utilizatorului
   * @param {string} role - Rolul utilizatorului (user/admin)
   * @returns {Promise<Object>} Rezultatul operatiunii de register
   */
  const register = async (username, password, role) => {
    const response = await fetch('http://localhost:5000/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, is_admin: role === "admin" }),
      credentials: "include"
    });
    const data = await response.json();
    if (!data.error) {
      // NU setează user-ul automat la register!
      
      // Doar inițializează localStorage pentru utilizatorul nou
      setTimeout(() => {
        const userAnalysesKey = `analize_${username}`;
        if (!localStorage.getItem(userAnalysesKey)) {
          localStorage.setItem(userAnalysesKey, "[]");
          console.log(`🆕 Inițializat localStorage pentru utilizatorul nou: ${username}`);
        }
      }, 100);
      
      return { success: true, message: "Contul a fost creat cu succes! Te poți conecta acum." };
    }
    return { success: false, message: data.error };
  };

  /**
   * Logout din sistem.
   * @returns {Promise<void>} Promise pentru operatiunea de logout
   */
  const logout = async () => {
    await fetch('http://localhost:5000/logout', {
      method: 'POST',
      credentials: "include"
    });
    setUser(null);
    // Curăță doar datele de autentificare, NU analizele (acestea rămân pentru fiecare utilizator)
    localStorage.removeItem("loggedUser");
    // NU șterge "analize" - acestea sunt păstrate pentru fiecare utilizator separat
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, checkAuth, forceLogout }}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook pentru utilizarea context-ului de autentificare.
 * @returns {Object} Functiile si starea de autentificare
 */
export function useAuth() {
  return useContext(AuthContext);
}