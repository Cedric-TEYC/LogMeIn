# Log Me In Application

## 🚀 Features

- **API** for adding logs
- **Web dashboard** for visualizing logs
- **PostgreSQL** for data persistence
- **Filters** by level, service and text search
- **Statistics** in real time
- **Auto-refresh** every 30 seconds

## 📁 Structure

```
app/
├── backend/
│   ├── app.py              # Flask API with PostgreSQL
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # TODO: create Dockerfile for the backend
├── frontend/
│   ├── index.html          # Web interface
│   ├── style.css           # Styles
│   ├── script.js           # Frontend logic
│   └── Dockerfile          # Dockerfile for the frontend is already created
├── docker-compose.yml      # TODO: create docker-compose file
└── README.md
```

## ✅ TODOs

- Create Dockerfile for the backend.

The backend app needs to be containerized. It expects those environment variables:

```
DB_HOST=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_PORT=
```

- create a docker-compose file to deploy the app (frontend + backend) with a PostgreSQL container.

## Local development

**PostgreSQL :**

```bash
# Start PostgreSQL locally
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
export DB_PORT=5432
python app.py
```

In order to run the tests (make sure the database is running):

```bash
pip install -r requirements.dev.txt
sh run_tests.sh
```

**Frontend :**

```bash
cd frontend
# Serve with a simple web server
python -m http.server 8000
```
