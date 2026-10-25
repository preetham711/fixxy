"""
Try common MySQL passwords to help you find the right one
"""
import mysql.connector

common_passwords = [
    "",           # Empty password
    "root",       # Common default
    "password",   # Another common one
    "admin",      # Sometimes used
    "mysql",      # Sometimes used
    "123456",     # Weak but common
]

print("=" * 60)
print("Trying Common MySQL Passwords...")
print("=" * 60)
print()

for pwd in common_passwords:
    try:
        pwd_display = "(empty)" if pwd == "" else pwd
        print(f"Trying password: {pwd_display}...", end=" ")
        
        conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password=pwd
        )
        
        print("✅ SUCCESS!")
        print()
        print("=" * 60)
        print(f"✅ FOUND IT! Your MySQL password is: {pwd_display}")
        print("=" * 60)
        print()
        print("Now update fixxy-3.py line ~68:")
        if pwd == "":
            print('   MYSQL_PASSWORD = ""')
        else:
            print(f'   MYSQL_PASSWORD = "{pwd}"')
        print()
        
        conn.close()
        exit(0)
        
    except mysql.connector.Error as e:
        if e.errno == 1045:
            print("❌ Wrong password")
        else:
            print(f"❌ Error: {e.msg}")

print()
print("=" * 60)
print("❌ None of the common passwords worked!")
print("=" * 60)
print()
print("You need to find or reset your MySQL root password.")
print()
print("To reset MySQL password on Windows:")
print("1. Stop MySQL service")
print("2. Start it with --skip-grant-tables")
print("3. Connect and reset password")
print()
print("Or check your MySQL installation notes for the password.")
