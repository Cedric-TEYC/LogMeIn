import os
from datetime import datetime

import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration de la base de données
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'database': os.getenv('DB_NAME', 'logs_db'),
    'user': os.getenv('DB_USER', 'logs_user'),
    'password': os.getenv('DB_PASSWORD', 'logs_password'),
    'port': os.getenv('DB_PORT', 5432)
}

def get_db_connection():
    """Créer une connexion à la base de données"""
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """Initialiser la base de données et créer la table logs"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Créer la table logs si elle n'existe pas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ DEFAULT NOW(),
                level VARCHAR(10) NOT NULL,
                message TEXT NOT NULL,
                service VARCHAR(100) DEFAULT 'unknown',
                data JSONB DEFAULT '{}'
            )
        ''')
        
        # Créer un index sur timestamp pour améliorer les performances
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp DESC)
        ''')
        
        # Créer un index sur level pour le filtrage
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level)
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Base de données initialisée avec succès")
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la DB: {e}")

# Initialiser la DB au démarrage
init_db()

@app.route('/health', methods=['GET'])
def health():
    """Point de santé simple"""
    try:
        # Vérifier la connexion à la DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        conn.close()
        return jsonify({'status': 'ok', 'database': 'connected', 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        return jsonify({'status': 'error', 'database': 'disconnected', 'error': str(e)}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    """Récupère la liste des logs"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Paramètres de pagination
        limit = min(request.args.get('limit', 100, type=int), 1000)
        offset = request.args.get('offset', 0, type=int)
        
        # Récupérer les logs triés par timestamp décroissant
        cursor.execute('''
            SELECT id, timestamp, level, message, service, data
            FROM logs 
            ORDER BY timestamp DESC 
            LIMIT %s OFFSET %s
        ''', (limit, offset))
        
        logs = cursor.fetchall()
        
        # Convertir en liste de dictionnaires avec formatage
        logs_list = []
        for log in logs:
            logs_list.append({
                'id': log['id'],
                'timestamp': log['timestamp'].isoformat(),
                'level': log['level'],
                'message': log['message'],
                'service': log['service'],
                'data': log['data']
            })
        
        # Compter le total
        cursor.execute('SELECT COUNT(*) FROM logs')
        total = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'logs': logs_list,
            'total': total,
            'returned': len(logs_list),
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logs', methods=['POST'])
def add_log():
    """Ajoute un nouveau log"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Insérer le nouveau log
        cursor.execute('''
            INSERT INTO logs (level, message, service, data)
            VALUES (%s, %s, %s, %s)
            RETURNING id, timestamp, level, message, service, data
        ''', (
            data.get('level', 'info'),
            data.get('message', ''),
            data.get('service', 'unknown'),
            psycopg2.extras.Json(data.get('data', {}))
        ))
        
        log_entry = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        # Formatage de la réponse
        response_log = {
            'id': log_entry['id'],
            'timestamp': log_entry['timestamp'].isoformat(),
            'level': log_entry['level'],
            'message': log_entry['message'],
            'service': log_entry['service'],
            'data': log_entry['data']
        }
        
        return jsonify({
            'success': True,
            'log': response_log
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Statistiques simples sur les logs"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Compter le total
        cursor.execute('SELECT COUNT(*) as total FROM logs')
        total = cursor.fetchone()['total']
        
        if total == 0:
            return jsonify({
                'total_logs': 0,
                'levels': {},
                'services': {},
                'last_log': None
            })
        
        # Compter par niveau
        cursor.execute('''
            SELECT level, COUNT(*) as count 
            FROM logs 
            GROUP BY level
        ''')
        levels = {row['level']: row['count'] for row in cursor.fetchall()}
        
        # Compter par service
        cursor.execute('''
            SELECT service, COUNT(*) as count 
            FROM logs 
            GROUP BY service 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        services = {row['service']: row['count'] for row in cursor.fetchall()}
        
        # Dernier log
        cursor.execute('''
            SELECT id, timestamp, level, message, service, data
            FROM logs 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''')
        last_log_row = cursor.fetchone()
        
        last_log = None
        if last_log_row:
            last_log = {
                'id': last_log_row['id'],
                'timestamp': last_log_row['timestamp'].isoformat(),
                'level': last_log_row['level'],
                'message': last_log_row['message'],
                'service': last_log_row['service'],
                'data': last_log_row['data']
            }
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_logs': total,
            'levels': levels,
            'services': services,
            'last_log': last_log
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logs/clear', methods=['DELETE'])
def clear_logs():
    """Vide tous les logs (utilisation avec précaution)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM logs')
        deleted_count = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'{deleted_count} logs cleared'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
