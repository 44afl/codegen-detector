# core/db.py
import pymysql
import threading
import queue
import time
import re

from core.configuration import Configuration
from core.cache import CacheManager

class MySQLConnectionPool:
    def __init__(self, size=5):
        cfg = Configuration.instance()
        self.host = cfg.get("DB_HOST", "localhost")
        self.user = cfg.get("DB_USER", "root")
        self.password = cfg.get("DB_PASS", "")
        self.db = cfg.get("DB_NAME", "test")
        self.port = cfg.get("DB_PORT", 3306)

        self.pool = queue.Queue(maxsize=size)
        self.size = size

        # Pre-create connections
        for _ in range(size):
            conn = self._create_conn()
            self.pool.put(conn)

    def _create_conn(self):
        return pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.db,
            port=self.port,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )

    def get_conn(self):
        return self.pool.get()

    def release(self, conn):
        try:
            self.pool.put(conn)
        except:
            conn.close()

    def close_all(self):
        while not self.pool.empty():
            conn = self.pool.get()
            try:
                conn.close()
            except:
                pass

def analyze_sql(func):
    patterns = [
        r"--",
        r"#", 
        r";",
        r"OR\s+1=1",
        r"UNION\s+SELECT",
        r"DROP\s+TABLE",
        r"DELETE\s+FROM"
    ]

    def wrapper(self, query, *args, **kwargs):
        for p in patterns:
            if re.search(p, query, flags=re.IGNORECASE):
                raise ValueError(f"[SECURITY] SQL Injection attempt blocked: {query}")
        return func(self, query, *args, **kwargs)

    return wrapper


def log_query(func):
    """
    Logs execution + slow queries.
    """
    def wrapper(self, query, *args, **kwargs):
        cfg = Configuration.instance()
        log_enabled = cfg.get("DB_LOGGING", True)
        slow_ms = cfg.get("DB_SLOW_QUERY_THRESHOLD", 250)

        if log_enabled:
            print(f"[DB] → Executing: {query}")

        t0 = time.time()
        result = func(self, query, *args, **kwargs)
        dt = (time.time() - t0) * 1000

        if log_enabled:
            print(f"[DB] ← Done in {dt:.2f} ms")

        if dt > slow_ms:
            print(f"[DB WARNING] Slow query ({dt:.2f} ms): {query}")

        return result

    return wrapper


def cache_query(ttl=10):
    """
    Caches SELECT results transparently.
    """
    def decorator(func):
        def wrapper(self, query, *args, **kwargs):
            if not query.strip().lower().startswith("select"):
                return func(self, query, *args, **kwargs)

            cache = CacheManager.get_cache("mysql_cache", default_ttl=ttl)
            key = query + str(args) + str(kwargs)

            cached = cache.get(key)
            if cached is not None:
                print("[DB] Cache HIT")
                return cached

            result = func(self, query, *args, **kwargs)
            cache.set(key, result)
            print("[DB] Cache MISS → stored")
            return result

        return wrapper
    return decorator

class Database:
    def __init__(self, pool_size=5):
        self.pool = MySQLConnectionPool(size=pool_size)
        self.lock = threading.Lock()

    @cache_query(ttl=15)
    @analyze_sql
    @log_query
    def select(self, query, params=None):
        conn = self.pool.get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or [])
                result = cursor.fetchall()
                return result
        finally:
            self.pool.release(conn)

    @analyze_sql
    @log_query
    def execute(self, query, params=None):
        conn = self.pool.get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or [])
            return True
        finally:
            self.pool.release(conn)

    def close(self):
        self.pool.close_all()
