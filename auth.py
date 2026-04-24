import hashlib
import os
from database import get_db_connection

def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return pwd_hash, salt

def create_user(username, password, role="pharmacist"):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False # المستخدم موجود
        pwd_hash, salt = hash_password(password)
        cursor.execute("INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)", 
                       (username, pwd_hash, salt, role))
        conn.commit()
        return True
    finally:
        conn.close()

def login_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, password_hash, salt, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user:
        if hash_password(password, user['salt'])[0] == user['password_hash']:
            return user['user_id'], user['role']
    return None

# --- دوال إدارة المستخدمين الجديدة ---
def get_all_users():
    conn = get_db_connection()
    users = conn.execute("SELECT user_id, username, role FROM users").fetchall()
    conn.close()
    return users

def delete_user(user_id):
    conn = get_db_connection()
    # نمنع حذف الآدمن الرئيسي (رقم 1 غالباً) لتجنب قفل النظام
    if user_id == 1: 
        conn.close()
        return False
    conn.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    return True

def update_password(user_id, new_password):
    pwd_hash, salt = hash_password(new_password)
    conn = get_db_connection()
    conn.execute("UPDATE users SET password_hash=?, salt=? WHERE user_id=?", (pwd_hash, salt, user_id))
    conn.commit()
    conn.close()

def seed_admin():
    create_user("awab","1234","admin")