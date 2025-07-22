// Configuration
const API_BASE_URL =
  window.location.hostname === "localhost" ? "http://localhost:5000" : "";

// État global
let allLogs = [];
let filteredLogs = [];
let currentFilters = {
  level: "",
  service: "",
  search: "",
};

// Éléments du DOM
const elements = {
  totalLogs: document.getElementById("total-logs"),
  errorCount: document.getElementById("error-count"),
  warningCount: document.getElementById("warning-count"),
  lastLog: document.getElementById("last-log"),
  levelFilter: document.getElementById("level-filter"),
  serviceFilter: document.getElementById("service-filter"),
  searchInput: document.getElementById("search-input"),
  logsList: document.getElementById("logs-list"),
  refreshBtn: document.getElementById("refresh-btn"),
  clearBtn: document.getElementById("clear-btn"),
  addTestBtn: document.getElementById("add-test-btn"),
  loadMoreBtn: document.getElementById("load-more-btn"),
};

// Utilitaires
const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleString("fr-FR");
};

const formatRelativeTime = (timestamp) => {
  const now = new Date();
  const logTime = new Date(timestamp);
  const diffMs = now - logTime;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return "À l'instant";
  if (diffMins < 60) return `${diffMins}min`;
  if (diffHours < 24) return `${diffHours}h`;
  return `${diffDays}j`;
};

// API
const api = {
  async getLogs(limit = 100) {
    const response = await fetch(`${API_BASE_URL}/logs?limit=${limit}`);
    if (!response.ok) throw new Error("Erreur lors du chargement des logs");
    return await response.json();
  },

  async getStats() {
    const response = await fetch(`${API_BASE_URL}/stats`);
    if (!response.ok) throw new Error("Erreur lors du chargement des stats");
    return await response.json();
  },

  async addLog(logData) {
    const response = await fetch(`${API_BASE_URL}/logs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(logData),
    });
    if (!response.ok) throw new Error("Erreur lors de l'ajout du log");
    return await response.json();
  },

  async clearLogs() {
    const response = await fetch(`${API_BASE_URL}/logs/clear`, {
      method: "DELETE",
    });
    if (!response.ok) throw new Error("Erreur lors de la suppression des logs");
    return await response.json();
  },
};

// Interface utilisateur
const updateStats = (stats) => {
  elements.totalLogs.textContent = stats.total_logs || 0;
  elements.errorCount.textContent = stats.levels.error || 0;
  elements.warningCount.textContent = stats.levels.warning || 0;

  if (stats.last_log) {
    elements.lastLog.textContent = formatRelativeTime(stats.last_log.timestamp);
  } else {
    elements.lastLog.textContent = "Aucun";
  }
};

const updateServiceFilter = (logs) => {
  const services = [...new Set(logs.map((log) => log.service))];

  // Vider et repeupler le filtre des services
  elements.serviceFilter.innerHTML =
    '<option value="">Tous les services</option>';
  services.forEach((service) => {
    const option = document.createElement("option");
    option.value = service;
    option.textContent = service;
    elements.serviceFilter.appendChild(option);
  });
};

const createLogElement = (log) => {
  const logDiv = document.createElement("div");
  logDiv.className = "log-entry";

  const data =
    log.data && Object.keys(log.data).length > 0
      ? JSON.stringify(log.data, null, 2)
      : null;

  logDiv.innerHTML = `
        <div class="log-header">
            <span class="log-level ${log.level}">${log.level}</span>
            <div class="log-meta">
                <span>📅 ${formatTimestamp(log.timestamp)}</span>
                <span>🏷️ ${log.service}</span>
                <span>⏱️ ${formatRelativeTime(log.timestamp)}</span>
            </div>
        </div>
        <div class="log-message">${log.message}</div>
        ${data ? `<div class="log-data">${data}</div>` : ""}
    `;

  return logDiv;
};

const applyFilters = () => {
  filteredLogs = allLogs.filter((log) => {
    const matchesLevel =
      !currentFilters.level || log.level === currentFilters.level;
    const matchesService =
      !currentFilters.service || log.service === currentFilters.service;
    const matchesSearch =
      !currentFilters.search ||
      log.message.toLowerCase().includes(currentFilters.search.toLowerCase());

    return matchesLevel && matchesService && matchesSearch;
  });

  renderLogs();
};

const renderLogs = () => {
  if (filteredLogs.length === 0) {
    elements.logsList.innerHTML = `
            <div class="empty-state">
                <h3>Aucun log trouvé</h3>
                <p>Aucun log ne correspond aux filtres actuels.</p>
            </div>
        `;
    return;
  }

  elements.logsList.innerHTML = "";
  filteredLogs.forEach((log) => {
    elements.logsList.appendChild(createLogElement(log));
  });

  // Afficher/masquer le bouton "Charger plus"
  elements.loadMoreBtn.style.display =
    filteredLogs.length >= 100 ? "block" : "none";
};

const showLoading = () => {
  elements.logsList.innerHTML = '<div class="loading">⏳ Chargement...</div>';
};

const showError = (message) => {
  elements.logsList.innerHTML = `<div class="error-message">❌ ${message}</div>`;
};

// Fonctions principales
const loadDashboard = async () => {
  try {
    showLoading();

    // Charger logs et stats en parallèle
    const [logsData, statsData] = await Promise.all([
      api.getLogs(),
      api.getStats(),
    ]);

    allLogs = logsData.logs;
    updateStats(statsData);
    updateServiceFilter(allLogs);
    applyFilters();
  } catch (error) {
    console.error("Erreur:", error);
    showError(error.message);
  }
};

const addTestLog = async () => {
  const levels = ["info", "warning", "error", "debug"];
  const services = ["api", "frontend", "database", "auth", "worker"];
  const messages = [
    "Utilisateur connecté avec succès",
    "Erreur de connexion à la base de données",
    "Traitement terminé",
    "Limite de débit atteinte",
    "Sauvegarde automatique effectuée",
    "Erreur de validation des données",
  ];

  const testLog = {
    level: levels[Math.floor(Math.random() * levels.length)],
    service: services[Math.floor(Math.random() * services.length)],
    message: messages[Math.floor(Math.random() * messages.length)],
    data: {
      user_id: Math.floor(Math.random() * 1000),
      ip: `192.168.1.${Math.floor(Math.random() * 255)}`,
      duration_ms: Math.floor(Math.random() * 1000),
    },
  };

  try {
    elements.addTestBtn.textContent = "⏳ Ajout...";
    elements.addTestBtn.disabled = true;

    await api.addLog(testLog);
    await loadDashboard();
  } catch (error) {
    console.error("Erreur lors de l'ajout:", error);
    alert("Erreur lors de l'ajout du log test");
  } finally {
    elements.addTestBtn.textContent = "➕ Test Log";
    elements.addTestBtn.disabled = false;
  }
};

const clearAllLogs = async () => {
  if (!confirm("Êtes-vous sûr de vouloir supprimer tous les logs ?")) {
    return;
  }

  try {
    elements.clearBtn.textContent = "⏳ Suppression...";
    elements.clearBtn.disabled = true;

    await api.clearLogs();
    await loadDashboard();
  } catch (error) {
    console.error("Erreur lors de la suppression:", error);
    alert("Erreur lors de la suppression des logs");
  } finally {
    elements.clearBtn.textContent = "🗑️ Vider";
    elements.clearBtn.disabled = false;
  }
};

// Event listeners
elements.refreshBtn.addEventListener("click", loadDashboard);
elements.clearBtn.addEventListener("click", clearAllLogs);
elements.addTestBtn.addEventListener("click", addTestLog);

elements.levelFilter.addEventListener("change", (e) => {
  currentFilters.level = e.target.value;
  applyFilters();
});

elements.serviceFilter.addEventListener("change", (e) => {
  currentFilters.service = e.target.value;
  applyFilters();
});

elements.searchInput.addEventListener("input", (e) => {
  currentFilters.search = e.target.value;
  applyFilters();
});

elements.loadMoreBtn.addEventListener("click", async () => {
  try {
    elements.loadMoreBtn.textContent = "⏳ Chargement...";
    const moreData = await api.getLogs(allLogs.length + 100);
    allLogs = moreData.logs;
    applyFilters();
  } catch (error) {
    console.error("Erreur:", error);
  } finally {
    elements.loadMoreBtn.textContent = "Charger plus";
  }
});

// Auto-refresh (toutes les 30 secondes)
setInterval(() => {
  loadDashboard();
}, 30000);

// Chargement initial
loadDashboard();
