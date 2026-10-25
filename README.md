# FIXXY — Car Spare Parts & Billing System

**A comprehensive car spare parts inventory and billing management system built with Python, Tkinter, and MySQL.**

---

## 🚗 Overview

FIXXY is a complete billing and inventory management system designed for car spare parts shops. It features a modern dark-themed GUI, customer registration, product catalogue, shopping cart, billing with GST calculation, coupon discounts, water wash services, and invoice generation.

### Key Features

- **User Authentication**: Secure login with PBKDF2 password hashing
- **Customer Registration**: New customers can create accounts
- **Product Catalogue**: Searchable parts with categories, stock tracking, and favorites
- **Shopping Cart**: Add/remove items, update quantities
- **Water Wash Services**: Special service packages
- **Coupon System**: Apply discount coupons at checkout
- **GST Calculation**: Automatic 18% GST calculation (configurable)
- **Billing & Orders**: Complete checkout with customer and vehicle details
- **Invoice Export**: HTML and text format invoice export
- **Stock Management**: Admin panel for inventory control
- **Settings**: Configure shop name, GST rate, and other parameters

---

## 🔧 Technology Stack

- **Language**: Python 3
- **GUI Framework**: Tkinter (built-in with Python)
- **Database**: MySQL 8.x
- **Python Package**: mysql-connector-python

---

## 📋 Prerequisites

Before running FIXXY, ensure you have the following installed:

### 1. Python 3.7 or higher
Check your Python version:
```bash
python --version
```

### 2. MySQL Server 8.x
Download and install MySQL from: https://dev.mysql.com/downloads/mysql/

**Important**: Remember the root password you set during MySQL installation.

### 3. pip (Python package manager)
Usually comes with Python. Verify:
```bash
pip --version
```

---

## 🚀 Installation & Setup

### Step 1: Install MySQL Connector

Open your terminal/command prompt and run:

```bash
pip install mysql-connector-python
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

### Step 2: Configure MySQL Connection

Open `fixxy-3.py` and locate the MySQL configuration section (around line 45):

```python
# ============================================================================
# MYSQL DATABASE CONFIGURATION
# ============================================================================

MYSQL_HOST = os.getenv("FIXXY_MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("FIXXY_MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("FIXXY_MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("FIXXY_MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("FIXXY_MYSQL_DATABASE", "fixxy_store")
```

**Option A: Edit the file directly**

Change the default values to match your MySQL setup:

```python
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "your_mysql_root_password"  # ⚠️ Enter your MySQL password here
MYSQL_DATABASE = "fixxy_store"
```

**Option B: Use environment variables (recommended for security)**

Set environment variables before running the application:

**Windows (PowerShell):**
```powershell
$env:FIXXY_MYSQL_PASSWORD = "your_mysql_root_password"
```

**Windows (Command Prompt):**
```cmd
set FIXXY_MYSQL_PASSWORD=your_mysql_root_password
```

**Linux/Mac:**
```bash
export FIXXY_MYSQL_PASSWORD="your_mysql_root_password"
```

### Step 3: Ensure MySQL Server is Running

**Windows:**
- Open Services (Win+R → `services.msc`)
- Find "MySQL80" or similar
- Ensure it's running

**Linux/Mac:**
```bash
sudo systemctl status mysql
```

Or:
```bash
sudo service mysql status
```

### Step 4: Run the Application

Navigate to the project folder and run:

```bash
python fixxy-3.py
```

**First Run**: The application will automatically:
1. Create the `fixxy_store` database
2. Create all required tables (users, products, orders, etc.)
3. Seed default products (18 spare parts)
4. Seed water wash services (4 packages)
5. Seed default coupons (WELCOME10, SERVICE5)
6. Create the admin account

---

## 🔐 Default Login Credentials

**Username**: `admin`  
**Password**: `admin123`

⚠️ **Change the admin password after first login for production use.**

---

## 💾 Database Structure

The application creates the following MySQL tables:

### Tables

1. **users** - User accounts (customers and admin)
2. **products** - Spare parts and water wash services
3. **coupons** - Discount coupons
4. **orders** - Customer orders/bills
5. **order_items** - Individual items in each order
6. **settings** - Application settings (shop name, GST rate, etc.)

### Default Data

- **18 Spare Parts**: Oil filters, brake pads, batteries, spark plugs, etc.
- **4 Water Wash Services**: Full Clean, Foam Wash, Premium Foam + Wax, Interior Deep Clean
- **2 Coupons**: WELCOME10 (10% off), SERVICE5 (5% off)
- **1 Admin User**: admin/admin123

---

## 📱 Usage Guide

### For Customers

1. **Register**: Click "Create a new customer account" on the login screen
2. **Browse Parts**: Use "Find Parts" to search the catalogue
3. **Add to Cart**: Click "Add to Cart" on any product
4. **Water Wash**: Choose from 4 wash packages
5. **Checkout**: Review cart, enter vehicle details, apply coupons
6. **Payment**: Choose payment method (UPI QR, Card, Cash on Delivery)
7. **Invoice**: View and export bill in HTML or text format

### For Admin

Admin users have additional capabilities:

1. **Manage Stock**: Add new products, view inventory
2. **Coupons**: Create and manage discount coupons
3. **Settings**: Update shop name, GST rate

---

## 🔄 Migration from SQLite

This version uses **MySQL** instead of SQLite. The old `fixxy_store.db` file is **no longer used**.

### Key Changes

- **Database**: SQLite → MySQL
- **Placeholders**: `?` → `%s`
- **AUTO_INCREMENT**: `INTEGER PRIMARY KEY AUTOINCREMENT` → `INT AUTO_INCREMENT PRIMARY KEY`
- **Data Types**: `REAL` → `DECIMAL(10,2)` for money values
- **Date/Time**: ISO format strings → MySQL DATETIME
- **Case-Insensitive**: `COLLATE NOCASE` → `LOWER()` function or charset collation
- **Upsert**: `ON CONFLICT ... DO UPDATE` → `ON DUPLICATE KEY UPDATE`
- **Insert Ignore**: `INSERT OR IGNORE` → `INSERT IGNORE`

---

## 🛠️ Troubleshooting

### Error: "mysql.connector not found"

**Solution**: Install the MySQL connector:
```bash
pip install mysql-connector-python
```

### Error: "Access denied for user 'root'@'localhost'"

**Solution**: Check your MySQL password in the configuration section.

### Error: "Can't connect to MySQL server"

**Solutions**:
1. Ensure MySQL server is running
2. Check the hostname (should be `localhost` for local installation)
3. Check the port (default is 3306)

### Error: "Unknown database 'fixxy_store'"

**Solution**: The application should create this automatically. If it doesn't, create it manually:

```sql
CREATE DATABASE fixxy_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Then run the application again.

### Application won't start

**Solution**: Check the error message. Common issues:
1. MySQL not running
2. Wrong password
3. MySQL connector not installed
4. Python version too old (need 3.7+)

---

## 🗄️ Manual Database Setup (if needed)

If automatic database creation fails, you can create it manually:

1. Open MySQL command line or MySQL Workbench
2. Run:

```sql
CREATE DATABASE IF NOT EXISTS fixxy_store 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```

3. Run the application — tables will be created automatically

---

## 📊 Features in Detail

### Product Management
- Add products with name, category, price, stock, description
- Track stock levels automatically during checkout
- Track total units sold
- Category-based filtering

### Cart & Billing
- Real-time cart updates
- Quantity controls
- Stock validation
- Subtotal, discount, GST, and grand total calculation

### Coupon System
- Create percentage-based discount coupons
- Enable/disable coupons
- Case-insensitive coupon codes
- Automatic discount application

### Order Management
- Generate unique bill numbers (format: FXyymmddHHMMSS + random)
- Store customer and vehicle details
- Track payment method
- Transaction-based checkout (all-or-nothing)

### Invoice Export
- HTML format (printable, can be saved as PDF from browser)
- Plain text format
- Complete order details with line items

---

## 🔐 Security Notes

### For Development/School Project
The current configuration stores the MySQL password in the source code, which is acceptable for a school demonstration project.

### For Production Use
1. **Never commit passwords to version control**
2. Use environment variables for credentials
3. Change the default admin password
4. Use a dedicated MySQL user (not root)
5. Enable MySQL SSL connections
6. Implement proper session management

---

## 📝 Project Information

- **Title**: FIXXY — Car Spare Parts & Billing System
- **Type**: Class XII Computer Science Project
- **Language**: Python 3
- **GUI**: Tkinter
- **Database**: MySQL
- **Concepts**: OOP, database connectivity, CRUD operations, GUI programming, password hashing, transaction management

---

## 📄 License

This is a school project for educational purposes.

---

## 🤝 Support

For issues or questions about this project:

1. Check the Troubleshooting section above
2. Verify MySQL is running and credentials are correct
3. Check Python and package versions
4. Review the error messages in the console

---

## 🎓 Learning Outcomes

This project demonstrates:

- Object-oriented programming in Python
- MySQL database design and operations
- GUI development with Tkinter
- CRUD operations (Create, Read, Update, Delete)
- Transaction management
- Password hashing (PBKDF2)
- Form validation
- Exception handling
- File I/O operations
- HTML generation

---

**Built with ❤️ for learning and demonstration purposes.**
