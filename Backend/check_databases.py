import pyodbc


def check_databases():
    # Use the connection string that worked from above
    conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;Trusted_Connection=yes;"

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Get all databases
        cursor.execute("""
            SELECT name, state_desc, create_date 
            FROM sys.databases 
            WHERE state = 0  -- Only online databases
            ORDER BY name
        """)

        print("📊 Available databases:")
        print("-" * 50)
        for row in cursor:
            print(f"📁 {row.name}")
            print(f"   Status: {row.state_desc}")
            print(f"   Created: {row.create_date}")
            print()

        conn.close()

    except pyodbc.Error as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_databases()