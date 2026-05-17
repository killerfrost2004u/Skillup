import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

# ============================================
# 1. ADAPTER PATTERN (Unified DB Interface)
# ============================================
class DatabaseAdapter(ABC):
    @abstractmethod
    def get_connection(self):
        pass

    @abstractmethod
    def format_query(self, query):
        pass

    @abstractmethod
    def get_cursor(self, conn):
        pass

class SQLiteAdapter(DatabaseAdapter):
    def __init__(self, db_path):
        self.db_path = db_path

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def format_query(self, query):
        # SQLite uses '?' instead of '%s'
        return query.replace('%s', '?')

    def get_cursor(self, conn):
        return conn.cursor()

    def fetch_row_as_dict(self, row):
        return dict(row) if row else None

class PostgresAdapter(DatabaseAdapter):
    def __init__(self, database_url):
        self.database_url = database_url

    def get_connection(self):
        return psycopg2.connect(self.database_url)

    def format_query(self, query):
        return query

    def get_cursor(self, conn):
        return conn.cursor(cursor_factory=RealDictCursor)

    def fetch_row_as_dict(self, row):
        return row # Already a dict due to RealDictCursor

# ============================================
# 2. SINGLETON & FACTORY PATTERN (DB Manager)
# ============================================
class DatabaseManager:
    _instance = None
    _adapter = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize_adapter()
        return cls._instance

    def _initialize_adapter(self):
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            logger.info("🔌 Using Postgres Adapter")
            self._adapter = PostgresAdapter(db_url)
        else:
            logger.info("🔌 Using SQLite Adapter")
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sqlite_db_path = os.path.join(base_dir, 'skill_up.db')
            self._adapter = SQLiteAdapter(sqlite_db_path)

    def execute_query(self, query, params=(), fetch_one=False, fetch_all=False):
        conn = self._adapter.get_connection()
        if not conn:
            return None

        try:
            formatted_query = self._adapter.format_query(query)
            cursor = self._adapter.get_cursor(conn)
            cursor.execute(formatted_query, params)
            
            if fetch_one:
                row = cursor.fetchone()
                if isinstance(self._adapter, SQLiteAdapter):
                    return self._adapter.fetch_row_as_dict(row)
                return row
            elif fetch_all:
                rows = cursor.fetchall()
                if isinstance(self._adapter, SQLiteAdapter):
                    return [self._adapter.fetch_row_as_dict(r) for r in rows]
                return rows
            else:
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"❌ DB Manager Error: {e}")
            return None
        finally:
            conn.close()

# Global access point for the Singleton
db_manager = DatabaseManager()
