"""
scripts/validate_db.py
Database verification script for Vemavaram Village CSP
"""

import os
import pymysql
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

def main():
    conn = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "vemavaram_csp"),
        cursorclass=pymysql.cursors.DictCursor
    )

    with conn.cursor() as cur:
        cur.execute("SHOW TABLES;")
        tables = [list(r.values())[0] for r in cur.fetchall()]
        print("=== TABLES CREATED IN vemavaram_csp ===")
        print(f"Total tables found: {len(tables)} (Expected: 15)")
        for idx, t in enumerate(sorted(tables), 1):
            print(f"  {idx:2d}. {t}")

        print("\n=== VERIFYING FOREIGN KEYS ===")
        cur.execute("""
            SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = 'vemavaram_csp' AND REFERENCED_TABLE_NAME IS NOT NULL
            ORDER BY TABLE_NAME, COLUMN_NAME;
        """)
        fks = cur.fetchall()
        for fk in fks:
            print(f"  {fk['TABLE_NAME']}.{fk['COLUMN_NAME']} -> {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']} [{fk['CONSTRAINT_NAME']}]")

        print("\n=== VERIFYING PRIMARY KEYS ===")
        cur.execute("""
            SELECT TABLE_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = 'vemavaram_csp' AND CONSTRAINT_NAME = 'PRIMARY'
            ORDER BY TABLE_NAME;
        """)
        pks = cur.fetchall()
        for pk in pks:
            print(f"  {pk['TABLE_NAME']} PK: {pk['COLUMN_NAME']}")

        print("\n=== VERIFYING SEED RECORDS ===")
        cur.execute("SELECT user_id, name, mobile, role, village, created_at FROM users WHERE role='admin';")
        admins = cur.fetchall()
        print(f"Admin Users ({len(admins)}):")
        for a in admins:
            print(f"  ID: {a['user_id']}, Name: {a['name']}, Mobile: {a['mobile']}, Role: {a['role']}, Village: {a['village']}")

        cur.execute("SELECT COUNT(*) as count FROM survey_insights;")
        print(f"Survey Insights: {cur.fetchone()['count']} records")

        cur.execute("SELECT COUNT(*) as count FROM wards;")
        print(f"Wards: {cur.fetchone()['count']} records")

        cur.execute("SELECT COUNT(*) as count FROM slas;")
        print(f"SLAs: {cur.fetchone()['count']} records")

        # Check contact_messages table structure
        print("\n=== VERIFYING contact_messages TABLE ===")
        cur.execute("DESCRIBE contact_messages;")
        cols = cur.fetchall()
        for c in cols:
            print(f"  {c['Field']} ({c['Type']}) Nullable: {c['Null']} Key: {c['Key']}")

        # Check worker_profiles table structure
        print("\n=== VERIFYING worker_profiles TABLE ===")
        cur.execute("DESCRIBE worker_profiles;")
        cols = cur.fetchall()
        for c in cols:
            print(f"  {c['Field']} ({c['Type']}) Nullable: {c['Null']} Key: {c['Key']}")

    conn.close()
    print("\nDatabase validation completed successfully.")

if __name__ == "__main__":
    main()

