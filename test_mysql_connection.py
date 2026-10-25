"""
Quick MySQL Connection Test for FIXXY
"""
import os
import mysql.connector
from mysql.connector import Error as MySQLError

# Configuration
MYSQL_HOST = os.getenv("FIXXY_MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("FIXXY_MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("FIXXY_MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("FIXXY_MYSQL_PASSWORD", "root")  # Try 'root' as default
MYSQL_DATABASE = os.getenv("FIXXY_MYSQL_DATABASE", "fixxy_store")

print("=" * 60)
print("FIXXY MySQL Connection Test")
print("=" * 60)
print(f"\nAttempting to connect to MySQL...")
print(f"Host: {MYSQL_HOST}")
print(f"Port: {MYSQL_PORT}")
print(f"User: {MYSQL_USER}")
print(f"Password: {'(empty)' if not MYSQL_PASSWORD else '***set***'}")
print(f"Database: {MYSQL_DATABASE}")
print()

try:
    # Try connecting without database first
    print("Step 1: Connecting to MySQL server...")
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )
    print("✅ Successfully connected to MySQL server!")
    
    # Check if database exists
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES LIKE 'fixxy_store'")
    result = cursor.fetchone()
    
    if result:
        print(f"✅ Database '{MYSQL_DATABASE}' already exists!")
    else:
        print(f"ℹ️  Database '{MYSQL_DATABASE}' does not exist (will be created by FIXXY)")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ CONNECTION TEST PASSED!")
    print("=" * 60)
    print("\nYou can now run: python fixxy-3.py")
    print()
    
except MySQLError as e:
    print(f"\n❌ CONNECTION FAILED!")
    print(f"Error Code: {e.errno}")
    print(f"Error Message: {e.msg}")
    print()
    
    if e.errno == 1045:
        print("🔧 FIX: Access denied - Wrong password!")
        print()
        print("Solutions:")
        print("1. Set environment variable:")
        print('   $env:FIXXY_MYSQL_PASSWORD = "your_password"')
        print()
        print("2. Or edit fixxy-3.py line ~68:")
        print('   MYSQL_PASSWORD = "your_mysql_password"')
        print()
    elif e.errno == 2003:
        print("🔧 FIX: Can't connect to MySQL server!")
        print()
        print("Check if MySQL is running:")
        print("   Get-Service -Name MySQL*")
        print()
    else:
        print("🔧 Check your MySQL configuration and try again.")
        print()
    
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    print()
