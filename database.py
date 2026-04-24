
import sqlite3
import os

DB_NAME = "pharmacy.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT DEFAULT 'pharmacist' 
    )
    """)

    # التعديل: إضافة cost_price (سعر الشراء)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drugs (
        drug_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        barcode TEXT UNIQUE,
        cost_price REAL NOT NULL, 
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        expiry_date TEXT NOT NULL,
        is_active INTEGER DEFAULT 1
    )
    """)

    # التعديل: إضافة profit (الربح)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_ref TEXT NOT NULL,
        sale_date TEXT NOT NULL,
        drug_id INTEGER,
        quantity_sold INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        profit REAL NOT NULL, 
        payment_method TEXT NOT NULL, 
        user_id INTEGER,
        FOREIGN KEY (drug_id) REFERENCES drugs (drug_id),
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)
    
    default_settings =[('backup_days', '7'), ('low_stock', '10'), ('expiry_days', '30')]
    for key, val in default_settings:
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, val))
    
    conn.commit()
    conn.close()