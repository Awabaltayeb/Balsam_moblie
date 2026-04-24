from database import get_db_connection
from datetime import datetime, timedelta

def get_financial_summary():
    """يجلب مبيعات وأرباح اليوم، وأرباح الشهر الحالي"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    current_month = datetime.now().strftime("%Y-%m")
    
    # إحصائيات اليوم (مبيعات، أرباح، عدد فواتير)
    cursor.execute("""
        SELECT SUM(total_amount) as sales_today, 
               SUM(profit) as profit_today, 
               COUNT(DISTINCT invoice_ref) as invoice_count 
        FROM sales WHERE date(sale_date) = ?
    """, (today,))
    today_stats = cursor.fetchone()
    
    # أرباح الشهر
    cursor.execute("""
        SELECT SUM(profit) as profit_month 
        FROM sales WHERE strftime('%Y-%m', sale_date) = ?
    """, (current_month,))
    month_stats = cursor.fetchone()
    
    conn.close()
    
    return {
        "sales_today": today_stats['sales_today'] or 0,
        "profit_today": today_stats['profit_today'] or 0,
        "invoices_today": today_stats['invoice_count'] or 0,
        "profit_month": month_stats['profit_month'] or 0
    }

def get_top_selling_drugs(limit=5):
    """يجلب أكثر الأدوية مبيعاً (بالكمية)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.name, SUM(s.quantity_sold) as total_qty 
        FROM sales s 
        JOIN drugs d ON s.drug_id = d.drug_id 
        GROUP BY s.drug_id 
        ORDER BY total_qty DESC LIMIT ?
    """, (limit,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_least_selling_drugs(limit=5):
    """يجلب أقل الأدوية مبيعاً (من الأدوية التي بيعت فعلاً)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.name, SUM(s.quantity_sold) as total_qty 
        FROM sales s 
        JOIN drugs d ON s.drug_id = d.drug_id 
        GROUP BY s.drug_id 
        ORDER BY total_qty ASC LIMIT ?
    """, (limit,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_stagnant_drugs(days=30):
    """يجلب الأدوية التي لم تُبع إطلاقاً منذ فترة (الأدوية الراكدة)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    target_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # الأدوية الموجودة في المخزون، و(لم يتم بيعها أبداً، أو آخر بيعة لها كانت قبل التاريخ المستهدف)
    cursor.execute("""
        SELECT name, quantity 
        FROM drugs 
        WHERE is_active=1 
        AND drug_id NOT IN (
            SELECT DISTINCT drug_id FROM sales WHERE date(sale_date) >= ?
        )
        ORDER BY quantity DESC LIMIT 10
    """, (target_date,))
    
    results = cursor.fetchall()
    conn.close()
    return results