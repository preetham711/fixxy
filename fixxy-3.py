"""
FIXXY — Car Spare Parts & Billing System
Class XII Computer Science Project
Python 3 + Tkinter + MySQL

Features
--------
• Login and account registration (passwords hashed with PBKDF2)
• Dashboard and vehicle details
• Searchable spare-parts catalogue with categories and stock tracking
• Combined cart and billing screen with INR totals
• Water-wash packages and separate payment-details screen
• Cart quantity controls, coupon discounts, GST calculation
• Customer checkout and order/bill generation
• Printable/exportable invoice (HTML works without extra packages;
  optional PDF export uses ReportLab if installed)
• Product stock management, coupon management, settings, CSV export
• MySQL database created automatically on first run

Requirements:
    pip install mysql-connector-python

Run:
    python fixxy-3.py

Demo login:
    Username: admin
    Password: admin123

The demo account is for school demonstration only. Change it before real use.
"""

import csv
import hashlib
import hmac
import html
import os
import secrets
import sys
import webbrowser
from datetime import datetime, date
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:
    import tkinter.messagebox as mb
    mb.showerror("Missing Dependency", 
                 "MySQL Connector is required.\n\n"
                 "Install it using:\n"
                 "pip install mysql-connector-python")
    sys.exit(1)

# ============================================================================
# MYSQL DATABASE CONFIGURATION
# ============================================================================
# Configure your MySQL connection below, or set environment variables:
#   FIXXY_MYSQL_HOST, FIXXY_MYSQL_PORT, FIXXY_MYSQL_USER,
#   FIXXY_MYSQL_PASSWORD, FIXXY_MYSQL_DATABASE

MYSQL_HOST = os.getenv("FIXXY_MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("FIXXY_MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("FIXXY_MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("FIXXY_MYSQL_PASSWORD", "root")  # ⚠️ Change this to your MySQL password
MYSQL_DATABASE = os.getenv("FIXXY_MYSQL_DATABASE", "fixxy_store")

APP_NAME = "FIXXY"
TAGLINE = "Drive Better  •  Fix Smarter"
ORANGE = "#ff7918"
ORANGE_HOVER = "#ff923e"
BG = "#071a2d"
PANEL = "#0d2943"
PANEL2 = "#123552"
FIELD = "#183c5c"
TEXT = "#f3f7fb"
MUTED = "#a9bfd1"
GREEN = "#43c58a"
RED = "#ff626b"
GST_RATE = 0.18

DEFAULT_PRODUCTS = [
    ("Oil Filter", "Filters", 450, 30, "Engine oil filtration"),
    ("Air Filter", "Filters", 650, 25, "Cleans air entering the engine"),
    ("Brake Pads", "Brakes", 1800, 18, "Friction pads for safe braking"),
    ("Spark Plug", "Engine Parts", 350, 50, "Ignition component"),
    ("Battery", "Electrical", 4500, 12, "Automotive battery"),
    ("Timing Belt", "Engine Parts", 1200, 15, "Engine timing belt"),
    ("Alternator", "Electrical", 6500, 8, "Charges battery while driving"),
    ("Water Pump", "Engine Parts", 3200, 10, "Engine coolant circulation"),
    ("Clutch Plate", "Transmission", 2800, 11, "Clutch assembly component"),
    ("Shock Absorber", "Suspension", 2400, 16, "Suspension damping component"),
    ("Headlight Bulb", "Electrical", 550, 40, "Replacement headlight bulb"),
    ("Wiper Blades", "Accessories", 700, 22, "Windshield wiper blades"),
    ("Radiator", "Cooling", 5200, 7, "Engine cooling radiator"),
    ("Fuel Pump", "Engine Parts", 3900, 9, "Fuel delivery component"),
    ("Wheel Bearing", "Suspension", 1450, 20, "Wheel rotation bearing"),
    ("Cabin Air Filter", "Filters", 800, 24, "Filters air entering cabin"),
    ("Disc Rotor", "Brakes", 2100, 13, "Brake disc rotor"),
    ("Fuse Set", "Electrical", 250, 60, "Automotive replacement fuses"),
]
DEFAULT_COUPONS = [("WELCOME10", 10, "Welcome discount", 1),
                   ("SERVICE5", 5, "Service customer discount", 1)]
WATER_WASH_SERVICES = [
    ("Full Clean", "Water Wash", 499, 99999, "Exterior wash, wheel cleaning and basic interior wipe"),
    ("Foam Wash", "Water Wash", 699, 99999, "Snow foam pre-wash, rinse and microfiber dry"),
    ("Premium Foam + Wax", "Water Wash", 999, 99999, "Foam wash, wax finish and tyre shine"),
    ("Interior Deep Clean", "Water Wash", 1299, 99999, "Seats, mats, dashboard and interior vacuum"),
]

def money(value):
    return "₹{:,.2f}".format(float(value))

def safe_float(value, label="Value"):
    try:
        number = float(value)
        if number < 0:
            raise ValueError
        return number
    except (ValueError, TypeError):
        raise ValueError(f"{label} must be a valid non-negative number.")

def safe_int(value, label="Quantity"):
    try:
        number = int(value)
        if number < 0:
            raise ValueError
        return number
    except (ValueError, TypeError):
        raise ValueError(f"{label} must be a whole number (0 or above).")

def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 180_000)
    return salt.hex() + "$" + digest.hex()

def verify_password(password, stored):
    try:
        salt_hex, digest_hex = stored.split("$", 1)
        check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                    bytes.fromhex(salt_hex), 180_000).hex()
        return hmac.compare_digest(check, digest_hex)
    except Exception:
        return False

class Database:
    def __init__(self):
        self.config = {
            'host': MYSQL_HOST,
            'port': MYSQL_PORT,
            'user': MYSQL_USER,
            'password': MYSQL_PASSWORD,
            'database': MYSQL_DATABASE,
            'autocommit': False
        }
        self.initialize()

    def connect(self):
        """Create a MySQL connection with dictionary cursor."""
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except MySQLError as e:
            # If database doesn't exist, create it
            if e.errno == 1049:  # Unknown database
                self._create_database()
                conn = mysql.connector.connect(**self.config)
                return conn
            raise

    def _create_database(self):
        """Create the fixxy_store database if it doesn't exist."""
        temp_config = self.config.copy()
        temp_config.pop('database')
        conn = mysql.connector.connect(**temp_config)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        cursor.close()
        conn.close()

    def initialize(self):
        """Create tables and seed initial data."""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    full_name VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'customer',
                    created_at DATETIME NOT NULL,
                    INDEX idx_username (username)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Create products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    price DECIMAL(10,2) NOT NULL CHECK(price >= 0),
                    stock INT NOT NULL DEFAULT 0 CHECK(stock >= 0),
                    description TEXT,
                    sold INT NOT NULL DEFAULT 0,
                    INDEX idx_category (category),
                    INDEX idx_name (name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Create coupons table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS coupons(
                    code VARCHAR(50) PRIMARY KEY,
                    discount DECIMAL(5,2) NOT NULL CHECK(discount >= 0 AND discount <= 100),
                    description TEXT,
                    active TINYINT NOT NULL DEFAULT 1
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Create orders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bill_no VARCHAR(100) NOT NULL UNIQUE,
                    user_id INT,
                    customer_name VARCHAR(255) NOT NULL,
                    phone VARCHAR(50) NOT NULL,
                    address TEXT NOT NULL,
                    car_brand VARCHAR(100) DEFAULT '',
                    car_model VARCHAR(100) DEFAULT '',
                    car_year VARCHAR(10) DEFAULT '',
                    subtotal DECIMAL(10,2) NOT NULL,
                    discount DECIMAL(10,2) NOT NULL DEFAULT 0,
                    gst DECIMAL(10,2) NOT NULL,
                    grand_total DECIMAL(10,2) NOT NULL,
                    coupon_code VARCHAR(50) DEFAULT '',
                    payment_method VARCHAR(100) NOT NULL,
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    INDEX idx_bill_no (bill_no),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Create order_items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id INT NOT NULL,
                    product_id INT,
                    product_name VARCHAR(255) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    quantity INT NOT NULL,
                    total DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY(order_id) REFERENCES orders(id),
                    FOREIGN KEY(product_id) REFERENCES products(id),
                    INDEX idx_order_id (order_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Create settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings(
                    `key` VARCHAR(100) PRIMARY KEY,
                    `value` TEXT NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Seed default products if table is empty
            cursor.execute("SELECT COUNT(*) as cnt FROM products")
            if cursor.fetchone()['cnt'] == 0:
                insert_sql = "INSERT INTO products(name,category,price,stock,description) VALUES(%s,%s,%s,%s,%s)"
                cursor.executemany(insert_sql, DEFAULT_PRODUCTS)
            
            # Seed water wash services
            for service in WATER_WASH_SERVICES:
                cursor.execute("SELECT 1 FROM products WHERE name=%s AND category='Water Wash'", (service[0],))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO products(name,category,price,stock,description) VALUES(%s,%s,%s,%s,%s)", service)
            
            # Seed default coupons if table is empty
            cursor.execute("SELECT COUNT(*) as cnt FROM coupons")
            if cursor.fetchone()['cnt'] == 0:
                cursor.executemany("INSERT INTO coupons(code,discount,description,active) VALUES(%s,%s,%s,%s)",
                                 DEFAULT_COUPONS)
            
            # Seed default admin user if table is empty
            cursor.execute("SELECT COUNT(*) as cnt FROM users")
            if cursor.fetchone()['cnt'] == 0:
                cursor.execute("INSERT INTO users(username,password_hash,full_name,role,created_at) VALUES(%s,%s,%s,%s,%s)",
                             ("admin", hash_password("admin123"), "FIXXY Administrator", "admin",
                              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # Seed default settings
            for key, value in [("shop_name", "FIXXY Car Spares"),
                              ("gst_rate", "18"),
                              ("currency", "INR")]:
                cursor.execute("INSERT IGNORE INTO settings(`key`,`value`) VALUES(%s,%s)", (key, value))
            
            conn.commit()
        except MySQLError as e:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def query(self, sql, params=()):
        """Execute a SELECT query and return all results as list of dicts."""
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def one(self, sql, params=()):
        """Execute a SELECT query and return one result as dict or None."""
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, params)
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def execute(self, sql, params=()):
        """Execute an INSERT/UPDATE/DELETE query and return lastrowid."""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid
        except MySQLError:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def setting(self, key, default=""):
        """Get a setting value by key."""
        row = self.one("SELECT `value` FROM settings WHERE `key`=%s", (key,))
        return row["value"] if row else default

    def set_setting(self, key, value):
        """Set or update a setting value."""
        self.execute("INSERT INTO settings(`key`,`value`) VALUES(%s,%s) "
                    "ON DUPLICATE KEY UPDATE `value`=VALUES(`value`)", (key, str(value)))

class FixxyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FIXXY — Car Spare Parts & Billing System")
        self.geometry("1240x760")
        self.minsize(980, 650)
        self.configure(bg=BG)
        self.db = Database()
        self.user = None
        self.cart = {}
        self.vehicle = {"brand": "Toyota", "model": "Innova", "year": "2020"}
        self.coupon_code = ""
        self.coupon_discount = 0
        self.current_page = None
        self.last_bill_no = None
        self.payment_method = "UPI QR"
        self.favourites = set()
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure("Treeview", background=PANEL, foreground=TEXT,
                             fieldbackground=PANEL, rowheight=29, borderwidth=0)
        self.style.configure("Treeview.Heading", background=PANEL2, foreground=TEXT,
                             font=("Segoe UI", 10, "bold"), relief="flat")
        self.style.map("Treeview", background=[("selected", ORANGE)], foreground=[("selected", "white")])
        self.style.configure("TCombobox", fieldbackground=FIELD, background=FIELD, foreground=TEXT)
        self.show_login()

    def clear(self):
        for child in self.winfo_children():
            child.destroy()

    def label(self, parent, text, size=10, bold=False, color=TEXT, **kwargs):
        return tk.Label(parent, text=text, bg=kwargs.pop("bg", parent.cget("bg")),
                        fg=color, font=("Segoe UI", size, "bold" if bold else "normal"),
                        **kwargs)

    def button(self, parent, text, command, primary=False, **kwargs):
        return tk.Button(parent, text=text, command=command,
                         bg=ORANGE if primary else PANEL2,
                         fg="white", activebackground=ORANGE_HOVER,
                         activeforeground="white", relief="flat", bd=0,
                         padx=14, pady=8, cursor="hand2",
                         font=("Segoe UI", 10, "bold" if primary else "normal"),
                         **kwargs)

    def entry(self, parent, variable=None, show=None, width=28):
        e = tk.Entry(parent, textvariable=variable, show=show, width=width,
                     bg=FIELD, fg=TEXT, insertbackground=TEXT, relief="flat",
                     font=("Segoe UI", 11), highlightthickness=1,
                     highlightbackground=PANEL2, highlightcolor=ORANGE)
        return e

    def draw_brand(self, parent, size=24, bg=None):
        """Compact FIXXY brand mark: tyre ring plus orange lightning bolt."""
        bg = bg or parent.cget("bg")
        holder = tk.Frame(parent, bg=bg)
        mark = tk.Canvas(holder, width=size+18, height=size+18, bg=bg, highlightthickness=0)
        mark.pack(side="left")
        mark.create_oval(4, 4, size+14, size+14, outline=ORANGE, width=max(2, size//10))
        mark.create_oval(9, 9, size+9, size+9, outline="#8aa6bb", width=1)
        mark.create_polygon(size*.62+3, 5, size*.37+7, size*.56+3,
                            size*.53+7, size*.56+3, size*.39+9, size+10,
                            size*.72+8, size*.43+5, size*.56+8, size*.43+5,
                            fill=ORANGE, outline="")
        tk.Label(holder, text="FIXXY", bg=bg, fg=ORANGE,
                 font=("Segoe UI", max(15, int(size*.9)), "bold")).pack(side="left", padx=(7,0))
        return holder

    def draw_hero_car(self, canvas):
        """Draw a stylized pseudo-3D sports car with native Tkinter shapes."""
        canvas.delete("all")
        canvas.configure(bg="#081c30")
        w=max(canvas.winfo_width(), 500); h=max(canvas.winfo_height(), 230)
        # studio glow and floor
        canvas.create_oval(w*.49, h*.12, w*.96, h*.88, fill="#0d3553", outline="")
        canvas.create_line(w*.08,h*.82,w*.95,h*.82,fill="#244b68",width=2)
        # shadow
        canvas.create_oval(w*.19,h*.66,w*.84,h*.91,fill="#04111e",outline="")
        # Low, sculpted Pagani-inspired hypercar silhouette; original artwork, not a logo copy.
        body=[(w*.10,h*.64),(w*.16,h*.55),(w*.28,h*.51),(w*.37,h*.42),
              (w*.46,h*.34),(w*.64,h*.35),(w*.73,h*.45),(w*.83,h*.50),
              (w*.94,h*.58),(w*.96,h*.65),(w*.90,h*.70),(w*.19,h*.70)]
        canvas.create_polygon(body,fill="#d84b20",outline="#ff9d59",width=3,smooth=True)
        # glass canopy and roof line
        canvas.create_polygon([(w*.34,h*.49),(w*.46,h*.37),(w*.62,h*.38),(w*.71,h*.47)],
                              fill="#163d59",outline="#b5e8ff",width=2)
        canvas.create_line(w*.49,h*.38,w*.52,h*.49,fill="#78bad9",width=2)
        canvas.create_line(w*.38,h*.50,w*.74,h*.50,fill="#ffbd83",width=2)
        # aerodynamic front splitter, rear wing and side intake
        canvas.create_polygon([(w*.09,h*.65),(w*.22,h*.68),(w*.30,h*.68),(w*.12,h*.71)],fill="#d5e0e8",outline="#ffffff")
        canvas.create_line(w*.20,h*.47,w*.28,h*.47,fill="#f5f7fa",width=3)
        canvas.create_line(w*.20,h*.45,w*.28,h*.45,fill="#f5f7fa",width=2)
        canvas.create_polygon([(w*.72,h*.47),(w*.82,h*.48),(w*.79,h*.53),(w*.71,h*.52)],fill="#101e2a",outline="#ffb47b",width=1)
        canvas.create_line(w*.79,h*.43,w*.87,h*.42,fill="#d5e0e8",width=3)
        canvas.create_line(w*.82,h*.42,w*.82,h*.48,fill="#d5e0e8",width=2)
        canvas.create_polygon([(w*.88,h*.56),(w*.94,h*.59),(w*.94,h*.62),(w*.88,h*.61)],fill="#fff0b2",outline="")
        canvas.create_polygon([(w*.13,h*.59),(w*.22,h*.57),(w*.23,h*.61),(w*.12,h*.63)],fill="#ffdf8a",outline="")
        canvas.create_line(w*.30,h*.64,w*.77,h*.64,fill="#ffbd83",width=2)
        for cx in (w*.32,w*.75):
            cy=h*.69; r=h*.13
            canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill="#07121d",outline="#b8c8d4",width=3)
            canvas.create_oval(cx-r*.58,cy-r*.58,cx+r*.58,cy+r*.58,fill="#7e93a4",outline="#f4f7fa",width=2)
            canvas.create_oval(cx-r*.18,cy-r*.18,cx+r*.18,cy+r*.18,fill=ORANGE,outline="")
        canvas.create_text(w*.08,h*.15,text="BUILT FOR THE ROAD",anchor="w",fill="#8eacc2",font=("Segoe UI",9,"bold"))
        canvas.create_text(w*.08,h*.25,text="YOUR RIDE.\nYOUR RULES.",anchor="w",fill=TEXT,font=("Segoe UI",17,"bold"),justify="left")

    def show_login(self):
        self.clear()
        self.configure(bg=BG)
        wrap = tk.Frame(self, bg=BG)
        wrap.pack(fill="both", expand=True)
        left = tk.Frame(wrap, bg=BG, padx=55, pady=40)
        left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(wrap, bg=PANEL, padx=35, pady=35)
        right.pack(side="right", fill="both", expand=True)
        self.draw_brand(left, 34, BG).pack(anchor="w", pady=(28, 4))
        self.label(left, TAGLINE, 13, True).pack(anchor="w")
        # Pagani-inspired hypercar artwork on the first/login screen (original illustration).
        car = tk.Canvas(left, height=245, bg=BG, highlightthickness=0)
        car.pack(fill="x", pady=(8, 0))
        self.draw_hero_car(car)
        car.bind("<Configure>", lambda _e: self.draw_hero_car(car))
        self.label(left, "CAR SPARE PARTS & BILLING SYSTEM", 18, True).pack(anchor="w", pady=(6, 5))
        self.label(left, "Find quality parts. Manage orders. Track expenditure.", 10, False, MUTED).pack(anchor="w")
        self.label(right, "Welcome back", 24, True).pack(anchor="w", pady=(45, 5))
        self.label(right, "Sign in to continue to your workspace", 10, False, MUTED).pack(anchor="w", pady=(0, 25))
        self.login_user = tk.StringVar()
        self.login_pass = tk.StringVar()
        self.label(right, "USERNAME", 9, True, MUTED).pack(anchor="w", pady=(8, 5))
        eu = self.entry(right, self.login_user); eu.pack(fill="x", ipady=8)
        self.label(right, "PASSWORD", 9, True, MUTED).pack(anchor="w", pady=(16, 5))
        ep = self.entry(right, self.login_pass, show="●"); ep.pack(fill="x", ipady=8)
        ep.bind("<Return>", lambda _e: self.login())
        self.button(right, "LOGIN  →", self.login, True).pack(fill="x", pady=(25, 10))
        self.button(right, "Create a new customer account", self.show_signup).pack(fill="x")
        self.label(right, "Demo: admin / admin123", 9, False, MUTED).pack(anchor="w", pady=(22, 0))
        self.label(right, "School project demonstration database", 8, False, MUTED).pack(anchor="w", pady=(8, 0))

    def login(self):
        username, password = self.login_user.get().strip(), self.login_pass.get()
        row = self.db.one("SELECT * FROM users WHERE LOWER(username)=LOWER(%s)", (username,))
        if not row or not verify_password(password, row["password_hash"]):
            messagebox.showerror("Login failed", "Incorrect username or password.")
            return
        self.user = dict(row)
        self.cart = {}
        self.coupon_code = ""
        self.coupon_discount = 0
        self.show_shell("Dashboard")

    def show_signup(self):
        self.clear()
        frame = tk.Frame(self, bg=BG, padx=70, pady=35)
        frame.pack(fill="both", expand=True)
        self.label(frame, "CREATE YOUR FIXXY ACCOUNT", 23, True, ORANGE).pack(anchor="w", pady=(20, 20))
        self.signup_vars = {k: tk.StringVar() for k in ("name", "username", "password", "confirm")}
        for key, caption in [("name", "Full name"), ("username", "Username"),
                             ("password", "Password"), ("confirm", "Confirm password")]:
            self.label(frame, caption, 10, True, MUTED).pack(anchor="w", pady=(8, 4))
            self.entry(frame, self.signup_vars[key], show="●" if key in ("password", "confirm") else None).pack(anchor="w", fill="x", ipady=7)
        self.button(frame, "CREATE ACCOUNT", self.register, True).pack(anchor="w", pady=22)
        self.button(frame, "← Back to login", self.show_login).pack(anchor="w")

    def register(self):
        v = {k: x.get().strip() for k, x in self.signup_vars.items()}
        if not v["name"] or not v["username"] or not v["password"]:
            messagebox.showwarning("Missing details", "Please complete all fields.")
            return
        if len(v["username"]) < 3 or len(v["password"]) < 6:
            messagebox.showwarning("Requirements", "Username must be 3+ characters and password 6+ characters.")
            return
        if v["password"] != v["confirm"]:
            messagebox.showwarning("Password mismatch", "The passwords do not match.")
            return
        try:
            self.db.execute("INSERT INTO users(username,password_hash,full_name,role,created_at) VALUES(%s,%s,%s,%s,%s)",
                            (v["username"], hash_password(v["password"]), v["name"], "customer",
                             datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        except MySQLError as e:
            if e.errno == 1062:  # Duplicate entry
                messagebox.showerror("Username unavailable", "Choose a different username.")
            else:
                messagebox.showerror("Registration error", str(e))
            return
        messagebox.showinfo("Account created", "Your account is ready. Please log in.")
        self.show_login()

    def show_shell(self, page):
        self.current_page = page
        self.clear()
        root = tk.Frame(self, bg=BG)
        root.pack(fill="both", expand=True)
        sidebar = tk.Frame(root, bg="#061526", width=205, padx=12, pady=15)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        self.draw_brand(sidebar, 24, "#061526").pack(anchor="w", padx=3, pady=(8, 2))
        self.label(sidebar, "CAR CARE • PARTS • SERVICE", 7, True, MUTED, bg="#061526").pack(anchor="w", padx=8, pady=(0, 24))
        nav = [("⌂", "Dashboard"), ("⌕", "Find Parts"), ("▣", "Cart & Billing"),
               ("✦", "Water Wash"), ("▤", "Payment Details")]
        for icon, name in nav:
            active = page == name or (page == "Payment Details" and name == "Payment Details")
            self.button(sidebar, f"{icon}   {name}", lambda n=name: self.navigate(n),
                        primary=active).pack(fill="x", pady=3)
        if self.user["role"] == "admin":
            self.label(sidebar, "ADMIN TOOLS", 8, True, MUTED, bg="#061526").pack(anchor="w", padx=8, pady=(18, 5))
            self.button(sidebar, "⚙   Manage Stock", lambda: self.show_shell("Manage Stock")).pack(fill="x", pady=3)
            self.button(sidebar, "✂   Coupons", lambda: self.show_shell("Coupons")).pack(fill="x", pady=3)
        spacer = tk.Frame(sidebar, bg="#061526"); spacer.pack(fill="both", expand=True)
        self.button(sidebar, "⚙   Settings", lambda: self.show_shell("Settings")).pack(fill="x", pady=3)
        self.button(sidebar, "↪   Logout", self.logout).pack(fill="x", pady=3)
        main = tk.Frame(root, bg=BG, padx=22, pady=18)
        main.pack(side="left", fill="both", expand=True)
        top = tk.Frame(main, bg=BG)
        top.pack(fill="x", pady=(0, 18))
        self.label(top, page.upper(), 17, True).pack(side="left")
        self.label(top, f"●  {self.user['full_name']}  ", 10, True, MUTED).pack(side="right")
        content = tk.Frame(main, bg=BG)
        content.pack(fill="both", expand=True)
        routes = {
            "Dashboard": self.page_dashboard, "Find Parts": self.page_catalog,
            "Cart & Billing": self.page_cart, "Payment Details": self.page_checkout,
            "Water Wash": self.page_water_wash, "Manage Stock": self.page_stock,
            "Coupons": self.page_coupons, "Settings": self.page_settings
        }
        routes.get(page, self.page_dashboard)(content)

    def navigate(self, page):
        self.show_shell(page)

    def logout(self):
        self.user = None
        self.cart = {}
        self.show_login()

    def card(self, parent, title, value, subtitle="", color=ORANGE):
        f = tk.Frame(parent, bg=PANEL, padx=17, pady=14)
        self.label(f, title, 10, True, MUTED, bg=PANEL).pack(anchor="w")
        self.label(f, value, 22, True, color, bg=PANEL).pack(anchor="w", pady=(8, 3))
        self.label(f, subtitle, 9, False, MUTED, bg=PANEL).pack(anchor="w")
        return f

    def page_dashboard(self, parent):
        self.label(parent, f"Welcome to FIXXY, {self.user['full_name'].split()[0]}!", 22, True).pack(anchor="w")
        self.label(parent, "One sleek place for car parts, water wash and billing.", 10, False, MUTED).pack(anchor="w", pady=(2, 12))
        hero=tk.Canvas(parent,height=255,bg="#081c30",highlightthickness=0)
        hero.pack(fill="x",pady=(0,14))
        self.draw_hero_car(hero)
        hero.bind("<Configure>",lambda _e:self.draw_hero_car(hero))
        row=tk.Frame(parent,bg=BG);row.pack(fill="x")
        count=self.db.one("SELECT COUNT(*) n FROM products WHERE category!='Water Wash'")["n"]
        stock=self.db.one("SELECT COALESCE(SUM(stock),0) n FROM products WHERE category!='Water Wash'")["n"]
        services=self.db.one("SELECT COUNT(*) n FROM products WHERE category='Water Wash'")["n"]
        for t,v,sub,c in [("Spare Parts",str(count),"Browse the catalogue",ORANGE),
                          ("Units Available",str(stock),"Current parts stock",GREEN),
                          ("Wash Packages",str(services),"Care for your car","#70b9ff")]:
            self.card(row,t,v,sub,c).pack(side="left",fill="x",expand=True,padx=(0,10))
        actions=tk.Frame(parent,bg=BG);actions.pack(fill="x",pady=14)
        for title,desc,page in [("Find Parts","Visual spare-parts catalogue","Find Parts"),
                                ("Cart & Billing","Manage items and see ₹ total","Cart & Billing"),
                                ("Water Wash","Foam wash, full clean and more","Water Wash"),
                                ("Payment Details","UPI QR, card or cash","Payment Details")]:
            box=tk.Frame(actions,bg=PANEL,padx=12,pady=12)
            box.pack(side="left",fill="both",expand=True,padx=(0,8))
            self.label(box,title,11,True,ORANGE,bg=PANEL).pack(anchor="w")
            self.label(box,desc,8,False,MUTED,bg=PANEL,wraplength=140,justify="left").pack(anchor="w",pady=7)
            self.button(box,"Open →",lambda p=page:self.navigate(p),True).pack(anchor="w")

    def page_catalog(self, parent):
        self.label(parent, "Explore the parts universe", 21, True, ORANGE).pack(anchor="w")
        self.label(parent, "All available parts load automatically • search is optional", 10, False, MUTED).pack(anchor="w", pady=(2, 12))
        bar = tk.Frame(parent, bg=BG); bar.pack(fill="x", pady=(0, 12))
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="All Categories")
        search = self.entry(bar, self.search_var, width=28); search.pack(side="left", ipady=7)
        search.bind("<Return>", lambda _e: self.refresh_catalog())
        cats = ["All Categories"] + sorted({r["category"] for r in self.db.query("SELECT DISTINCT category FROM products WHERE category!='Water Wash'")})
        ttk.Combobox(bar, textvariable=self.category_var, values=cats, state="readonly", width=18).pack(side="left", padx=8, ipady=5)
        self.button(bar, "⌕  Search", self.refresh_catalog, True).pack(side="left")
        self.button(bar, "Clear", lambda: (self.search_var.set(""), self.category_var.set("All Categories"), self.refresh_catalog())).pack(side="left", padx=7)
        self.favourites_only = getattr(self, "favourites_only", False)
        self.button(bar, "★ Favourites Only" if self.favourites_only else "☆ Show Favourites",
                    self.toggle_favourites_filter).pack(side="right", padx=4)
        outer = tk.Frame(parent, bg=BG); outer.pack(fill="both", expand=True)
        self.catalog_canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        scroll = ttk.Scrollbar(outer, orient="vertical", command=self.catalog_canvas.yview)
        self.catalog_canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y"); self.catalog_canvas.pack(side="left", fill="both", expand=True)
        self.catalog_inner = tk.Frame(self.catalog_canvas, bg=BG)
        self.catalog_window = self.catalog_canvas.create_window((0, 0), window=self.catalog_inner, anchor="nw")
        self.catalog_inner.bind("<Configure>", lambda _e: self.catalog_canvas.configure(scrollregion=self.catalog_canvas.bbox("all")))
        self.catalog_canvas.bind("<Configure>", lambda e: self.catalog_canvas.itemconfigure(self.catalog_window, width=e.width))
        def _wheel(event):
            if self.catalog_canvas.winfo_exists():
                delta = event.delta
                if delta == 0:
                    return
                self.catalog_canvas.yview_scroll(-1 if delta > 0 else 1, "units")
        self.catalog_canvas.bind("<Enter>", lambda _e: self.catalog_canvas.bind_all("<MouseWheel>", _wheel))
        self.catalog_canvas.bind("<Leave>", lambda _e: self.catalog_canvas.unbind_all("<MouseWheel>"))
        self.refresh_catalog()

    def page_water_wash(self, parent):
        self.label(parent,"Water Wash Studio",22,True,ORANGE).pack(anchor="w")
        self.label(parent,"Choose a car-care package. Prices are in Indian rupees (₹).",10,False,MUTED).pack(anchor="w",pady=(2,14))
        hero=tk.Canvas(parent,height=115,bg="#0b2942",highlightthickness=0)
        hero.pack(fill="x",pady=(0,14))
        hero.create_text(24,25,text="WATER • FOAM • SHINE",anchor="w",fill=ORANGE,font=("Segoe UI",15,"bold"))
        hero.create_text(24,60,text="A fresh finish for every drive.",anchor="w",fill=TEXT,font=("Segoe UI",11))
        hero.create_oval(600,12,740,120,outline="#70b9ff",width=3)
        hero.create_arc(615,27,725,105,start=20,extent=140,style="arc",outline="#d8f2ff",width=4)
        hero.create_text(670,66,text="✦",fill=ORANGE,font=("Segoe UI",28,"bold"))
        wrap=tk.Frame(parent,bg=BG);wrap.pack(fill="both",expand=True)
        for col in range(2): wrap.grid_columnconfigure(col,weight=1,uniform="wash")
        services=self.db.query("SELECT * FROM products WHERE category='Water Wash' ORDER BY price")
        icons={"Full Clean":"🚘","Foam Wash":"✧","Premium Foam + Wax":"✦","Interior Deep Clean":"◈"}
        for i,p in enumerate(services):
            r,c=divmod(i,2)
            card=tk.Frame(wrap,bg=PANEL,padx=18,pady=15,highlightthickness=1,highlightbackground="#244b68")
            card.grid(row=r,column=c,sticky="nsew",padx=7,pady=7)
            art=tk.Canvas(card,height=76,bg="#102d46",highlightthickness=0);art.pack(fill="x",pady=(0,8))
            art.create_oval(art.winfo_reqwidth()//2-28,5,art.winfo_reqwidth()//2+28,61,fill="#183f5d",outline="#367095",width=2)
            art.create_text(art.winfo_reqwidth()//2,33,text=icons.get(p["name"],"✦"),fill=ORANGE,font=("Segoe UI",27,"bold"))
            self.label(card,p["name"],14,True,TEXT,bg=PANEL).pack(anchor="w")
            self.label(card,p["description"],9,False,MUTED,bg=PANEL,wraplength=420,justify="left").pack(anchor="w",pady=(5,9))
            self.label(card,money(p["price"]),19,True,ORANGE,bg=PANEL).pack(anchor="w")
            self.button(card,"＋ Add package to cart",lambda pid=p["id"]:self.add_product_to_cart(pid),True).pack(anchor="w",pady=(10,0))
        self.button(parent,"View Cart & Billing →",lambda:self.navigate("Cart & Billing"),True).pack(anchor="e",pady=(10,0))

    def draw_part_art(self, canvas, product):
        """Draw a small, offline part illustration using Tkinter Canvas (no image packages)."""
        name = product["name"].lower()
        category = product["category"].lower()
        canvas.delete("all")
        canvas.configure(bg="#102d46")
        canvas.create_oval(18, 12, 128, 122, fill="#163b59", outline="#255675", width=2)
        accent = ORANGE
        if "filter" in name:
            canvas.create_rectangle(48, 36, 96, 94, fill="#d8e2ea", outline="#f8fbff", width=2)
            for y in range(42, 91, 8):
                canvas.create_line(52, y, 92, y, fill="#71889a", width=2)
            canvas.create_oval(58, 25, 86, 39, fill="#ff9b43", outline="")
        elif "brake" in name or "rotor" in name or "bearing" in name:
            canvas.create_oval(35, 27, 111, 103, fill="#aebdca", outline="#e9f0f5", width=3)
            canvas.create_oval(53, 45, 93, 85, fill="#102d46", outline="#ff9b43", width=3)
            for x, y in [(73,34),(42,65),(103,65),(73,96)]:
                canvas.create_oval(x-4,y-4,x+4,y+4,fill=ORANGE,outline="")
        elif "battery" in name:
            canvas.create_rectangle(35, 43, 111, 91, fill="#24394b", outline="#e8f0f6", width=2)
            canvas.create_rectangle(47, 34, 61, 44, fill="#c8d5df", outline="")
            canvas.create_rectangle(85, 34, 99, 44, fill="#c8d5df", outline="")
            canvas.create_text(58, 66, text="+", fill="#ff6868", font=("Segoe UI", 20, "bold"))
            canvas.create_text(87, 66, text="−", fill="#70b9ff", font=("Segoe UI", 20, "bold"))
        elif "plug" in name:
            canvas.create_rectangle(60, 25, 86, 65, fill="#d9e3eb", outline="#ffffff", width=2)
            for y in range(32, 57, 6): canvas.create_line(60,y,86,y,fill="#7d8f9d",width=2)
            canvas.create_rectangle(65, 65, 81, 91, fill="#ffbd69", outline="")
            canvas.create_line(73, 91, 73, 103, fill="#e8f0f6", width=4)
        elif "belt" in name:
            canvas.create_oval(32, 28, 114, 104, outline="#f28b35", width=12)
            canvas.create_oval(51, 47, 95, 85, outline="#536b7d", width=6)
        elif "bulb" in name or "headlight" in name:
            canvas.create_oval(48, 25, 98, 75, fill="#fff0b0", outline="#ffca62", width=3)
            canvas.create_rectangle(61, 72, 85, 98, fill="#aebdca", outline="")
            for x,y in [(44,30),(101,31),(40,58),(104,59)]:
                canvas.create_line(73,50,x,y,fill="#ffca62",width=2)
        elif "pump" in name:
            canvas.create_oval(42, 35, 104, 97, fill="#9eafbd", outline="#e6eef4", width=3)
            canvas.create_oval(58, 51, 88, 81, fill="#102d46", outline=ORANGE, width=4)
            canvas.create_rectangle(70, 23, 78, 37, fill="#dce6ed", outline="")
        elif "shock" in name:
            canvas.create_line(73, 25, 73, 104, fill="#c6d4df", width=8)
            for y in range(38, 91, 10):
                canvas.create_line(51,y,95,y+5,fill=ORANGE,width=4)
            canvas.create_oval(62, 17, 84, 34, fill="#c6d4df", outline="")
            canvas.create_oval(62, 96, 84, 113, fill="#c6d4df", outline="")
        elif "wiper" in name:
            canvas.create_line(37, 84, 103, 39, fill="#d9e5ee", width=8)
            canvas.create_line(32, 91, 108, 42, fill=ORANGE, width=3)
            canvas.create_oval(66, 58, 80, 72, fill="#aebdca", outline="")
        elif "radiator" in name:
            canvas.create_rectangle(39, 26, 107, 105, fill="#a8bbc9", outline="#edf4f8", width=3)
            for x in range(47, 103, 8): canvas.create_line(x, 34, x, 97, fill="#526f83", width=2)
        else:
            canvas.create_oval(43, 30, 103, 90, fill="#d1dce5", outline="#f7fafc", width=3)
            canvas.create_oval(59, 46, 87, 74, fill="#102d46", outline=ORANGE, width=3)
            canvas.create_line(73, 19, 73, 31, fill=ORANGE, width=4)
            canvas.create_line(73, 90, 73, 103, fill=ORANGE, width=4)
        canvas.create_text(73, 119, text="FIXXY PART", fill="#91b7d1", font=("Segoe UI", 7, "bold"))

    def toggle_favourite(self, pid):
        if not hasattr(self, "favourites"):
            self.favourites = set()
        if pid in self.favourites:
            self.favourites.remove(pid)
        else:
            self.favourites.add(pid)
        self.refresh_catalog()

    def toggle_favourites_filter(self):
        self.favourites_only = not getattr(self, "favourites_only", False)
        self.refresh_catalog()

    def add_product_to_cart(self, pid):
        p = self.db.one("SELECT * FROM products WHERE id=%s", (pid,))
        if not p: return
        if p["category"] != "Water Wash" and p["stock"] < 1:
            messagebox.showwarning("Out of stock", "This part is currently out of stock."); return
        self.cart[pid] = self.cart.get(pid, 0) + 1
        if p["category"] != "Water Wash" and self.cart[pid] > p["stock"]:
            self.cart[pid] = p["stock"]
            messagebox.showinfo("Stock limit", f"Maximum available quantity: {p['stock']}")
        self.coupon_code = ""; self.coupon_discount = 0
        messagebox.showinfo("Added to cart", f"{p['name']} added to your cart.")
    def refresh_catalog(self):
        if not hasattr(self, "catalog_inner") or not self.catalog_inner.winfo_exists():
            return
        for child in self.catalog_inner.winfo_children(): child.destroy()
        term = self.search_var.get().strip()
        category = self.category_var.get()
        sql = "SELECT * FROM products WHERE category!='Water Wash' AND (name LIKE ? OR category LIKE ? OR description LIKE ?)"
        params = [f"%{term}%", f"%{term}%", f"%{term}%"]
        if category != "All Categories":
            sql += " AND category=?"; params.append(category)
        sql += " ORDER BY category,name"
        products = self.db.query(sql, params)
        if getattr(self, "favourites_only", False):
            favourite_ids = getattr(self, "favourites", set())
            products = [p for p in products if p["id"] in favourite_ids]
        if not products:
            message = ("No favourite parts yet. Tap ☆ on a part to save it." 
                       if getattr(self, "favourites_only", False) else
                       "No parts match that filter. Clear the search to see every part.")
            self.label(self.catalog_inner, message, 13, True, MUTED,
                       wraplength=600, justify="left").pack(pady=40, anchor="w")
            self.catalog_canvas.configure(scrollregion=(0, 0, 0, 100))
            return
        for col in range(3):
            self.catalog_inner.grid_columnconfigure(col, weight=1, uniform="parts")
        for i, p in enumerate(products):
            r, c = divmod(i, 3)
            card = tk.Frame(self.catalog_inner, bg=PANEL, padx=12, pady=10,
                            highlightthickness=1, highlightbackground="#1d4665")
            card.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)
            art = tk.Canvas(card, width=190, height=145, bg="#102d46", highlightthickness=0)
            art.pack(fill="x", pady=(0, 10), expand=True)
            self.draw_part_art(art, p)
            top = tk.Frame(card, bg=PANEL); top.pack(fill="x")
            self.label(top, p["name"], 11, True, TEXT, bg=PANEL, wraplength=150, justify="left").pack(side="left", anchor="w")
            favs = getattr(self, "favourites", set())
            self.button(top, "★" if p["id"] in favs else "☆",
                        lambda pid=p["id"]: self.toggle_favourite(pid)).pack(side="right", padx=(4,0))
            self.label(card, p["category"].upper(), 8, True, "#70b9ff", bg=PANEL).pack(anchor="w", pady=(5,2))
            self.label(card, money(p["price"]), 16, True, ORANGE, bg=PANEL).pack(anchor="w")
            stock_color = RED if p["stock"] < 5 else GREEN
            stock_text = f"● {p['stock']} in stock" if p["stock"] else "● OUT OF STOCK"
            self.label(card, stock_text, 9, True, stock_color, bg=PANEL).pack(anchor="w", pady=(4,2))
            self.label(card, p["description"] or "Quality replacement component", 8, False, MUTED,
                       bg=PANEL, wraplength=175, justify="left").pack(anchor="w", pady=(2,8))
            row = tk.Frame(card, bg=PANEL); row.pack(fill="x")
            self.button(row, "＋ Add to Cart", lambda pid=p["id"]: self.add_product_to_cart(pid),
                        True, state="normal" if p["stock"] > 0 else "disabled").pack(side="left", fill="x", expand=True)
        self.catalog_canvas.configure(scrollregion=self.catalog_canvas.bbox("all"))

    def add_selected(self):
        selected = self.catalog_tree.selection()
        if not selected:
            messagebox.showwarning("Select a part", "Select a catalogue item first."); return
        try: qty = safe_int(self.qty_var.get())
        except ValueError as e: messagebox.showerror("Invalid quantity", str(e)); return
        if qty < 1:
            messagebox.showwarning("Invalid quantity", "Quantity must be at least 1."); return
        pid = int(selected[0])
        product = self.db.one("SELECT * FROM products WHERE id=%s", (pid,))
        current = self.cart.get(pid, 0)
        if current + qty > product["stock"]:
            messagebox.showwarning("Stock limit", f"Only {product['stock']} unit(s) are available."); return
        self.cart[pid] = current + qty
        self.coupon_code = ""; self.coupon_discount = 0
        messagebox.showinfo("Added", f"{product['name']} added to your cart.")
        self.refresh_catalog()

    def cart_lines(self):
        lines = []
        for pid, qty in list(self.cart.items()):
            p = self.db.one("SELECT * FROM products WHERE id=%s", (pid,))
            if not p:
                self.cart.pop(pid, None); continue
            lines.append({"id": pid, "name": p["name"], "category": p["category"],
                          "price": p["price"], "stock": p["stock"], "qty": qty,
                          "total": p["price"] * qty})
        return lines

    def totals(self):
        subtotal = sum(x["total"] for x in self.cart_lines())
        discount = subtotal * self.coupon_discount / 100
        taxable = max(0, subtotal - discount)
        gst = taxable * (float(self.db.setting("gst_rate", "18")) / 100)
        return subtotal, discount, gst, taxable + gst

    def page_cart(self, parent):
        self.label(parent,"Cart & Billing",22,True,ORANGE).pack(anchor="w",pady=(0,10))
        body=tk.Frame(parent,bg=BG);body.pack(fill="both",expand=True)
        left=tk.Frame(body,bg=BG);left.pack(side="left",fill="both",expand=True,padx=(0,12))
        right=tk.Frame(body,bg=PANEL,padx=16,pady=14);right.pack(side="right",fill="y")
        cols=("id","name","category","price","qty","total","stock")
        tree=ttk.Treeview(left,columns=cols,show="headings",height=8);self.cart_tree=tree
        for c,title,width in [("id","ID",35),("name","Item / Service",165),("category","Type",95),("price","Price (₹)",85),("qty","Qty",48),("total","Total (₹)",90),("stock","Stock",48)]:
            tree.heading(c,text=title);tree.column(c,width=width,anchor="w" if c in ("name","category") else "center")
        tree.pack(fill="both",expand=True)
        controls=tk.Frame(left,bg=BG);controls.pack(fill="x",pady=8)
        self.label(controls,"Qty:",9,True).pack(side="left")
        self.cart_qty_var=tk.StringVar(value="1");self.entry(controls,self.cart_qty_var,width=5).pack(side="left",padx=5,ipady=3)
        self.button(controls,"Set Qty",self.set_cart_quantity).pack(side="left")
        self.button(controls,"Remove",self.remove_cart_item).pack(side="left",padx=5)
        self.button(controls,"Empty Cart",self.empty_cart).pack(side="left")
        self.label(right,"CUSTOMER DETAILS",12,True,ORANGE,bg=PANEL).pack(anchor="w",pady=(0,7))
        defaults={"name":self.user["full_name"],"phone":"","address":"","brand":self.vehicle["brand"],"model":self.vehicle["model"],"year":self.vehicle["year"],"coupon":self.coupon_code,"payment":self.payment_method}
        previous=getattr(self,"checkout_vars",{})
        self.checkout_vars={k:tk.StringVar(value=(previous[k].get() if k in previous else v)) for k,v in defaults.items()}
        for key,caption in [("name","Customer name"),("phone","Phone number"),("address","Address"),("brand","Car brand"),("model","Car model"),("year","Car year")]:
            self.label(right,caption,8,True,MUTED,bg=PANEL).pack(anchor="w",pady=(5,2))
            self.entry(right,self.checkout_vars[key],width=27).pack(fill="x",ipady=3)
        self.label(right,"BILL SUMMARY",11,True,ORANGE,bg=PANEL).pack(anchor="w",pady=(12,5))
        self.cart_summary=self.label(right,"",10,True,TEXT,bg=PANEL,justify="left",wraplength=250);self.cart_summary.pack(anchor="w")
        couponrow=tk.Frame(right,bg=PANEL);couponrow.pack(fill="x",pady=(9,4))
        self.entry(couponrow,self.checkout_vars["coupon"],width=15).pack(side="left",fill="x",expand=True,ipady=4)
        self.button(couponrow,"Apply",self.apply_checkout_coupon).pack(side="left",padx=(5,0))
        self.button(right,"Choose Payment →",self.open_checkout,True).pack(fill="x",pady=(12,5))
        self.button(right,"Continue Shopping",lambda:self.navigate("Find Parts")).pack(fill="x")
        self.refresh_cart()

    def refresh_cart(self):
        if not hasattr(self,"cart_tree") or not self.cart_tree.winfo_exists(): return
        for i in self.cart_tree.get_children(): self.cart_tree.delete(i)
        for x in self.cart_lines():
            self.cart_tree.insert("","end",iid=str(x["id"]),values=(x["id"],x["name"],x["category"],
                f"{x['price']:,.2f}",x["qty"],f"{x['total']:,.2f}",x["stock"]))
        sub,disc,gst,total=self.totals()
        self.cart_summary.config(text=f"Subtotal  {money(sub)}\nDiscount  {money(disc)}\nGST  {money(gst)}\nGRAND TOTAL  {money(total)}")

    def selected_cart_id(self):
        selected=self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Select item","Select an item in the cart first."); return None
        return int(selected[0])

    def set_cart_quantity(self):
        pid=self.selected_cart_id()
        if pid is None:return
        try: qty=safe_int(self.cart_qty_var.get())
        except ValueError as e: messagebox.showerror("Invalid quantity",str(e));return
        if qty==0:self.cart.pop(pid,None)
        else:
            p=self.db.one("SELECT stock FROM products WHERE id=%s",(pid,))
            if not p or (p["category"] != "Water Wash" and qty>p["stock"]):
                messagebox.showwarning("Stock limit",f"Maximum available quantity: {p['stock'] if p else 0}");return
            self.cart[pid]=qty
        self.refresh_cart()

    def remove_cart_item(self):
        pid=self.selected_cart_id()
        if pid is not None:self.cart.pop(pid,None);self.refresh_cart()

    def empty_cart(self):
        if self.cart and messagebox.askyesno("Empty cart","Remove all items from the cart?"):
            self.cart.clear();self.coupon_code="";self.coupon_discount=0;self.refresh_cart()

    def open_checkout(self):
        if not self.cart_lines():
            messagebox.showwarning("Empty cart","Add at least one part before checkout.");return
        self.show_shell("Payment Details")

    def page_checkout(self,parent):
        self.label(parent,"Payment Details",22,True,ORANGE).pack(anchor="w")
        self.label(parent,"Choose how you would like to pay. This is a school-project demo; no real payment is processed.",10,False,MUTED).pack(anchor="w",pady=(3,15))
        if not hasattr(self, "checkout_vars"):
            defaults={"name":self.user["full_name"],"phone":"","address":"","brand":self.vehicle["brand"],"model":self.vehicle["model"],"year":self.vehicle["year"],"coupon":self.coupon_code,"payment":self.payment_method}
        previous=getattr(self,"checkout_vars",{})
        self.checkout_vars={k:tk.StringVar(value=(previous[k].get() if k in previous else v)) for k,v in defaults.items()}
        body=tk.Frame(parent,bg=BG);body.pack(fill="both",expand=True)
        left=tk.Frame(body,bg=PANEL,padx=20,pady=18);left.pack(side="left",fill="both",expand=True,padx=(0,12))
        right=tk.Frame(body,bg=PANEL,padx=20,pady=18,width=300);right.pack(side="right",fill="y")
        self.label(left,"SELECT PAYMENT METHOD",12,True,ORANGE,bg=PANEL).pack(anchor="w",pady=(0,12))
        if not hasattr(self,"payment_var"):
            self.payment_var=tk.StringVar(value=self.payment_method)
        else:
            self.payment_var.set(self.payment_method)
        methods=[("UPI QR","Scan QR using any UPI app"),("Debit / Credit Card","Card payment (demo only)"),("Cash on Delivery","Pay when the service or parts arrive")]
        for value,desc in methods:
            row=tk.Frame(left,bg="#123552",padx=12,pady=12);row.pack(fill="x",pady=5)
            tk.Radiobutton(row,text=value,variable=self.payment_var,value=value,bg="#123552",fg=TEXT,
                           selectcolor=FIELD,activebackground="#123552",activeforeground=TEXT,
                           font=("Segoe UI",11,"bold")).pack(anchor="w")
            self.label(row,desc,9,False,MUTED,bg="#123552").pack(anchor="w",padx=(26,0),pady=(3,0))
        self.payment_preview=tk.Frame(left,bg=PANEL,pady=12);self.payment_preview.pack(fill="both",expand=True)
        if not hasattr(self,"payment_trace_id"):
            self.payment_trace_id=self.payment_var.trace_add("write",lambda *_:self.refresh_payment_preview())
        self.refresh_payment_preview()
        self.label(right,"PAYMENT SUMMARY",12,True,ORANGE,bg=PANEL).pack(anchor="w",pady=(0,12))
        for x in self.cart_lines():
            self.label(right,f"{x['name']} × {x['qty']}",9,False,MUTED,bg=PANEL,wraplength=250).pack(anchor="w",pady=2)
            self.label(right,money(x["total"]),9,True,TEXT,bg=PANEL).pack(anchor="e")
        sub,disc,gst,total=self.totals()
        self.label(right,f"Subtotal: {money(sub)}",10,False,bg=PANEL).pack(anchor="w",pady=(14,3))
        self.label(right,f"Discount: {money(disc)}",10,False,bg=PANEL).pack(anchor="w",pady=3)
        self.label(right,f"GST: {money(gst)}",10,False,bg=PANEL).pack(anchor="w",pady=3)
        self.label(right,f"TOTAL TO PAY: {money(total)}",16,True,ORANGE,bg=PANEL).pack(anchor="w",pady=(12,18))
        self.button(right,"CONFIRM & GENERATE BILL",self.place_order,True).pack(fill="x",pady=(8,7))
        self.button(right,"← Back to Cart & Billing",lambda:self.navigate("Cart & Billing")).pack(fill="x")

    def refresh_payment_preview(self):
        if not hasattr(self,"payment_preview") or not self.payment_preview.winfo_exists(): return
        for child in self.payment_preview.winfo_children(): child.destroy()
        method=self.payment_var.get()
        if method=="UPI QR":
            self.label(self.payment_preview,"SCAN TO PAY (DEMO QR)",10,True,MUTED,bg=PANEL).pack(anchor="w",pady=(0,8))
            qr=tk.Canvas(self.payment_preview,width=154,height=154,bg="white",highlightthickness=0)
            qr.pack(anchor="w")
            # Decorative QR-like matrix only; it is not a working payment code.
            import random
            rng=random.Random(42)
            size=7; margin=8
            for r in range(19):
                for c in range(19):
                    if rng.random()>.53:
                        qr.create_rectangle(margin+c*size,margin+r*size,margin+(c+1)*size,margin+(r+1)*size,fill="#102030",outline="")
            for x,y in [(8,8),(92,8),(8,92)]:
                qr.create_rectangle(x,y,x+35,y+35,fill="white",outline="#102030",width=3)
                qr.create_rectangle(x+7,y+7,x+28,y+28,fill="#102030",outline="")
            self.label(self.payment_preview,"Illustration only — no real transaction will occur.",9,False,MUTED,bg=PANEL).pack(anchor="w",pady=7)
        elif method=="Debit / Credit Card":
            self.label(self.payment_preview,"CARD PAYMENT (DEMO)",10,True,MUTED,bg=PANEL).pack(anchor="w",pady=(0,8))
            self.label(self.payment_preview,"Cardholder name",9,True,MUTED,bg=PANEL).pack(anchor="w")
            self.card_name=self.entry(self.payment_preview,width=32);self.card_name.pack(anchor="w",fill="x",ipady=5,pady=(2,7))
            self.label(self.payment_preview,"Card number (demo only)",9,True,MUTED,bg=PANEL).pack(anchor="w")
            self.card_number=self.entry(self.payment_preview,width=32);self.card_number.pack(anchor="w",fill="x",ipady=5,pady=(2,7))
            self.label(self.payment_preview,"Do not enter real card information. The form does not process payments.",9,False,"#ffb0a8",bg=PANEL,wraplength=480,justify="left").pack(anchor="w",pady=4)
        else:
            self.label(self.payment_preview,"CASH ON DELIVERY",12,True,ORANGE,bg=PANEL).pack(anchor="w",pady=(15,5))
            self.label(self.payment_preview,"Pay the displayed total when your order arrives or the wash service is completed.",10,False,MUTED,bg=PANEL,wraplength=480,justify="left").pack(anchor="w")

    def apply_checkout_coupon(self):
        code=self.checkout_vars["coupon"].get().strip().upper()
        row=self.db.one("SELECT * FROM coupons WHERE UPPER(code)=%s AND active=1",(code,))
        if not row:
            messagebox.showwarning("Invalid coupon","This coupon is not valid or is inactive.");return
        self.coupon_code=row["code"];self.coupon_discount=float(row["discount"])
        if hasattr(self,"cart_summary") and self.cart_summary.winfo_exists(): self.refresh_cart()
        messagebox.showinfo("Coupon applied",f"{self.coupon_discount:g}% discount applied to the bill.")

    def place_order(self):
        if not self.cart_lines():
            messagebox.showwarning("Empty cart","Add a part or water-wash package before confirming payment.");return
        v={k:x.get().strip() for k,x in self.checkout_vars.items()}
        if hasattr(self,"payment_var"):
            v["payment"] = self.payment_var.get()
        self.payment_method = v["payment"]
        if not v["name"] or not v["phone"] or not v["address"]:
            messagebox.showwarning("Missing details","Enter customer name, phone and address.");return
        if len("".join(c for c in v["phone"] if c.isdigit()))<10:
            messagebox.showwarning("Phone number","Enter a valid phone number with at least 10 digits.");return
        lines=self.cart_lines()
        if not lines:messagebox.showwarning("Empty cart","Your cart is empty.");return
        sub,disc,gst,total=self.totals()
        bill_no="FX"+datetime.now().strftime("%y%m%d%H%M%S")+secrets.token_hex(2).upper()
        stamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Use transaction for checkout
        conn = self.db.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            # Check stock availability
            for x in lines:
                cursor.execute("SELECT stock FROM products WHERE id=%s", (x["id"],))
                stock = cursor.fetchone()
                if not stock or (x["category"] != "Water Wash" and stock["stock"] < x["qty"]):
                    raise ValueError(f"Insufficient stock for {x['name']}. Please review your cart.")
            
            # Insert order
            cursor.execute("""INSERT INTO orders(bill_no,user_id,customer_name,phone,address,car_brand,car_model,car_year,
                subtotal,discount,gst,grand_total,coupon_code,payment_method,created_at)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (bill_no,self.user["id"],v["name"],v["phone"],v["address"],v["brand"],v["model"],v["year"],
                 sub,disc,gst,total,self.coupon_code,v["payment"],stamp))
            oid = cursor.lastrowid
            
            # Insert order items and update stock
            for x in lines:
                cursor.execute("""INSERT INTO order_items(order_id,product_id,product_name,category,price,quantity,total)
                    VALUES(%s,%s,%s,%s,%s,%s,%s)""",(oid,x["id"],x["name"],x["category"],x["price"],x["qty"],x["total"]))
                if x["category"] == "Water Wash":
                    cursor.execute("UPDATE products SET sold=sold+%s WHERE id=%s",(x["qty"],x["id"]))
                else:
                    cursor.execute("UPDATE products SET stock=stock-%s,sold=sold+%s WHERE id=%s",(x["qty"],x["qty"],x["id"]))
            
            conn.commit()
        except (MySQLError, ValueError) as e:
            conn.rollback()
            messagebox.showerror("Order not placed",str(e))
            return
        finally:
            cursor.close()
            conn.close()
        
        self.last_bill_no=bill_no
        self.cart.clear();self.coupon_code="";self.coupon_discount=0
        self.show_bill(oid)

    def show_bill(self, order_id):
        order=self.db.one("SELECT * FROM orders WHERE id=%s",(order_id,))
        items=self.db.query("SELECT * FROM order_items WHERE order_id=%s",(order_id,))
        win=tk.Toplevel(self);win.title(f"FIXXY Bill — {order['bill_no']}");win.geometry("850x650");win.configure(bg=BG)
        top=tk.Frame(win,bg=PANEL,padx=18,pady=12);top.pack(fill="x")
        self.draw_brand(top,22,PANEL).pack(side="left")
        self.label(top,"CAR SPARE PARTS & BILLING SYSTEM",10,True,bg=PANEL).pack(side="right")
        text=tk.Text(win,bg="#ffffff",fg="#172333",font=("Consolas",10),wrap="word",padx=20,pady=18)
        text.pack(fill="both",expand=True,padx=15,pady=12)
        text.insert("end",f"FIXXY — CAR SPARE PARTS & BILLING SYSTEM\n")
        text.insert("end","="*78+"\n")
        created_at_str = str(order['created_at']) if isinstance(order['created_at'], datetime) else order['created_at']
        text.insert("end",f"Bill No: {order['bill_no']}     Date: {created_at_str}\n")
        text.insert("end","-"*78+"\n")
        text.insert("end",f"Customer: {order['customer_name']}\nPhone: {order['phone']}\nAddress: {order['address']}\n")
        text.insert("end",f"Vehicle: {order['car_brand']} {order['car_model']} ({order['car_year']})\n")
        text.insert("end","-"*78+"\n")
        text.insert("end",f"{'S.No':<6}{'Item / Service':<27}{'Category':<16}{'Qty':>5}{'Price':>11}{'Total':>13}\n")
        text.insert("end","-"*78+"\n")
        for i,x in enumerate(items,1):
            text.insert("end",f"{i:<6}{x['product_name'][:26]:<27}{x['category'][:15]:<16}{x['quantity']:>5}{float(x['price']):>11.2f}{float(x['total']):>13.2f}\n")
        text.insert("end","-"*78+"\n")
        text.insert("end",f"{'Subtotal':>62} {money(order['subtotal']):>14}\n")
        text.insert("end",f"{'Discount':>62} {money(order['discount']):>14}\n")
        text.insert("end",f"{'GST':>62} {money(order['gst']):>14}\n")
        text.insert("end",f"{'GRAND TOTAL':>62} {money(order['grand_total']):>14}\n")
        text.insert("end",f"\nPayment method: {order['payment_method']}\n")
        text.insert("end","Thank you for choosing FIXXY!\n")
        text.config(state="disabled")
        buttons=tk.Frame(win,bg=BG);buttons.pack(fill="x",padx=15,pady=(0,12))
        self.button(buttons,"Save Bill / Export",lambda:self.export_bill(order_id),True).pack(side="left")
        self.button(buttons,"Print",lambda:self.print_bill(order_id)).pack(side="left",padx=8)
        self.button(buttons,"Close",win.destroy).pack(side="right")

    def bill_html(self, order_id):
        o=self.db.one("SELECT * FROM orders WHERE id=%s",(order_id,))
        items=self.db.query("SELECT * FROM order_items WHERE order_id=%s",(order_id,))
        rows="".join(f"<tr><td>{html.escape(x['product_name'])}</td><td>{html.escape(x['category'])}</td><td>{x['quantity']}</td><td>{money(x['price'])}</td><td>{money(x['total'])}</td></tr>" for x in items)
        created_at_str = str(o['created_at']) if isinstance(o['created_at'], datetime) else o['created_at']
        return f"""<!doctype html><html><head><meta charset="utf-8"><title>FIXXY {o['bill_no']}</title>
        <style>body{{font:15px Arial;margin:40px;color:#172333}}h1{{color:#f47718}}table{{width:100%;border-collapse:collapse;margin-top:24px}}
        th,td{{padding:10px;border:1px solid #ccd5df;text-align:left}}th{{background:#102c47;color:white}}.tot{{text-align:right;margin-top:22px;line-height:1.9}}
        @media print{{button{{display:none}}}}</style></head><body><h1>⚙ FIXXY</h1><h3>Car Spare Parts & Billing System</h3>
        <p><b>Bill No:</b> {html.escape(o['bill_no'])} &nbsp; <b>Date:</b> {html.escape(created_at_str)}</p>
        <p><b>Customer:</b> {html.escape(o['customer_name'])}<br><b>Phone:</b> {html.escape(o['phone'])}<br>
        <b>Address:</b> {html.escape(o['address'])}<br><b>Vehicle:</b> {html.escape(o['car_brand'])} {html.escape(o['car_model'])} ({html.escape(o['car_year'])})</p>
        <table><thead><tr><th>Part</th><th>Category</th><th>Qty</th><th>Price</th><th>Total</th></tr></thead><tbody>{rows}</tbody></table>
        <div class="tot">Subtotal: {money(o['subtotal'])}<br>Discount: {money(o['discount'])}<br>GST: {money(o['gst'])}<br>
        <h2>Grand Total: {money(o['grand_total'])}</h2>Payment: {html.escape(o['payment_method'])}</div>
        <p>Thank you for choosing FIXXY!</p><button onclick="window.print()">Print this bill</button></body></html>"""

    def export_bill(self, order_id):
        path=filedialog.asksaveasfilename(defaultextension=".html",filetypes=[("HTML bill (print to PDF)","*.html"),("Text file","*.txt")],
                                          initialfile=f"FIXXY_{self.db.one('SELECT bill_no FROM orders WHERE id=%s',(order_id,))['bill_no']}")
        if not path:return
        try:
            if path.lower().endswith(".txt"):
                o=self.db.one("SELECT * FROM orders WHERE id=%s",(order_id,))
                items=self.db.query("SELECT * FROM order_items WHERE order_id=%s",(order_id,))
                with open(path,"w",encoding="utf-8") as f:
                    f.write(f"FIXXY BILL\\nBill No: {o['bill_no']}\\nCustomer: {o['customer_name']}\\n")
                    for x in items:f.write(f"{x['product_name']} x{x['quantity']} = {money(x['total'])}\\n")
                    f.write(f"Subtotal: {money(o['subtotal'])}\\nDiscount: {money(o['discount'])}\\nGST: {money(o['gst'])}\\nGRAND TOTAL: {money(o['grand_total'])}\\n")
            else:
                with open(path,"w",encoding="utf-8") as f:f.write(self.bill_html(order_id))
            messagebox.showinfo("Saved","Bill exported successfully. Open the HTML file in a browser and choose Print → Save as PDF.")
        except OSError as e:messagebox.showerror("Save failed",str(e))

    def print_bill(self, order_id):
        path=filedialog.asksaveasfilename(defaultextension=".html",filetypes=[("HTML bill","*.html")],initialfile="FIXXY_bill.html")
        if not path:return
        try:
            Path(path).write_text(self.bill_html(order_id),encoding="utf-8")
            webbrowser.open(Path(path).resolve().as_uri())
            messagebox.showinfo("Print bill","The bill opened in your browser. Use its Print option to print or save as PDF.")
        except OSError as e:messagebox.showerror("Print failed",str(e))

    def page_stock(self,parent):
        self.label(parent,"Manage Spare-Parts Stock (Admin)",20,True).pack(anchor="w",pady=(0,10))
        cols=("id","name","category","price","stock","sold")
        tree=ttk.Treeview(parent,columns=cols,show="headings",height=13)
        self.stock_tree=tree
        for c,t,w in [("id","ID",45),("name","Part Name",210),("category","Category",130),("price","Price (₹)",110),("stock","Stock",80),("sold","Sold",80)]:
            tree.heading(c,text=t);tree.column(c,width=w,anchor="w" if c in ("name","category") else "center")
        tree.pack(fill="both",expand=True)
        for p in self.db.query("SELECT * FROM products WHERE category!='Water Wash' ORDER BY name"):
            tree.insert("","end",iid=str(p["id"]),values=(p["id"],p["name"],p["category"],p["price"],p["stock"],p["sold"]))
        form=tk.Frame(parent,bg=PANEL,padx=12,pady=12);form.pack(fill="x",pady=10)
        self.stock_vars={k:tk.StringVar() for k in ("name","category","price","stock","description")}
        for k,caption in [("name","Part name"),("category","Category"),("price","Price ₹"),("stock","Stock"),("description","Description")]:
            self.label(form,caption,8,True,MUTED,bg=PANEL).pack(side="left",padx=(0,4))
            self.entry(form,self.stock_vars[k],width=12 if k!="description" else 18).pack(side="left",padx=(0,8),ipady=4)
        self.button(parent,"Add New Part",self.add_product,True).pack(anchor="w")
        self.button(parent,"Refresh List",lambda:self.show_shell("Manage Stock")).pack(anchor="w",pady=7)

    def add_product(self):
        v={k:x.get().strip() for k,x in self.stock_vars.items()}
        if not v["name"] or not v["category"]:
            messagebox.showwarning("Missing details","Part name and category are required.");return
        try:price=safe_float(v["price"],"Price");stock=safe_int(v["stock"],"Stock")
        except ValueError as e:messagebox.showerror("Invalid data",str(e));return
        try:
            self.db.execute("INSERT INTO products(name,category,price,stock,description) VALUES(%s,%s,%s,%s,%s)",
                            (v["name"],v["category"],price,stock,v["description"]))
            messagebox.showinfo("Saved","New part added to catalogue.");self.show_shell("Manage Stock")
        except MySQLError as e:messagebox.showerror("Database error",str(e))

    def page_coupons(self,parent):
        self.label(parent,"Coupon Management (Admin)",20,True).pack(anchor="w",pady=(0,12))
        tree=ttk.Treeview(parent,columns=("code","discount","description","active"),show="headings",height=12)
        for c,t,w in [("code","Coupon Code",180),("discount","Discount %",100),("description","Description",280),("active","Active",80)]:
            tree.heading(c,text=t);tree.column(c,width=w)
        tree.pack(fill="both",expand=True)
        for r in self.db.query("SELECT * FROM coupons ORDER BY code"):
            tree.insert("","end",iid=r["code"],values=(r["code"],r["discount"],r["description"],"Yes" if r["active"] else "No"))
        form=tk.Frame(parent,bg=PANEL,padx=15,pady=15);form.pack(fill="x",pady=12)
        self.coupon_vars={k:tk.StringVar() for k in ("code","discount","description")}
        for k,cap in [("code","Coupon code"),("discount","Discount %"),("description","Description")]:
            self.label(form,cap,9,True,MUTED,bg=PANEL).pack(side="left",padx=(0,4))
            self.entry(form,self.coupon_vars[k],width=17).pack(side="left",padx=(0,12),ipady=5)
        self.button(parent,"Add / Update Coupon",self.save_coupon,True).pack(anchor="w")
        self.button(parent,"Toggle Selected Active / Inactive",lambda:self.toggle_coupon(tree)).pack(anchor="w",pady=8)

    def save_coupon(self):
        v={k:x.get().strip() for k,x in self.coupon_vars.items()}
        if not v["code"]:
            messagebox.showwarning("Missing code","Enter a coupon code.");return
        try:d=safe_float(v["discount"],"Discount")
        except ValueError as e:messagebox.showerror("Invalid discount",str(e));return
        if d>100:messagebox.showwarning("Invalid discount","Discount cannot exceed 100%.");return
        self.db.execute("INSERT INTO coupons(code,discount,description,active) VALUES(%s,%s,%s,1) "
                        "ON DUPLICATE KEY UPDATE discount=VALUES(discount),description=VALUES(description)",
                        (v["code"].upper(),d,v["description"]))
        messagebox.showinfo("Saved","Coupon saved.");self.show_shell("Coupons")

    def toggle_coupon(self,tree):
        sel=tree.selection()
        if not sel:messagebox.showwarning("Select coupon","Select a coupon first.");return
        self.db.execute("UPDATE coupons SET active=CASE active WHEN 1 THEN 0 ELSE 1 END WHERE code=%s",(sel[0],))
        self.show_shell("Coupons")

    def page_settings(self,parent):
        self.label(parent,"Settings & Project Information",21,True).pack(anchor="w",pady=(0,12))
        frame=tk.Frame(parent,bg=PANEL,padx=20,pady=20);frame.pack(fill="x",anchor="n")
        self.label(frame,"SHOP NAME",9,True,MUTED,bg=PANEL).pack(anchor="w")
        self.shop_var=tk.StringVar(value=self.db.setting("shop_name","FIXXY Car Spares"))
        self.entry(frame,self.shop_var).pack(anchor="w",fill="x",ipady=6,pady=(4,12))
        self.label(frame,"GST RATE (%)",9,True,MUTED,bg=PANEL).pack(anchor="w")
        self.gst_var=tk.StringVar(value=self.db.setting("gst_rate","18"))
        self.entry(frame,self.gst_var).pack(anchor="w",fill="x",ipady=6,pady=(4,12))
        self.button(frame,"Save Settings",self.save_settings,True).pack(anchor="w")
        info=tk.Frame(parent,bg=BG);info.pack(fill="x",pady=18)
        self.label(info,"PROJECT DETAILS",11,True,ORANGE).pack(anchor="w")
        self.label(info,"Title: FIXXY — Car Spare Parts & Billing System",10).pack(anchor="w",pady=3)
        self.label(info,"Language: Python 3  |  GUI: Tkinter  |  Database: MySQL",10).pack(anchor="w",pady=3)
        self.label(info,"Concepts: functions, classes, SQL CRUD, validation, exception handling and bill export.",10,False,MUTED,wraplength=850,justify="left").pack(anchor="w",pady=3)
        self.label(info,f"MySQL Database: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}",9,False,MUTED,wraplength=850,justify="left").pack(anchor="w",pady=3)

    def save_settings(self):
        try:gst=safe_float(self.gst_var.get(),"GST rate")
        except ValueError as e:messagebox.showerror("Invalid setting",str(e));return
        if gst>100:messagebox.showwarning("Invalid setting","GST rate must be 100% or less.");return
        self.db.set_setting("shop_name",self.shop_var.get().strip() or "FIXXY Car Spares")
        self.db.set_setting("gst_rate",gst)
        messagebox.showinfo("Saved","Settings updated.");self.show_shell("Settings")

if __name__ == "__main__":
    try:
        app = FixxyApp()
        app.mainloop()
    except Exception as exc:
        # Keep unexpected startup failures readable for students.
        try:
            messagebox.showerror("FIXXY startup error", 
                               f"{exc}\n\nMySQL: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}\n\n"
                               f"Make sure MySQL is running and credentials are correct.")
        except Exception:
            print("FIXXY startup error:", exc, file=sys.stderr)
            raise
