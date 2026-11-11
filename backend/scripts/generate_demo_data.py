import os
import random
import pymysql
import bcrypt
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker('en_IN')

# Database Configuration (Make sure this matches your config.py)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "grampur_csp")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

VILLAGE_NAME = "Gadepudi Village"

# Default password for all demo users: Demo@123
DEMO_PASSWORD_HASH = bcrypt.hashpw("Demo@123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )

def clear_existing_data(cursor):
    print("Clearing existing data...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("TRUNCATE TABLE feedback;")
    cursor.execute("TRUNCATE TABLE complaint_status_history;")
    cursor.execute("TRUNCATE TABLE assignments;")
    cursor.execute("TRUNCATE TABLE notifications;")
    cursor.execute("TRUNCATE TABLE complaints;")
    cursor.execute("TRUNCATE TABLE workers;")
    cursor.execute("DELETE FROM users WHERE role != 'admin';")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    print("Existing data cleared.")

def generate_users(cursor, count=500):
    print(f"Generating {count} villagers...")
    users = []
    for _ in range(count):
        mobile = fake.unique.numerify(text='9#########')
        users.append((
            fake.name(),
            mobile,
            VILLAGE_NAME,
            DEMO_PASSWORD_HASH,
            'villager'
        ))
    
    query = """
        INSERT INTO users (name, mobile, village, password_hash, role)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.executemany(query, users)
    print("Villagers created.")

def generate_workers(cursor, count=50):
    print(f"Generating {count} workers...")
    departments = [
        'Roads & Infrastructure',
        'Electrical & Streetlights',
        'Water Supply',
        'Drainage & Sanitation',
        'Waste Management',
        'General Services'
    ]
    
    for _ in range(count):
        name = fake.name()
        mobile = fake.unique.numerify(text='8#########')
        dept = random.choice(departments)
        
        # Create user account for worker
        cursor.execute("""
            INSERT INTO users (name, mobile, village, password_hash, role)
            VALUES (%s, %s, %s, %s, 'worker')
        """, (name, mobile, VILLAGE_NAME, DEMO_PASSWORD_HASH))
        
        user_id = cursor.lastrowid
        
        # Create worker profile
        cursor.execute("""
            INSERT INTO workers (user_id, worker_name, mobile, department)
            VALUES (%s, %s, %s, %s)
        """, (user_id, name, mobile, dept))
    print("Workers created.")

def generate_complaints(cursor, count=1000):
    print(f"Generating {count} complaints...")
    
    # Fetch all villagers
    cursor.execute("SELECT user_id FROM users WHERE role = 'villager'")
    villagers = [row['user_id'] for row in cursor.fetchall()]
    
    # Fetch all workers and their departments
    cursor.execute("SELECT worker_id, department, user_id FROM workers")
    workers = cursor.fetchall()
    
    # Fetch admin
    cursor.execute("SELECT user_id FROM users WHERE role = 'admin' LIMIT 1")
    admin = cursor.fetchone()
    admin_id = admin['user_id'] if admin else 1

    categories = [
        'Road Issues', 'Streetlight Issues', 'Water Supply Problems', 
        'Drainage Problems', 'Garbage Collection Issues', 'Sanitation Issues'
    ]
    
    statuses = ['Submitted', 'Under Review', 'Assigned', 'In Progress', 'Resolved', 'Rejected']
    priorities = ['Low', 'Medium', 'High', 'Critical']

    complaints = []
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    for i in range(count):
        # Generate complaint_id
        complaint_id = f"CMP{start_date.year}{str(i+1).zfill(3)}"
        
        created_at = fake.date_time_between(start_date=start_date, end_date=end_date)
        
        category = random.choice(categories)
        status = random.choices(statuses, weights=[10, 10, 15, 20, 40, 5], k=1)[0]
        
        # Determine resolved_at based on status
        resolved_at = None
        if status == 'Resolved':
            # Resolve usually takes 1 to 14 days
            resolve_days = random.randint(1, 14)
            resolved_at = created_at + timedelta(days=resolve_days)
            if resolved_at > end_date:
                resolved_at = end_date
                
        # Insert Complaint
        cursor.execute("""
            INSERT INTO complaints (
                complaint_id, user_id, title, category, description, 
                location, status, priority, created_at, updated_at, resolved_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            complaint_id,
            random.choice(villagers),
            f"Issue regarding {category.lower()}",
            category,
            fake.paragraph(),
            fake.address()[:250],
            status,
            random.choice(priorities),
            created_at,
            resolved_at or created_at,
            resolved_at
        ))
        
        # Insert Status History
        history = []
        history.append((complaint_id, None, 'Submitted', admin_id, created_at))
        
        if status in ['Under Review', 'Assigned', 'In Progress', 'Resolved']:
            review_time = created_at + timedelta(hours=random.randint(1, 24))
            history.append((complaint_id, 'Submitted', 'Under Review', admin_id, review_time))
            cursor.execute("INSERT INTO complaint_status_history (complaint_id, old_status, new_status, changed_by, changed_at) VALUES (%s, %s, %s, %s, %s)", history[-1])
            
        if status in ['Assigned', 'In Progress', 'Resolved']:
            assign_time = created_at + timedelta(hours=random.randint(24, 48))
            
            # Map category to worker department roughly
            dept_map = {
                'Road Issues': 'Roads & Infrastructure',
                'Streetlight Issues': 'Electrical & Streetlights',
                'Water Supply Problems': 'Water Supply',
                'Drainage Problems': 'Drainage & Sanitation',
                'Garbage Collection Issues': 'Waste Management',
                'Sanitation Issues': 'Waste Management'
            }
            target_dept = dept_map.get(category, 'General Services')
            eligible_workers = [w for w in workers if w['department'] == target_dept]
            if not eligible_workers:
                eligible_workers = workers
            worker = random.choice(eligible_workers)
            
            cursor.execute("UPDATE complaints SET worker_id = %s WHERE complaint_id = %s", (worker['worker_id'], complaint_id))
            
            # Create Assignment
            cursor.execute("""
                INSERT INTO assignments (complaint_id, worker_id, assigned_by, assigned_date)
                VALUES (%s, %s, %s, %s)
            """, (complaint_id, worker['worker_id'], admin_id, assign_time))
            
            history.append((complaint_id, 'Under Review', 'Assigned', admin_id, assign_time))
            cursor.execute("INSERT INTO complaint_status_history (complaint_id, old_status, new_status, changed_by, changed_at) VALUES (%s, %s, %s, %s, %s)", history[-1])
            
        if status in ['In Progress', 'Resolved']:
            progress_time = created_at + timedelta(days=random.randint(2, 5))
            history.append((complaint_id, 'Assigned', 'In Progress', worker['user_id'], progress_time))
            cursor.execute("INSERT INTO complaint_status_history (complaint_id, old_status, new_status, changed_by, changed_at) VALUES (%s, %s, %s, %s, %s)", history[-1])

        if status == 'Resolved':
            history.append((complaint_id, 'In Progress', 'Resolved', worker['user_id'], resolved_at))
            cursor.execute("INSERT INTO complaint_status_history (complaint_id, old_status, new_status, changed_by, changed_at) VALUES (%s, %s, %s, %s, %s)", history[-1])
            
            # 50% chance of getting feedback
            if random.random() > 0.5:
                cursor.execute("""
                    INSERT INTO feedback (complaint_id, user_id, rating, remarks, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (complaint_id, random.choice(villagers), random.randint(3, 5), fake.sentence(), resolved_at + timedelta(days=1)))

    print("Complaints generated.")

def run():
    print("Starting demo data generation...")
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            clear_existing_data(cursor)
            generate_users(cursor, count=500)
            generate_workers(cursor, count=100)
            generate_complaints(cursor, count=1000)
            conn.commit()
            print("Successfully populated database with realistic demo data.")
    except Exception as e:
        conn.rollback()
        print(f"Error during data generation: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run()
