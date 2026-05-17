import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')
IS_VERCEL = os.getenv('VERCEL') == '1' or os.getenv('VERCEL_ENV') is not None

def get_db_connection():
    """Get database connection (PostgreSQL for Vercel/Production, SQLite for Local)"""
    try:
        if DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sqlite_db_path = os.path.join(base_dir, 'skill_up.db')
            
            conn = sqlite3.connect(sqlite_db_path)
            conn.row_factory = sqlite3.Row
            return conn
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return None

def execute_query(query, params=(), fetch_one=False, fetch_all=False):
    """Execute SQL query and return results (unified interface for SQLite/Postgres)"""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        is_sqlite = isinstance(conn, sqlite3.Connection)
        if is_sqlite:
            # Simple Adapter logic: SQLite uses ? for placeholders instead of %s
            query = query.replace('%s', '?')
            cursor = conn.cursor()
            cursor.execute(query, params)
        else:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            
        if fetch_one:
            row = cursor.fetchone()
            return dict(row) if is_sqlite and row else row
        elif fetch_all:
            rows = cursor.fetchall()
            return [dict(row) for row in rows] if is_sqlite else rows
        else:
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"❌ Query error: {e}")
        return None
    finally:
        if conn:
            conn.close()
