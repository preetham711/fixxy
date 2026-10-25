# MySQL Setup Guide for FIXXY

This guide will help you set up MySQL for the FIXXY application.

---

## Option 1: Quick Setup (Automatic)

The FIXXY application will automatically create the database and tables on first run. You only need to:

1. **Install MySQL Server** (see below)
2. **Configure credentials** in `fixxy-3.py`
3. **Run the application**

---

## Installing MySQL Server

### Windows

1. **Download MySQL Installer**
   - Visit: https://dev.mysql.com/downloads/installer/
   - Download "MySQL Installer for Windows"

2. **Run the Installer**
   - Choose "Developer Default" or "Server only"
   - Set a **root password** (remember this!)
   - Use default port: **3306**

3. **Verify Installation**
   - Open Command Prompt
   - Run: `mysql --version`

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install MySQL Server
sudo apt install mysql-server

# Secure the installation
sudo mysql_secure_installation

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql
```

### macOS

```bash
# Using Homebrew
brew install mysql

# Start MySQL service
brew services start mysql

# Secure the installation
mysql_secure_installation
```

---

## Configuring FIXXY for MySQL

### Method 1: Edit the Python File (Simple)

Open `fixxy-3.py` and find this section (around line 45):

```python
MYSQL_HOST = os.getenv("FIXXY_MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("FIXXY_MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("FIXXY_MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("FIXXY_MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("FIXXY_MYSQL_DATABASE", "fixxy_store")
```

Change to:

```python
MYSQL_HOST = os.getenv("FIXXY_MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("FIXXY_MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("FIXXY_MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("FIXXY_MYSQL_PASSWORD", "YOUR_MYSQL_PASSWORD")  # ⚠️ Put your password here
MYSQL_DATABASE = os.getenv("FIXXY_MYSQL_DATABASE", "fixxy_store")
```

### Method 2: Use Environment Variables (Recommended)

This is more secure as it doesn't store the password in the source code.

**Windows PowerShell:**
```powershell
$env:FIXXY_MYSQL_HOST = "localhost"
$env:FIXXY_MYSQL_PORT = "3306"
$env:FIXXY_MYSQL_USER = "root"
$env:FIXXY_MYSQL_PASSWORD = "your_password_here"
$env:FIXXY_MYSQL_DATABASE = "fixxy_store"
```

**Windows Command Prompt:**
```cmd
set FIXXY_MYSQL_HOST=localhost
set FIXXY_MYSQL_PORT=3306
set FIXXY_MYSQL_USER=root
set FIXXY_MYSQL_PASSWORD=your_password_here
set FIXXY_MYSQL_DATABASE=fixxy_store
```

**Linux/macOS:**
```bash
export FIXXY_MYSQL_HOST="localhost"
export FIXXY_MYSQL_PORT="3306"
export FIXXY_MYSQL_USER="root"
export FIXXY_MYSQL_PASSWORD="your_password_here"
export FIXXY_MYSQL_DATABASE="fixxy_store"
```

To make these permanent, add them to:
- Windows: System Environment Variables
- Linux/macOS: `~/.bashrc` or `~/.zshrc`

---

## Option 2: Manual Database Setup

If you prefer to create the database manually before running the application:

### Step 1: Connect to MySQL

**Windows Command Prompt:**
```cmd
mysql -u root -p
```

**Linux/macOS Terminal:**
```bash
mysql -u root -p
```

Enter your root password when prompted.

### Step 2: Create the Database

```sql
CREATE DATABASE fixxy_store 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```

### Step 3: Verify

```sql
SHOW DATABASES;
```

You should see `fixxy_store` in the list.

### Step 4: Exit MySQL

```sql
EXIT;
```

### Step 5: Run FIXXY

The application will automatically create tables and seed data.

---

## Creating a Dedicated MySQL User (Optional but Recommended)

Instead of using the root user, you can create a dedicated user for FIXXY:

```sql
-- Connect to MySQL as root
mysql -u root -p

-- Create a new user
CREATE USER 'fixxy_user'@'localhost' IDENTIFIED BY 'fixxy_password_123';

-- Grant privileges on fixxy_store database
GRANT ALL PRIVILEGES ON fixxy_store.* TO 'fixxy_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Exit
EXIT;
```

Then update your configuration:

```python
MYSQL_USER = "fixxy_user"
MYSQL_PASSWORD = "fixxy_password_123"
```

---

## Database Schema

The application creates these tables automatically:

### users
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- username (VARCHAR, UNIQUE)
- password_hash (TEXT)
- full_name (VARCHAR)
- role (VARCHAR) - 'customer' or 'admin'
- created_at (DATETIME)

### products
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- name (VARCHAR)
- category (VARCHAR)
- price (DECIMAL)
- stock (INT)
- description (TEXT)
- sold (INT)

### coupons
- code (VARCHAR, PRIMARY KEY)
- discount (DECIMAL)
- description (TEXT)
- active (TINYINT)

### orders
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- bill_no (VARCHAR, UNIQUE)
- user_id (INT, FOREIGN KEY)
- customer_name (VARCHAR)
- phone (VARCHAR)
- address (TEXT)
- car_brand, car_model, car_year (VARCHAR)
- subtotal, discount, gst, grand_total (DECIMAL)
- coupon_code (VARCHAR)
- payment_method (VARCHAR)
- created_at (DATETIME)

### order_items
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- order_id (INT, FOREIGN KEY)
- product_id (INT, FOREIGN KEY)
- product_name (VARCHAR)
- category (VARCHAR)
- price (DECIMAL)
- quantity (INT)
- total (DECIMAL)

### settings
- key (VARCHAR, PRIMARY KEY)
- value (TEXT)

---

## Verifying the Setup

After running FIXXY for the first time, you can verify the database:

```sql
-- Connect to MySQL
mysql -u root -p

-- Use the database
USE fixxy_store;

-- List all tables
SHOW TABLES;

-- Check default products
SELECT * FROM products LIMIT 5;

-- Check default admin user
SELECT username, full_name, role FROM users;

-- Check coupons
SELECT * FROM coupons;

-- Exit
EXIT;
```

---

## Troubleshooting

### Can't connect to MySQL

```bash
# Check if MySQL is running (Windows)
sc query MySQL80

# Check if MySQL is running (Linux/macOS)
sudo systemctl status mysql
```

### Forgot MySQL root password

**Windows:**
1. Stop MySQL service
2. Start MySQL with skip-grant-tables
3. Reset password
4. Restart normally

**Linux:**
```bash
sudo mysql
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
EXIT;
```

### Port 3306 already in use

Check what's using the port:
```bash
# Windows
netstat -ano | findstr :3306

# Linux/macOS
sudo lsof -i :3306
```

### Access denied error

- Verify username and password
- Check that user has privileges
- Try connecting with mysql command line first

### Database exists but tables are empty

Delete and recreate:
```sql
DROP DATABASE fixxy_store;
CREATE DATABASE fixxy_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Then run FIXXY again.

---

## Default Data Seeded

When you first run FIXXY, these are automatically created:

### Products (18 spare parts)
- Oil Filter, Air Filter, Brake Pads, Spark Plug, Battery
- Timing Belt, Alternator, Water Pump, Clutch Plate
- Shock Absorber, Headlight Bulb, Wiper Blades, Radiator
- Fuel Pump, Wheel Bearing, Cabin Air Filter, Disc Rotor, Fuse Set

### Water Wash Services (4 packages)
- Full Clean (₹499)
- Foam Wash (₹699)
- Premium Foam + Wax (₹999)
- Interior Deep Clean (₹1299)

### Coupons (2 codes)
- WELCOME10 - 10% discount
- SERVICE5 - 5% discount

### Admin Account
- Username: admin
- Password: admin123

---

## Backup & Restore

### Backup the database

```bash
mysqldump -u root -p fixxy_store > fixxy_backup.sql
```

### Restore from backup

```bash
mysql -u root -p fixxy_store < fixxy_backup.sql
```

---

## Security Recommendations

1. **Change default admin password** after first login
2. **Use a dedicated MySQL user** (not root)
3. **Use strong passwords** for MySQL users
4. **Don't commit passwords** to version control
5. **Use environment variables** for credentials
6. **Enable SSL** for MySQL connections in production
7. **Regular backups** of the database

---

**You're all set! Run `python fixxy-3.py` to start the application.**
