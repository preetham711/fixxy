# FIXXY Quick Start Guide

Get FIXXY running in 5 minutes!

---

## ⚡ Quick Setup (5 Steps)

### Step 1: Install MySQL

**Windows:**
- Download: https://dev.mysql.com/downloads/installer/
- Install and set a root password (remember it!)

**Linux:**
```bash
sudo apt install mysql-server
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

### Step 2: Install Python Package

```bash
pip install mysql-connector-python
```

### Step 3: Configure Password

Edit `fixxy-3.py` around line 50:

```python
MYSQL_PASSWORD = os.getenv("FIXXY_MYSQL_PASSWORD", "YOUR_PASSWORD_HERE")
```

Replace `"YOUR_PASSWORD_HERE"` with your MySQL root password.

Or set an environment variable:

**Windows PowerShell:**
```powershell
$env:FIXXY_MYSQL_PASSWORD = "your_password"
```

**Windows CMD:**
```cmd
set FIXXY_MYSQL_PASSWORD=your_password
```

**Linux/macOS:**
```bash
export FIXXY_MYSQL_PASSWORD="your_password"
```

### Step 4: Run the Application

```bash
python fixxy-3.py
```

### Step 5: Login

**Username:** `admin`  
**Password:** `admin123`

---

## ✅ What Happens on First Run

1. ✅ Creates `fixxy_store` database in MySQL
2. ✅ Creates 6 tables (users, products, orders, etc.)
3. ✅ Adds 18 spare parts
4. ✅ Adds 4 water wash services
5. ✅ Adds 2 coupons (WELCOME10, SERVICE5)
6. ✅ Creates admin account

**All automatic — no manual steps required!**

---

## 🔧 Troubleshooting

### ❌ "Access denied for user 'root'"

**Fix:** Wrong password. Check MySQL password in the config.

### ❌ "mysql.connector not found"

**Fix:**
```bash
pip install mysql-connector-python
```

### ❌ "Can't connect to MySQL server"

**Fix:** Start MySQL service:

**Windows:** Services → MySQL80 → Start

**Linux:**
```bash
sudo systemctl start mysql
```

**macOS:**
```bash
brew services start mysql
```

---

## 📚 Need More Help?

- **Full setup:** See README.md
- **MySQL details:** See MYSQL_SETUP.md
- **Migration info:** See MIGRATION_SUMMARY.md

---

## 🎯 Test Checklist

After running, test these:

- [ ] Login as admin (admin/admin123)
- [ ] Create a new customer account
- [ ] Browse products (should see 18+ items)
- [ ] Add item to cart
- [ ] Apply coupon WELCOME10
- [ ] Complete checkout
- [ ] View generated bill

---

**That's it! You're ready to go! 🚗💨**
