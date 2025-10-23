import pyodbc
import subprocess


def find_sql_instance():
    print("🔍 Finding SQL Server instance...")

    # Get available ODBC drivers
    print("\n📋 Available ODBC Drivers:")
    drivers = pyodbc.drivers()
    for i, driver in enumerate(drivers, 1):
        print(f"   {i}. {driver}")

    # Common server configurations to test
    servers_to_test = [
        'localhost',
        'localhost\\SQLEXPRESS',
        '.',
        '.\\SQLEXPRESS',
        '(local)',
        '127.0.0.1',
        'localhost,1433'
    ]

    print("\n🔌 Testing connections...")
    successful_connections = []

    for driver in drivers:
        if 'SQL Server' in driver or 'ODBC' in driver:
            print(f"\n🚀 Testing driver: {driver}")

            for server in servers_to_test:
                try:
                    # Test with Windows Authentication
                    conn_str = f"DRIVER={{{driver}}};SERVER={server};Trusted_Connection=yes;Timeout=3;"
                    conn = pyodbc.connect(conn_str)

                    cursor = conn.cursor()
                    cursor.execute("SELECT @@SERVERNAME as server_name, DB_NAME() as db_name")
                    row = cursor.fetchone()

                    print(f"   ✅ SUCCESS: {server}")
                    print(f"      Server: {row.server_name}")
                    print(f"      Driver: {driver}")

                    successful_connections.append({
                        'server': server,
                        'driver': driver,
                        'server_name': row.server_name
                    })

                    conn.close()
                    break  # Stop testing this driver if one connection works

                except pyodbc.Error as e:
                    print(f"   ❌ Failed: {server} - {str(e)[:50]}...")

    return successful_connections


if __name__ == "__main__":
    results = find_sql_instance()

    if results:
        print("\n🎉 SUCCESSFUL CONNECTIONS FOUND:")
        for i, result in enumerate(results, 1):
            print(f"{i}. Server: {result['server']}")
            print(f"   Driver: {result['driver']}")
            print(f"   Name: {result['server_name']}")
    else:
        print("\n❌ No successful connections found.")