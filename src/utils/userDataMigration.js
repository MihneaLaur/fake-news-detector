/**
 * Utilitar pentru migrarea datelor utilizatorilor din localStorage global
 * la localStorage specific pentru fiecare utilizator
 */

export const migrateUserAnalyses = (username) => {
  if (!username || username === "guest") return;
  
  const userAnalysesKey = `analize_${username}`;
  const existingUserAnalyses = JSON.parse(localStorage.getItem(userAnalysesKey) || "[]");
  
  // Dacă utilizatorul are deja analize în noul format, nu face nimic
  if (existingUserAnalyses.length > 0) {
    console.log(`✅ Utilizatorul ${username} are deja ${existingUserAnalyses.length} analize în noul format`);
    return existingUserAnalyses.length;
  }
  
  // Încarcă toate analizele din localStorage-ul global
  const allAnalyses = JSON.parse(localStorage.getItem("analize") || "[]");
  
  // Filtrează analizele pentru utilizatorul curent
  const userAnalyses = allAnalyses.filter(analysis => analysis.username === username);
  
  if (userAnalyses.length > 0) {
    // Salvează în noul format
    localStorage.setItem(userAnalysesKey, JSON.stringify(userAnalyses));
    console.log(`🔄 Migrat ${userAnalyses.length} analize pentru ${username} la noul format`);
    return userAnalyses.length;
  }
  
  return 0;
};

export const getUserAnalyses = (username) => {
  if (!username) return [];
  
  const userAnalysesKey = `analize_${username}`;
  return JSON.parse(localStorage.getItem(userAnalysesKey) || "[]");
};

export const addUserAnalysis = (username, analysis) => {
  if (!username || !analysis) return false;
  
  const userAnalysesKey = `analize_${username}`;
  const userAnalyses = JSON.parse(localStorage.getItem(userAnalysesKey) || "[]");
  
  // Adaugă analiza cu username-ul corect
  const analysisWithUser = {
    ...analysis,
    username: username
  };
  
  userAnalyses.push(analysisWithUser);
  localStorage.setItem(userAnalysesKey, JSON.stringify(userAnalyses));
  
  // Păstrează și în formatul vechi pentru compatibilitate cu backend-ul
  const allAnalyses = JSON.parse(localStorage.getItem("analize") || "[]");
  allAnalyses.push(analysisWithUser);
  localStorage.setItem("analize", JSON.stringify(allAnalyses));
  
  return true;
};

export const clearUserAnalyses = (username) => {
  if (!username) return false;
  
  const userAnalysesKey = `analize_${username}`;
  localStorage.removeItem(userAnalysesKey);
  
  // Șterge și din localStorage-ul global
  const allAnalyses = JSON.parse(localStorage.getItem("analize") || "[]");
  const filteredAnalyses = allAnalyses.filter(analysis => analysis.username !== username);
  localStorage.setItem("analize", JSON.stringify(filteredAnalyses));
  
  console.log(`🗑️ Șterse toate analizele pentru ${username}`);
  return true;
};

export const getAllUsersFromAnalyses = () => {
  const allAnalyses = JSON.parse(localStorage.getItem("analize") || "[]");
  const users = [...new Set(allAnalyses.map(analysis => analysis.username))];
  return users.filter(user => user && user !== "guest");
};

export const getAnalysesStats = () => {
  const allAnalyses = JSON.parse(localStorage.getItem("analize") || "[]");
  const userStats = {};
  
  allAnalyses.forEach(analysis => {
    const username = analysis.username || "unknown";
    if (!userStats[username]) {
      userStats[username] = {
        total: 0,
        fake: 0,
        real: 0,
        deepfake: 0,
        authentic: 0
      };
    }
    
    userStats[username].total++;
    
    switch (analysis.rezultat) {
      case 'fake':
        userStats[username].fake++;
        break;
      case 'real':
        userStats[username].real++;
        break;
      case 'deepfake':
        userStats[username].deepfake++;
        break;
      case 'authentic':
        userStats[username].authentic++;
        break;
    }
  });
  
  return userStats;
};

export const cleanupOrphanedAnalyses = () => {
  const allAnalyses = JSON.parse(localStorage.getItem("analize") || "[]");
  const validAnalyses = allAnalyses.filter(analysis => 
    analysis.username && 
    analysis.username !== "guest" && 
    analysis.username !== "unknown" &&
    analysis.username.trim() !== ""
  );
  
  const removedCount = allAnalyses.length - validAnalyses.length;
  
  if (removedCount > 0) {
    localStorage.setItem("analize", JSON.stringify(validAnalyses));
    console.log(`🧹 Curățare completă: șters ${removedCount} analize orfane`);
  }
  
  return {
    removed: removedCount,
    remaining: validAnalyses.length,
    total: allAnalyses.length
  };
};

export const migrateAllUsersToNewFormat = () => {
  const users = getAllUsersFromAnalyses();
  let totalMigrated = 0;
  
  users.forEach(username => {
    const migrated = migrateUserAnalyses(username);
    totalMigrated += migrated;
  });
  
  console.log(`🔄 Migrare completă: ${totalMigrated} analize pentru ${users.length} utilizatori`);
  
  return {
    users: users.length,
    analyses: totalMigrated
  };
}; 