# FIXXY Project Structure

## 📁 Repository Overview

This repository contains the complete FIXXY Car Spare Parts & Billing System migrated from SQLite to MySQL.

---

## 📂 File Structure

```
fixxy/
├── fixxy-3.py                  # Main application file (Tkinter GUI + MySQL)
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore patterns
│
├── 📖 Documentation
│   ├── README.md               # Complete project documentation
│   ├── QUICKSTART.md           # 5-minute quick start guide
│   ├── MYSQL_SETUP.md          # MySQL installation & configuration
│   ├── MIGRATION_SUMMARY.md    # SQLite to MySQL migration details
│   ├── START_HERE.txt          # Quick reference guide
│   └── PROJECT_STRUCTURE.md    # This file
│
└── 🛠️ Setup & Testing Tools
    ├── setup_fixxy.py          # Interactive setup wizard
    ├── test_mysql_connection.py # Test MySQL connectivity
    ├── find_mysql_password.py   # Find common MySQL passwords
    └── run_fixxy.bat            # Windows batch file to run FIXXY
```

---

## 📄 File Descriptions

### Core Application

| File | Description | Lines |
|------|-------------|-------|
| **fixxy-3.py** | Main application with Tkinter GUI and MySQL backend | ~1,250 |
| **requirements.txt** | Python package dependencies (mysql-connector-python) | 8 |

### Documentation Files

| File | Purpose | Size |
|------|---------|------|
| **README.md** | Comprehensive setup and usage documentation | ~400 lines |
| **QUICKSTART.md** | Fast 5-minute setup guide for quick start | ~100 lines |
| **MYSQL_SETUP.md** | Detailed MySQL installation and troubleshooting | ~400 lines |
| **MIGRATION_SUMMARY.md** | Technical migration details (SQLite → MySQL) | ~600 lines |
| **START_HERE.txt** | Quick reference with ASCII art formatting | ~100 lines |

### Helper Scripts

| File | Purpose | Use Case |
|------|---------|----------|
| **setup_fixxy.py** | Interactive wizard to configure MySQL password | First-time setup |
| **test_mysql_connection.py** | Test MySQL connection with current credentials | Troubleshooting |
| **find_mysql_password.py** | Try common MySQL passwords automatically | Password recovery |
| **run_fixxy.bat** | Windows batch file to launch FIXXY | Quick launch |

---

## 🗄️ Database Schema

The application creates **6 tables** in MySQL:

### Tables

1. **users** - User authentication and accounts
   - Columns: id, username, password_hash, full_name, role, created_at
   - Indexes: username

2. **products** - Spare parts and services inventory
   - Columns: id, name, category, price, stock, description, sold
   - Indexes: name, category

3. **coupons** - Discount coupon codes
   - Columns: code (PK), discount, description, active

4. **orders** - Customer orders and bills
   - Columns: id, bill_no, user_id, customer details, totals, payment_method, created_at
   - Foreign keys: user_id → users(id)

5. **order_items** - Individual items in each order
   - Columns: id, order_id, product_id, product_name, category, price, quantity, total
   - Foreign keys: order_id → orders(id), product_id → products(id)

6. **settings** - Application configuration
   - Columns: key (PK), value

---

## 📊 Default Data

When you run FIXXY for the first time, it automatically seeds:

- **18 Spare Parts**: Oil Filter, Brake Pads, Battery, Spark Plug, etc.
- **4 Water Wash Services**: Full Clean, Foam Wash, Premium, Deep Clean
- **2 Discount Coupons**: WELCOME10 (10%), SERVICE5 (5%)
- **1 Admin User**: admin / admin123
- **3 Settings**: shop_name, gst_rate, currency

---

## 🔧 Technology Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.7+ |
| **GUI Framework** | Tkinter (built-in) |
| **Database** | MySQL 8.x |
| **Database Driver** | mysql-connector-python |
| **Password Hashing** | PBKDF2 (hashlib) |

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/preetham711/fixxy.git
cd fixxy
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure MySQL
```bash
python setup_fixxy.py
```

### 4. Run Application
```bash
python fixxy-3.py
```

### 5. Login
```
Username: admin
Password: admin123
```

---

## 📖 Documentation Reading Order

For new users, read in this order:

1. **START_HERE.txt** - Quick overview
2. **QUICKSTART.md** - Get running in 5 minutes
3. **README.md** - Full documentation
4. **MYSQL_SETUP.md** - If you have MySQL issues
5. **MIGRATION_SUMMARY.md** - Technical details (for developers)

---

## 🔐 Security Notes

### Development
- Default MySQL password is set to "root" in the code
- Default admin password is "admin123"

### Production (if deploying)
- Use environment variables for credentials
- Change default admin password
- Create dedicated MySQL user (not root)
- Enable MySQL SSL connections

---

## 🐛 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| "Access denied" error | Run `python setup_fixxy.py` to configure password |
| "Can't connect to MySQL" | Check if MySQL service is running |
| "mysql.connector not found" | Run `pip install mysql-connector-python` |
| "Unknown database" | Application creates it automatically on first run |

### Helper Commands

```bash
# Test MySQL connection
python test_mysql_connection.py

# Try common passwords
python find_mysql_password.py

# Check MySQL service (Windows)
Get-Service -Name MySQL*

# View logs
python fixxy-3.py
```

---

## 🎓 Educational Value

This project demonstrates:

✅ Object-Oriented Programming (OOP)  
✅ MySQL Database Design & Operations  
✅ GUI Development (Tkinter)  
✅ CRUD Operations  
✅ Transaction Management  
✅ Password Security (PBKDF2)  
✅ Form Validation  
✅ Exception Handling  
✅ File I/O  
✅ HTML Generation  
✅ MVC Pattern  

---

## 📝 Features

### Customer Features
- User registration and login
- Browse 18+ spare parts with search
- View 4 water wash service packages
- Shopping cart with quantity controls
- Apply discount coupons
- GST calculation (18%)
- Multiple payment methods
- Invoice export (HTML/Text)

### Admin Features
- Stock management
- Add new products
- Coupon management
- Settings configuration
- View sales data

---

## 🔄 Migration Details

This project was migrated from SQLite to MySQL:

| Aspect | Changed |
|--------|---------|
| Database | SQLite → MySQL |
| Placeholders | `?` → `%s` |
| Data Types | REAL → DECIMAL, INTEGER → INT |
| Auto Increment | AUTOINCREMENT → AUTO_INCREMENT |
| Upsert | ON CONFLICT → ON DUPLICATE KEY UPDATE |
| Case Insensitive | COLLATE NOCASE → LOWER()/charset |

See **MIGRATION_SUMMARY.md** for complete technical details.

---

## 📜 License

Educational project for Class XII Computer Science.

---

## 🤝 Contributing

This is a school project, but suggestions are welcome!

---

## 📧 Contact

Repository: https://github.com/preetham711/fixxy

---

**Built with ❤️ for learning and demonstration purposes.**
