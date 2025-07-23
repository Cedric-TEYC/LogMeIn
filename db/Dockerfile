FROM postgres:15

# Variables d'environnement par défaut
ENV POSTGRES_DB=logs_db
ENV POSTGRES_USER=logs_user
ENV POSTGRES_PASSWORD=logs_password

# Pour persister les données (volume Docker)
VOLUME ["/var/lib/postgresql/data"]

# Expose le port par défaut de PostgreSQL
EXPOSE 5432
