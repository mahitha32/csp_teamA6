"""
backend/scripts/setup_tidb.py
Automated, idempotent database setup script for TiDB Starter / TiDB Serverless.
Vemavaram Village Complaint Redressal System (Vemavaram CSP)

Tasks performed:
1. Validates connection parameters and SSL/TLS using certifi.
2. Applies the complete schema from `migrations/schema_complete.sql`:
   - Creates all 15 tables using CREATE TABLE IF NOT EXISTS.
   - Safely omits default admin with publicly known password (Admin@123).
   - Safely omits mock survey data from survey_insights.
   - Applies idempotent seed data (wards, slas) with INSERT IGNORE.
3. Verifies that all 15 tables and relationships are created.
4. Performs a health query test.
"""

import os
import sys
import getpass
import ssl
import certifi
import pymysql
from dotenv import load_dotenv, set_key

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

env_path = os.path.join(backend_dir, ".env")
load_dotenv(env_path)


EXPECTED_TABLES = [
    "users",
    "worker_profiles",
    "otp_sessions",
    "wards",
    "complaints",
    "assignments",
    "complaint_status_history",
    "feedback",
    "notifications",
    "activity_logs",
    "survey_insights",
    "contact_messages",
    "assets",
    "slas",
    "escalations",
]


def get_db_credentials():
    """Retrieve database credentials from env or prompt user securely."""
    host = os.getenv("DB_HOST", "").strip()
    port = int(os.getenv("DB_PORT", "4000") if os.getenv("DB_PORT") else "4000")
    db_name = os.getenv("DB_NAME", "vemavaram_csp").strip()
    user = os.getenv("DB_USER", "").strip()
    password = os.getenv("DB_PASSWORD", "").strip()
    ssl_mode = os.getenv("DB_SSL_MODE", "REQUIRED").strip()

    # If host is localhost or missing, prompt interactively
    if not host or host in ("localhost", "127.0.0.1"):
        print("\n" + "=" * 60)
        print(" TiDB Starter Database Configuration")
        print(" Enter your TiDB cluster credentials (stored securely in .env)")
        print("=" * 60)
        host = input("TiDB Host (e.g. gateway01.ap-southeast-1.prod.aws.tidbcloud.com): ").strip()
        port_input = input("TiDB Port [default 4000]: ").strip()
        port = int(port_input) if port_input else 4000
        db_name_input = input("TiDB Database Name [default vemavaram_csp]: ").strip()
        db_name = db_name_input if db_name_input else "vemavaram_csp"
        user = input("TiDB Username: ").strip()
        password = getpass.getpass("TiDB Password (typing hidden): ").strip()
        ssl_mode = "REQUIRED"

        # Save to local backend/.env securely
        if host and user and password:
            set_key(env_path, "DB_HOST", host)
            set_key(env_path, "DB_PORT", str(port))
            set_key(env_path, "DB_NAME", db_name)
            set_key(env_path, "DB_USER", user)
            set_key(env_path, "DB_PASSWORD", password)
            set_key(env_path, "DB_SSL_MODE", ssl_mode)
            print(f"[OK] Saved credentials to local '{env_path}'")

    return host, port, db_name, user, password, ssl_mode


def connect_tidb(host, port, db_name, user, password, ssl_mode):
    """Establish a secure TLS connection to TiDB using certifi."""
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

    # TiDB Serverless requires SSL
    if ssl_mode and ssl_mode.upper() != "DISABLED":
        connect_kwargs["ssl"] = {"ca": certifi.where()}

    try:
        conn = pymysql.connect(**connect_kwargs)
        return conn
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to TiDB cluster: {e}")
        return None


def split_sql_statements(sql_text):
    """Split SQL script into discrete statements, ignoring semicolons inside quotes or comments."""
    statements = []
    current = []
    in_single_quote = False
    in_double_quote = False
    in_backtick = False
    in_line_comment = False
    in_block_comment = False
    i = 0
    n = len(sql_text)

    while i < n:
        c = sql_text[i]
        next_c = sql_text[i + 1] if i + 1 < n else ""

        if in_line_comment:
            if c == "\n":
                in_line_comment = False
            current.append(c)
            i += 1
            continue

        if in_block_comment:
            if c == "*" and next_c == "/":
                in_block_comment = False
                current.append("*/")
                i += 2
                continue
            current.append(c)
            i += 1
            continue

        if in_single_quote:
            if c == "\\" and next_c:
                current.append(c + next_c)
                i += 2
                continue
            if c == "'":
                in_single_quote = False
            current.append(c)
            i += 1
            continue

        if in_double_quote:
            if c == "\\" and next_c:
                current.append(c + next_c)
                i += 2
                continue
            if c == '"':
                in_double_quote = False
            current.append(c)
            i += 1
            continue

        if in_backtick:
            if c == "`":
                in_backtick = False
            current.append(c)
            i += 1
            continue

        # Detect comment starts
        if c == "-" and next_c == "-":
            in_line_comment = True
            current.append("--")
            i += 2
            continue

        if c == "/" and next_c == "*":
            in_block_comment = True
            current.append("/*")
            i += 2
            continue

        # Detect quote starts
        if c == "'":
            in_single_quote = True
            current.append(c)
            i += 1
            continue

        if c == '"':
            in_double_quote = True
            current.append(c)
            i += 1
            continue

        if c == "`":
            in_backtick = True
            current.append(c)
            i += 1
            continue

        # Detect statement end
        if c == ";":
            stmt = "".join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
            i += 1
            continue

        current.append(c)
        i += 1

    stmt = "".join(current).strip()
    if stmt:
        statements.append(stmt)

    return statements


def execute_schema(conn, schema_file_path):
    """Execute schema_complete.sql excluding default admin and mock survey data."""
    if not os.path.exists(schema_file_path):
        raise FileNotFoundError(f"Schema file not found: {schema_file_path}")

    with open(schema_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    raw_statements = split_sql_statements(content)
    executed_count = 0
    skipped_count = 0

    with conn.cursor() as cursor:
        cursor.execute("SET foreign_key_checks = 1;")

        for stmt in raw_statements:
            cleaned = stmt.strip()
            if not cleaned:
                continue

            # Strip leading comment lines to inspect the SQL verb
            lines = [l for l in cleaned.split("\n") if not l.strip().startswith("--")]
            sql_clean = "\n".join(lines).strip()
            if not sql_clean:
                continue

            # 1. Skip CREATE DATABASE and USE if already inside target database
            if sql_clean.upper().startswith("CREATE DATABASE") or sql_clean.upper().startswith("USE "):
                skipped_count += 1
                continue

            # 2. Exclude default admin with public password (Admin@123)
            if "Admin@123" in sql_clean or "9999900000" in sql_clean:
                print("  [SKIP] Default admin with public password (Admin@123) excluded for security.")
                skipped_count += 1
                continue

            # 3. Exclude mock survey insights data
            if "INSERT INTO survey_insights" in sql_clean:
                print("  [SKIP] Preloaded 2025 survey statistics excluded (survey_insights kept empty).")
                skipped_count += 1
                continue

            # Execute statement
            try:
                cursor.execute(sql_clean)
                executed_count += 1
                first_verb = sql_clean.split()[0:4]
                print(f"  [EXEC] {' '.join(first_verb)}")
            except Exception as e:
                print(f"  [WARN] Statement warning/error: {e}")
                print(f"         Statement snippet: {sql_clean[:60]}...")

    print(f"\n[OK] Schema execution finished. {executed_count} statements executed, {skipped_count} statements safely skipped.")


def verify_tables(conn):
    """Verify that all 15 expected tables exist and check count."""
    with conn.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        rows = cursor.fetchall()

    existing_tables = set()
    for row in rows:
        existing_tables.update(row.values())

    print("\n" + "=" * 60)
    print(" TiDB Database Verification — vemavaram_csp")
    print("=" * 60)

    all_present = True
    for table in EXPECTED_TABLES:
        status = "EXISTS" if table in existing_tables else "MISSING"
        if status == "MISSING":
            all_present = False
            print(f"  [FAIL] Table '{table}': {status}")
        else:
            print(f"  [PASS] Table '{table}': {status}")

    print("-" * 60)
    print(f"Total tables found: {len(existing_tables)} / {len(EXPECTED_TABLES)} expected")

    # Verify foreign keys on complaints table
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL;
        """)
        fks = cursor.fetchall()
        print(f"Total Foreign Key constraints registered: {len(fks)}")
        for fk in fks[:5]:
            print(f"  FK: {fk['TABLE_NAME']}.{fk['COLUMN_NAME']} -> {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}")
        if len(fks) > 5:
            print(f"  ... and {len(fks) - 5} more foreign keys established.")

    # Check that survey_insights has 0 records
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS cnt FROM survey_insights;")
        survey_cnt = cursor.fetchone()["cnt"]
        print(f"Survey insights record count: {survey_cnt} (Expected: 0)")

    # Check wards seed count
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS cnt FROM wards;")
        wards_cnt = cursor.fetchone()["cnt"]
        print(f"Wards seed count: {wards_cnt} (Expected: 4)")

    # Check SLAs seed count
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS cnt FROM slas;")
        slas_cnt = cursor.fetchone()["cnt"]
        print(f"SLAs seed count: {slas_cnt} (Expected: 6)")

    return all_present


def main():
    print("============================================================")
    print(" Vemavaram CSP — TiDB Starter Database Setup")
    print("============================================================")

    host, port, db_name, user, password, ssl_mode = get_db_credentials()
    if not host or not user or not password:
        print("[ERROR] Database credentials incomplete. Please set them in backend/.env")
        sys.exit(1)

    print(f"Connecting to TiDB: host={host}, port={port}, database={db_name}, user={user}...")
    conn = connect_tidb(host, port, db_name, user, password, ssl_mode)
    if not conn:
        print("[FATAL] Could not connect to TiDB cluster.")
        sys.exit(1)

    print("[SUCCESS] Connected securely to TiDB cluster via TLS!")

    schema_file = os.path.join(backend_dir, "migrations", "schema_complete.sql")
    print(f"\nApplying schema from: {schema_file}")
    execute_schema(conn, schema_file)

    success = verify_tables(conn)
    conn.close()

    if success:
        print("\n============================================================")
        print(" [SUCCESS] TiDB Database setup completed successfully!")
        print(" Next step: Run 'python scripts/create_admin.py' to create")
        print(" your secure production administrator account.")
        print("============================================================")
    else:
        print("\n[WARNING] Some tables were not detected. Please review logs above.")


if __name__ == "__main__":
    main()

