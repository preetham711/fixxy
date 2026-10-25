"""
FIXXY Setup Wizard
Interactive configuration for MySQL password
"""
import os
import mysql.connector
from pathlib import Path

print("=" * 70)
print("🚗 FIXXY SETUP WIZARD")
print("=" * 70)
print()
print("This wizard will help you configure FIXXY to connect to MySQL.")
print()

# Get MySQL password
print("Please enter your MySQL root password:")
print("(The password won't be visible as you type for security)")
print()

import getpass
mysql_password = getpass.getpass("MySQL root password: ")

# Test the connection
print()
print("Testing MySQL connection...", end=" ")

try:
    conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password=mysql_password
    )
    
    print("✅ SUCCESS!")
    conn.close()
    
    # Update the fixxy-3.py file
    fixxy_file = Path("fixxy-3.py")
    
    if fixxy_file.exists():
        print()
        print("Updating fixxy-3.py with your MySQL password...")
        
        content = fixxy_file.read_text(encoding='utf-8')
        
        # Find and replace the password line
        import re
        pattern = r'MYSQL_PASSWORD = os\.getenv\("FIXXY_MYSQL_PASSWORD", ".*?"\)'
        replacement = f'MYSQL_PASSWORD = os.getenv("FIXXY_MYSQL_PASSWORD", "{mysql_password}")'
        
        new_content = re.sub(pattern, replacement, content)
        
        fixxy_file.write_text(new_content, encoding='utf-8')
        
        print("✅ Configuration updated!")
        print()
        print("=" * 70)
        print("✅ SETUP COMPLETE!")
        print("=" * 70)
        print()
        print("You can now run FIXXY:")
        print("   python fixxy-3.py")
        print()
        print("The application will open in a desktop window.")
        print("Default login: admin / admin123")
        print()
    else:
        print("❌ Could not find fixxy-3.py")
        print()
        print("But your password works! Manually edit fixxy-3.py:")
        print(f'   MYSQL_PASSWORD = "{mysql_password}"')
        print()

except mysql.connector.Error as e:
    print("❌ FAILED!")
    print()
    if e.errno == 1045:
        print("❌ Access denied - Wrong password!")
        print()
        print("The password you entered is incorrect.")
        print("Please run this script again with the correct password.")
    elif e.errno == 2003:
        print("❌ Can't connect to MySQL server!")
        print()
        print("Make sure MySQL is running:")
        print("   Get-Service -Name MySQL*")
    else:
        print(f"❌ Error {e.errno}: {e.msg}")
    print()

except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print()
