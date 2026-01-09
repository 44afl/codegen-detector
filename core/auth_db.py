import sqlite3
import hashlib
import secrets
import datetime
from contextlib import contextmanager

class AuthDB:
    def __init__(self, db_path='auth.db'):
        self.db_path = db_path
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    email_verified BOOLEAN DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    plan_type TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_date TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, password_hash):
        return self.hash_password(password) == password_hash
    
    def create_user(self, email, password, full_name=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            password_hash = self.hash_password(password)
            
            cursor.execute(
                'INSERT INTO users (email, password_hash, full_name) VALUES (?, ?, ?)',
                (email, password_hash, full_name)
            )
            return cursor.lastrowid
    
    def get_user_by_email(self, email):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_by_id(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def create_session(self, user_id, expiry_hours=24):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.datetime.now() + datetime.timedelta(hours=expiry_hours)
            
            cursor.execute(
                'INSERT INTO sessions (user_id, session_token, expires_at) VALUES (?, ?, ?)',
                (user_id, session_token, expires_at)
            )
            return session_token
    
    def get_session(self, session_token):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM sessions WHERE session_token = ? AND expires_at > ?',
                (session_token, datetime.datetime.now())
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def delete_session(self, session_token):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
    
    def create_password_reset_token(self, user_id, expiry_hours=1):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            token = secrets.token_urlsafe(32)
            expires_at = datetime.datetime.now() + datetime.timedelta(hours=expiry_hours)
            
            cursor.execute(
                'INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)',
                (user_id, token, expires_at)
            )
            return token
    
    def get_password_reset_token(self, token):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM password_reset_tokens WHERE token = ? AND expires_at > ? AND used = 0',
                (token, datetime.datetime.now())
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def mark_token_used(self, token):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE password_reset_tokens SET used = 1 WHERE token = ?', (token,))
    
    def update_password(self, user_id, new_password):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            password_hash = self.hash_password(new_password)
            cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
    
    def create_subscription(self, user_id, plan_type, duration_days=30):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            end_date = datetime.datetime.now() + datetime.timedelta(days=duration_days)
            
            cursor.execute(
                'INSERT INTO subscriptions (user_id, plan_type, end_date) VALUES (?, ?, ?)',
                (user_id, plan_type, end_date)
            )
            return cursor.lastrowid
    
    def get_user_subscription(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM subscriptions WHERE user_id = ? AND status = "active" ORDER BY end_date DESC LIMIT 1',
                (user_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_subscription_status(self, subscription_id, status):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE subscriptions SET status = ? WHERE id = ?', (status, subscription_id))
