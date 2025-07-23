# Dashboard de Logs Simple

Un dashboard minimaliste pour afficher et gérer des logs en temps réel avec PostgreSQL.

## 🚀 Fonctionnalités

- **API simple** pour ajouter des logs
- **Dashboard web** pour visualiser les logs
- **Base PostgreSQL** pour persistence des données
- **Filtres** par niveau, service et recherche textuelle
- **Statistiques** en temps réel
- **Auto-refresh** toutes les 30 secondes

## 📁 Structure

```
simple-monitoring/
├── backend/
│   ├── app.py              # API Flask avec PostgreSQL
│   ├── requirements.txt    # Dépendances Python
│   └── Dockerfile
├── frontend/
│   ├── index.html          # Interface web
│   ├── style.css           # Styles
│   ├── script.js           # Logique frontend
│   └── Dockerfile
├── docker-compose.yml      # Configuration Docker avec PostgreSQL
└── README.md
```

## 🛠️ Installation et Démarrage

### Avec Docker (recommandé)

```bash
# Cloner le projet
git clone [repository]
cd simple-monitoring

# Démarrer les services (PostgreSQL + Backend + Frontend)
docker-compose up -d

# Vérifier que tous les services sont démarrés
docker-compose ps

# Accéder au dashboard
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
# PostgreSQL: localhost:5432
```

### Développement local

**PostgreSQL :**
```bash
# Démarrer PostgreSQL localement
docker run --name postgres-logs -e POSTGRES_DB=logs_db -e POSTGRES_USER=logs_user -e POSTGRES_PASSWORD=logs_password -p 5432:5432 -d postgres:15
```

**Backend :**
```bash
cd backend
pip install -r requirements.txt
export DB_HOST=localhost
export DB_NAME=logs_db
export DB_USER=logs_user
export DB_PASSWORD=logs_password
python app.py
```

**Frontend :**
```bash
cd frontend
# Servir avec un serveur web simple
python -m http.server 8000
```

## 📊 Base de Données

### Structure de la table `logs`

```sql
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    service VARCHAR(100) DEFAULT 'unknown',
    data JSONB DEFAULT '{}'
);
```

### Index pour performances

- `idx_logs_timestamp` sur `timestamp DESC`
- `idx_logs_level` sur `level`

## 📊 Utilisation

### Interface Web

1. **Dashboard** : Affiche les statistiques et la liste des logs
2. **Filtres** : Filtrer par niveau, service ou message
3. **Pagination** : Support des `limit` et `offset`
4. **Actions** :
   - 🔄 Actualiser : Recharge les données
   - 🗑️ Vider : Supprime tous les logs
   - ➕ Test Log : Ajoute un log de test

### API Endpoints

**Ajouter un log :**
```bash
POST /logs
Content-Type: application/json

{
  "level": "info",
  "message": "Message du log",
  "service": "mon-service",
  "data": {
    "user_id": 123,
    "action": "login"
  }
}
```

**Récupérer les logs :**
```bash
GET /logs?limit=100&offset=0
```

**Statistiques :**
```bash
GET /stats
```

**Vider les logs :**
```bash
DELETE /logs/clear
```

**Santé de l'API :**
```bash
GET /health
```

### Exemple d'utilisation avec curl

```bash
# Ajouter un log
curl -X POST http://localhost:5000/logs \
  -H "Content-Type: application/json" \
  -d '{
    "level": "error",
    "message": "Erreur de connexion à la base de données",
    "service": "api",
    "data": {"error_code": 500, "retries": 3}
  }'

# Récupérer les logs avec pagination
curl "http://localhost:5000/logs?limit=50&offset=0"

# Obtenir les statistiques
curl http://localhost:5000/stats
```

## 🔧 Configuration

### Variables d'environnement

- **DB_HOST** : Hôte PostgreSQL (défaut: `db`)
- **DB_NAME** : Nom de la base (défaut: `logs_db`)
- **DB_USER** : Utilisateur (défaut: `logs_user`)
- **DB_PASSWORD** : Mot de passe (défaut: `logs_password`)
- **DB_PORT** : Port (défaut: `5432`)

### Ports

- **Frontend** : 3000
- **Backend** : 5000
- **PostgreSQL** : 5432

## 📝 Format des Logs

```json
{
  "id": 123,
  "timestamp": "2024-01-20T10:00:00.123456+00:00",
  "level": "info|warning|error|debug",
  "message": "Description du log",
  "service": "nom-du-service",
  "data": {
    "clé": "valeur",
    "autres": "données"
  }
}
```

## 🗄️ Avantages de PostgreSQL

- **Persistence** : Les données survivent aux redémarrages
- **Performance** : Index pour requêtes rapides
- **JSONB** : Support natif des données JSON
- **Scalabilité** : Peut gérer millions de logs
- **Transactions** : Intégrité des données

## 🚀 Extensions possibles

- Partitioning par date pour les gros volumes
- Archivage automatique des anciens logs
- Réplication pour haute disponibilité
- Monitoring avec pg_stat_statements
- Backup automatique

## 🎯 Cas d'usage

- Monitoring d'applications en production
- Centralisation des logs microservices
- Debug et troubleshooting
- Audit de sécurité
- Analytics sur les événements
