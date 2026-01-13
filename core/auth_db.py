import sqlite3
import hashlib
import secrets
import datetime
import time
import re
from functools import wraps
from contextlib import contextmanager

from aop.aspects import log_call, timeit, debug


class TTLCache:
    """Small TTL cache for SELECT results."""

    def __init__(self, ttl=15):
        self.ttl = ttl
        self.store = {}

    def get(self, key):
        now = time.time()
        if key not in self.store:
            return None
        value, expires_at = self.store[key]
        if now > expires_at:
            self.store.pop(key, None)
            return None
        return value

    def set(self, key, value):
        expires_at = time.time() + self.ttl
        self.store[key] = (value, expires_at)

    def clear(self):
        self.store.clear()


def analyze_sql(func):
    """Basic SQL injection patterns blocker."""

    patterns = [
        r"--",
        r"#",
        r";",
        r"OR\s+1=1",
        r"UNION\s+SELECT",
        r"DROP\s+TABLE",
        r"DELETE\s+FROM",
    ]

    @wraps(func)
    def wrapper(self, query, params=None, *args, **kwargs):
        sql = query or ""
        for pattern in patterns:
            if re.search(pattern, sql, flags=re.IGNORECASE):
                raise ValueError(f"[SECURITY] SQL Injection attempt blocked: {query}")
        return func(self, query, params=params, *args, **kwargs)

    return wrapper


def log_query(func):
    @wraps(func)
    def wrapper(self, query, params=None, *args, **kwargs):
        print(f"[DB] → Executing: {query} params={params or []}")
        start = time.time()
        result = func(self, query, params=params, *args, **kwargs)
        duration_ms = (time.time() - start) * 1000
        print(f"[DB] ← Done in {duration_ms:.2f} ms")
        if duration_ms > 250:
            print(f"[DB WARNING] Slow query ({duration_ms:.2f} ms): {query}")
        return result

    return wrapper


def cache_query(ttl=15):
    def decorator(func):
        @wraps(func)
        def wrapper(self, query, params=None, *args, **kwargs):
            sql = (query or "").strip().lower()
            if not sql.startswith("select"):
                return func(self, query, params=params, *args, **kwargs)

            cache_key = (query, tuple(params or []))
            cached = self.query_cache.get(cache_key)
            if cached is not None:
                print("[DB] Cache HIT")
                return cached

            result = func(self, query, params=params, *args, **kwargs)
            self.query_cache.set(cache_key, result)
            print("[DB] Cache MISS → stored")
            return result

        return wrapper

    return decorator

class AuthDB:
    def __init__(self, db_path='auth.db'):
        self.db_path = db_path
        self.query_cache = TTLCache(ttl=15)
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
    
    @log_call
    @timeit
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

    def _invalidate_cache(self):
        self.query_cache.clear()

    @cache_query(ttl=15)
    @analyze_sql
    @log_query
    def _select(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def _fetchone(self, query, params=None):
        rows = self._select(query, params)
        return rows[0] if rows else None

    @analyze_sql
    @log_query
    def _execute(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            return {"lastrowid": cursor.lastrowid, "rowcount": cursor.rowcount}
    
    @debug
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    @debug
    def verify_password(self, password, password_hash):
        return self.hash_password(password) == password_hash
    
    @log_call
    @timeit
    def create_user(self, email, password, full_name=None):
        password_hash = self.hash_password(password)
        result = self._execute(
            'INSERT INTO users (email, password_hash, full_name) VALUES (?, ?, ?)',
            (email, password_hash, full_name)
        )
        self._invalidate_cache()
        return result["lastrowid"]
    
    @log_call
    @timeit
    def get_user_by_email(self, email):
        return self._fetchone('SELECT * FROM users WHERE email = ?', (email,))
    
    @log_call
    @timeit
    def get_user_by_id(self, user_id):
        return self._fetchone('SELECT * FROM users WHERE id = ?', (user_id,))
    
    @log_call
    @timeit
    def create_session(self, user_id, expiry_hours=24):
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.datetime.now() + datetime.timedelta(hours=expiry_hours)
        self._execute(
            'INSERT INTO sessions (user_id, session_token, expires_at) VALUES (?, ?, ?)',
            (user_id, session_token, expires_at)
        )
        self._invalidate_cache()
        return session_token
    
    @log_call
    @timeit
    def get_session(self, session_token):
        return self._fetchone(
            'SELECT * FROM sessions WHERE session_token = ? AND expires_at > ?',
            (session_token, datetime.datetime.now())
        )
    
    @log_call
    @timeit
    def delete_session(self, session_token):
        self._execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
        self._invalidate_cache()
    
    @log_call
    @timeit
    def create_password_reset_token(self, user_id, expiry_hours=1):
        token = secrets.token_urlsafe(32)
        expires_at = datetime.datetime.now() + datetime.timedelta(hours=expiry_hours)
        self._execute(
            'INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)',
            (user_id, token, expires_at)
        )
        self._invalidate_cache()
        return token
    
    @log_call
    @timeit
    def get_password_reset_token(self, token):
        return self._fetchone(
            'SELECT * FROM password_reset_tokens WHERE token = ? AND expires_at > ? AND used = 0',
            (token, datetime.datetime.now())
        )
    
    @log_call
    @timeit
    def mark_token_used(self, token):
        self._execute('UPDATE password_reset_tokens SET used = 1 WHERE token = ?', (token,))
        self._invalidate_cache()
    
    @log_call
    @timeit
    def update_password(self, user_id, new_password):
        password_hash = self.hash_password(new_password)
        self._execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
        self._invalidate_cache()
    
    @log_call
    @timeit
    def create_subscription(self, user_id, plan_type, duration_days=30):
        end_date = datetime.datetime.now() + datetime.timedelta(days=duration_days)
        result = self._execute(
            'INSERT INTO subscriptions (user_id, plan_type, end_date) VALUES (?, ?, ?)',
            (user_id, plan_type, end_date)
        )
        self._invalidate_cache()
        return result["lastrowid"]
    
    @log_call
    @timeit
    def get_user_subscription(self, user_id):
        return self._fetchone(
            'SELECT * FROM subscriptions WHERE user_id = ? AND status = "active" ORDER BY end_date DESC LIMIT 1',
            (user_id,)
        )
    
    @log_call
    @timeit
    def update_subscription_status(self, subscription_id, status):
        self._execute('UPDATE subscriptions SET status = ? WHERE id = ?', (status, subscription_id))
        self._invalidate_cache()
