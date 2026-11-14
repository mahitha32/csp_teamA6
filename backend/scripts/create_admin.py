"""
backend/scripts/create_admin.py
Secure interactive creation of the production administrator account.
Vemavaram Village Complaint Redressal System (Vemavaram CSP)

Hashes password with bcrypt (12 rounds) and creates an admin record in `users`.
Does NOT use or expose any default or publicly known passwords.
"""

import os
import sys
import getpass
import re
import certifi
import bcrypt
import pymysql
from dotenv import load_dotenv

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

load_dotenv(os.path.join(backend_dir, ".env"))


def main():
    print("=" * 60)
    print(" Vemavaram CSP — Secure Administrator Creation")
    print("=" * 60)

    host = os.getenv("DB_HOST", "localhost").strip()
    port = int(os.getenv("DB_PORT", "4000") if os.getenv("DB_PORT") else "4000")
    db_name = os.getenv("DB_NAME", "vemavaram_csp").strip()
    user = os.getenv("DB_USER", "").strip()
    password = os.getenv("DB_PASSWORD", "").strip()
    ssl_mode = os.getenv("DB_SSL_MODE", "REQUIRED").strip()

    if not host or not user:
        print("[ERROR] Database credentials not found in backend/.env")
        sys.exit(1)

    print("\nPlease enter details for the production Administrator:")
    name = input("Administrator Name [default: Village Admin]: ").strip()
    if not name:
        name = "Village Admin"

    while True:
        mobile = input("Admin Mobile Number (10 digits): ").strip()
        if re.match(r"^[6-9]\d{9}$", mobile):
            break
        print("[!] Please enter a valid 10-digit Indian mobile number (e.g., 9876543210).")

    email = input("Admin Email [optional, e.g. admin@vemavaram.gov.in]: ").strip()
    if not email:
        email = f"admin@{mobile}.gov.in"

    while True:
        pwd = getpass.getpass("Admin Password (min 8 chars, typing hidden): ").strip()
        if len(pwd) < 8:
            print("[!] Password must be at least 8 characters long.")
            continue
        if pwd == "Admin@123":
            print("[!] 'Admin@123' is a prohibited default password. Please choose a strong, unique password.")
            continue
        pwd_confirm = getpass.getpass("Confirm Admin Password: ").strip()
        if pwd != pwd_confirm:
            print("[!] Passwords do not match. Try again.")
            continue
        break

    # Hash with bcrypt (12 rounds)
    print("\nHashing password securely with bcrypt (12 rounds)...")
    salt = bcrypt.gensalt(rounds=12)
    pwd_hash = bcrypt.hashpw(pwd.encode("utf-8"), salt).decode("utf-8")

    # Connect to database
    connect_kwargs = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": db_name,
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": True,
    }
    if ssl_mode and ssl_mode.upper() != "DISABLED":
        connect_kwargs["ssl"] = {"ca": certifi.where()}

    try:
        conn = pymysql.connect(**connect_kwargs)
    except Exception as e:
        print(f"[ERROR] Could not connect to database: {e}")
        sys.exit(1)

    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO users (name, mobile, email, village, password_hash, role, is_active)
            VALUES (%s, %s, %s, 'Vemavaram', %s, 'admin', 1)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                email = VALUES(email),
                password_hash = VALUES(password_hash),
                role = 'admin',
                is_active = 1;
        """, (name, mobile, email, pwd_hash))

    conn.close()

    print("\n" + "=" * 60)
    print(" [SUCCESS] Administrator Account Created Successfully!")
    print(f" Name:   {name}")
    print(f" Mobile: {mobile}")
    print(f" Email:  {email}")
    print(f" Role:   admin")
    print(" Password hash stored safely in TiDB.")
    print("=" * 60)


if __name__ == "__main__":
    main()

