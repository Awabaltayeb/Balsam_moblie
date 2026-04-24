from database import get_db_connection

def add_drug(name, barcode, cost_price, price, quantity, expiry):
    conn = get_db_connection()
    conn.execute("INSERT INTO drugs (name, barcode, cost_price, price, quantity, expiry_date) VALUES (?, ?, ?, ?, ?, ?)", 
                 (name, barcode, cost_price, price, quantity, expiry))
    conn.commit()
    conn.close()

def update_drug(drug_id, name, barcode, cost_price, price, quantity, expiry):
    conn = get_db_connection()
    conn.execute("UPDATE drugs SET name=?, barcode=?, cost_price=?, price=?, quantity=?, expiry_date=? WHERE drug_id=?", 
                 (name, barcode, cost_price, price, quantity, expiry, drug_id))
    conn.commit()
    conn.close()

def delete_drug(drug_id):
    """Soft delete: Just mark as inactive."""
    conn = get_db_connection()
    conn.execute("UPDATE drugs SET is_active=0 WHERE drug_id=?", (drug_id,))
    conn.commit()
    conn.close()

def get_all_active_drugs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drugs WHERE is_active=1 ORDER BY name")
    drugs = cursor.fetchall()
    conn.close()
    return drugs

def search_drugs(term):
    """Search by name or barcode."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM drugs WHERE is_active=1 AND (name LIKE ? OR barcode LIKE ?)"
    cursor.execute(query, (f'%{term}%', f'%{term}%'))
    results = cursor.fetchall()
    conn.close()
    return results

def get_drug_by_id(drug_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drugs WHERE drug_id=?", (drug_id,))
    result = cursor.fetchone()
    conn.close()
    return result