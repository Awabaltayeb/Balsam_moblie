from database import get_db_connection
from datetime import datetime, timedelta
import settings  # استدعاء الملف الجديد

def get_low_stock_drugs():
    # قراءة الحد الأدنى من الإعدادات
    threshold = int(settings.get_setting('low_stock') or 10)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drugs WHERE quantity <= ? AND is_active=1", (threshold,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_expiring_drugs():
    # قراءة مدة الصلاحية من الإعدادات
    days = int(settings.get_setting('expiry_days') or 30)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    target_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    query = "SELECT * FROM drugs WHERE expiry_date <= ? AND is_active=1"
    cursor.execute(query, (target_date,))
    results = cursor.fetchall()
    conn.close()
    return results