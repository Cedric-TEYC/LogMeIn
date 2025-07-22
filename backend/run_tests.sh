# Run this script to run the tests
# You need to have the database running

export DB_HOST=localhost
export DB_NAME=logs_db
export DB_USER=logs_user
export DB_PASSWORD=logs_password
export DB_PORT=5432

python -m pytest tests/test_api.py -v
