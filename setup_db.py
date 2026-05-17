import psycopg2
import os
from dotenv import load_dotenv

def setup_database():
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in .env file!")
        return
    
    print("Connecting to PostgreSQL...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Read the SQL schema
        sql_path = os.path.join("Data Base", "Postgres_Schema.sql")
        print(f"Reading schema from {sql_path}...")
        with open(sql_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
            
        print("Executing SQL script...")
        cur.execute(sql_script)
        print("✅ Database schema initialized successfully!")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error setting up database: {e}")

if __name__ == "__main__":
    setup_database()
