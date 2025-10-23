# quick_test.py
import pyodbc

try:
    # Try Windows Authentication first
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "Trusted_Connection=yes;"
    )
    print("✅ Connected to SQL Server!")

    cursor = conn.cursor()
    cursor.execute("SELECT @@version")
    version = cursor.fetchone()[0]
    print(f"SQL Server Version: {version}")

    conn.close()

except pyodbc.Error as e:
    print(f"❌ Connection failed: {e}")