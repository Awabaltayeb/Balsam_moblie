
import sqlite3
from datetime import datetime
from database import get_db_connection

def process_cart_sale(user_id, cart_items, payment_method):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    invoice_ref = datetime.now().strftime("%Y%m%d%H%M%S")
    sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        for item in cart_items:
            drug_id = item['drug_id']
            qty_sold = item['qty']
            price = item['price']
            
            # جلب الكمية الحالية وسعر التكلفة من المخزون
            cursor.execute("SELECT quantity, cost_price FROM drugs WHERE drug_id=?", (drug_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"الدواء غير موجود")
            
            current_qty, cost_price = result['quantity'], result['cost_price']
            
            if current_qty < qty_sold:
                raise ValueError(f"الكمية غير كافية للدواء ID: {drug_id}")
            
            # تحديث الكمية
            new_qty = current_qty - qty_sold
            cursor.execute("UPDATE drugs SET quantity=? WHERE drug_id=?", (new_qty, drug_id))
            
            # حساب الإجمالي والربح
            line_total = price * qty_sold
            line_profit = (price - cost_price) * qty_sold  # معادلة الربح
            
            # إدخال الفاتورة مع الربح
            cursor.execute("""
                INSERT INTO sales (invoice_ref, sale_date, drug_id, quantity_sold, total_amount, profit, payment_method, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (invoice_ref, sale_date, drug_id, qty_sold, line_total, line_profit, payment_method, user_id))
        
        conn.commit()
        return "Success", invoice_ref
        
    except ValueError as ve:
        conn.rollback()
        return str(ve), None
    except Exception as e:
        conn.rollback()
        return f"Database Error: {str(e)}", None
    finally:
        conn.close()
