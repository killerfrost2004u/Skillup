import psycopg2
import os
from dotenv import load_dotenv

def setup_database():
    # Connection string provided by the user
    DATABASE_URL = "postgresql://neondb_owner:npg_mM8uwqzxLD3y@ep-patient-block-al080m6m-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    print("Connecting to Neon PostgreSQL...")
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
