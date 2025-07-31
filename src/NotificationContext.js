/**
 * Context pentru gestionarea notificarilor in aplicatie.
 * Permite afisarea de notificari cu diferite tipuri si durate.
 */

import React, { createContext, useContext, useState } from "react";

const NotificationContext = createContext();

/**
 * Provider pentru context-ul de notificari.
 * @param {Object} props - Props cu children
 * @returns {JSX.Element} Provider cu functiile de notificare
 */
export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);

  /**
   * Adauga o notificare noua in sistem.
   * @param {string} message - Mesajul notificarii
   * @param {string} type - Tipul notificarii (info/success/error/warning)
   * @param {number} duration - Durata afisarii in milisecunde
   * @returns {number} ID-ul notificarii pentru management
   */
  const addNotification = (message, type = 'info', duration = 5000) => {
    const id = Date.now() + Math.random();
    const notification = { id, message, type, duration };
    
    setNotifications(prev => [...prev, notification]);
    
    // Auto-remove după duration
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }
    
    return id;
  };

  /**
   * Elimina o notificare din sistem.
   * @param {number} id - ID-ul notificarii de eliminat
   */
  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  /**
   * Afiseaza alerta de deconectare automata.
   */
  const showDisconnectionAlert = () => {
    addNotification(
      "🚪 Ai fost deconectat din sistem. Te redirectez la pagina de login...",
      'warning',
      3000
    );
  };

  /**
   * Afiseaza mesaj de reconectare reusita.
   */
  const showReconnectionSuccess = () => {
    addNotification(
      "✅ Reconectat cu succes!",
      'success',
      2000
    );
  };

  /**
   * Afiseaza o notificare de eroare.
   * @param {string} message - Mesajul de eroare
   */
  const showError = (message) => {
    addNotification(
      `❌ Eroare: ${message}`,
      'error',
      5000
    );
  };

  /**
   * Afiseaza o notificare de succes.
   * @param {string} message - Mesajul de succes
   */
  const showSuccess = (message) => {
    addNotification(
      `✅ ${message}`,
      'success',
      3000
    );
  };

  return (
    <NotificationContext.Provider value={{
      notifications,
      addNotification,
      removeNotification,
      showDisconnectionAlert,
      showReconnectionSuccess,
      showError,
      showSuccess
    }}>
      {children}
    </NotificationContext.Provider>
  );
}

/**
 * Hook pentru utilizarea context-ului de notificari.
 * @returns {Object} Functiile si starea de notificare
 * @throws {Error} Daca nu este utilizat in cadrul NotificationProvider
 */
export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
} 