import csv
from database import get_db_connection

def get_sales_report_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # تأكد أن s.payment_method موجودة هنا 👇
    query = """
        SELECT 
          s.invoice_ref,
          s.sale_date, 
          d.name, 
          s.quantity_sold, 
          s.total_amount, 
          s.payment_method, 
          u.username
        FROM sales s
        LEFT JOIN drugs d ON 
    s.drug_id = d.drug_id
        LEFT JOIN users u ON
     s.user_id = u.user_id
        ORDER BY s.sale_date DESC
    """
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        print(f"Database Error in Reports: {e}") # هذا السطر سيطبع الخطأ في التيرمينال لو وجد
        conn.close()
        return []

def export_to_csv(filename="sales_report.csv"):
    data = get_sales_report_data()
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["رقم الفاتورة", "التاريخ", "الدواء", "الكمية", "الإجمالي", "طريقة الدفع", "البائع"])
            for row in data:
                writer.writerow([
                    row['invoice_ref'], 
                    row['sale_date'], 
                    row['name'], 
                    row['quantity_sold'], 
                    row['total_amount'], 
                    row['payment_method'], # تأكد أن هذا الاسم يطابق العمود في قاعدة البيانات
                    row['username']
                ])
        return True
    except Exception:
        return False