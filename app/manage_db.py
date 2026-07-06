import sys
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "growth_capabilities.db")

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")  # Enforce cascade deletes
    conn.row_factory = sqlite3.Row
    return conn

def list_companies():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.industry, COUNT(e.id) as eval_count 
        FROM companies c
        LEFT JOIN evaluations e ON e.company_id = c.id
        GROUP BY c.id
        ORDER BY c.name
    """)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No companies found in database.")
        return
        
    print(f"{'ID':<5} | {'Company Name':<25} | {'Industry':<35} | {'Evaluations':<12}")
    print("-" * 85)
    for r in rows:
        print(f"{r['id']:<5} | {r['name']:<25} | {r['industry'] or 'N/A':<35} | {r['eval_count']:<12}")

def delete_company(company_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if company exists
    cursor.execute("SELECT id FROM companies WHERE name = ?", (company_name,))
    row = cursor.fetchone()
    if not row:
        print(f"Error: Company '{company_name}' not found in database.")
        conn.close()
        return
        
    company_id = row["id"]
    
    # Delete the company (cascade deletes will automatically remove associated evaluations & scores)
    cursor.execute("DELETE FROM companies WHERE id = ?", (company_id,))
    conn.commit()
    conn.close()
    print(f"✓ Successfully deleted '{company_name}' and all associated history.")

def print_usage():
    print("Growth Intelligence Platform - Database Management Utility")
    print("Usage:")
    print("  uv run python app/manage_db.py list")
    print("  uv run python app/manage_db.py delete \"Company Name\"")

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    if cmd == "list":
        list_companies()
    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("Error: Please specify the company name to delete.")
            print("Example: uv run python app/manage_db.py delete \"MSC Cruises\"")
            sys.exit(1)
        company_name = sys.argv[2]
        delete_company(company_name)
    else:
        print(f"Error: Unknown command '{cmd}'")
        print_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()
