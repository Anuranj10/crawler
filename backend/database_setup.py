import sqlite3
import json
import os
from datetime import datetime

DB_NAME = "scholarships.db"
JSON_FILE = "scholarships_data.json"

def get_db_connection():
    """Establish and return a connection to the SQLite database."""
    # Ensure foreign keys are enabled if we use them later
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = 1")
    return conn

def init_db():
    """Initialize the database schema for scholarships."""
    print("[*] Initializing SQLite database schema...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table 1: Scholarships
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scholarships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        description_snippet TEXT,
        eligibility_criteria TEXT,
        income_limit TEXT,
        target_demographics TEXT, -- Stored as JSON array string
        education_levels TEXT,    -- Stored as JSON array string
        important_dates TEXT,     -- Stored as JSON array string
        application_links TEXT,   -- Stored as JSON array string
        full_text_hash TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Table 2: Users (For the Recommendation engine later)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT,
        salt TEXT,
        name TEXT,
        education_level TEXT,
        family_income REAL,
        category TEXT, -- e.g., 'General', 'OBC', 'SC', 'ST'
        religion TEXT,
        gender TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Table 3: User Applications (To track which user applied to what)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        scholarship_id INTEGER NOT NULL,
        status TEXT DEFAULT 'Saved', -- e.g., 'Saved', 'Applied', 'Rejected'
        applied_on TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (scholarship_id) REFERENCES scholarships (id)
    )
    ''')
    
    # Table 4: Automated Rules Engine Weights (Optional advanced feature)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recommendation_weights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parameter TEXT UNIQUE NOT NULL,
        weight_score INTEGER NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()
    print("[+] Database schema created successfully.")

def is_duplicate(cursor, url, item_hash):
    """Check if the scholarship already exists based on URL or text hash."""
    cursor.execute('SELECT id FROM scholarships WHERE url = ? OR full_text_hash = ?', (url, str(item_hash)))
    return cursor.fetchone() is not None

def insert_data():
    """Read data from Phase 1/2 JSON file and insert into SQLite."""
    print(f"[*] Reading data from {JSON_FILE}...")
    
    if not os.path.exists(JSON_FILE):
        print(f"[!] File {JSON_FILE} not found. Have you ran the crawler yet?")
        return

    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[!] Error reading JSON: {e}")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    inserted = 0
    duplicates = 0
    
    for item in data:
        url = item.get('url')
        full_text_hash = item.get('full_text_hash')
        
        if not url:
            continue
            
        if is_duplicate(cursor, url, full_text_hash):
            duplicates += 1
            continue
            
        try:
            # Convert list fields to JSON strings for SQLite storage
            target_demographics = json.dumps(item.get('target_demographics')) if item.get('target_demographics') else None
            education_levels = json.dumps(item.get('education_levels')) if item.get('education_levels') else None
            important_dates = json.dumps(item.get('important_dates')) if item.get('important_dates') else None
            application_links = json.dumps(item.get('application_links')) if item.get('application_links') else None
            
            cursor.execute('''
            INSERT INTO scholarships (
                url, title, description_snippet, eligibility_criteria, 
                income_limit, target_demographics, education_levels, 
                important_dates, application_links, full_text_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                url,
                item.get('title', 'No Title'),
                item.get('description_snippet', ''),
                item.get('eligibility_criteria'),
                item.get('income_limit'),
                target_demographics,
                education_levels,
                important_dates,
                application_links,
                str(full_text_hash) if full_text_hash else None
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            # Catch any unhandled unique constraint failures
            duplicates += 1
        except Exception as e:
            print(f"[!] Error inserting {url}: {e}")
            
    conn.commit()
    conn.close()
    
    print(f"[+] Data seeding complete!")
    print(f"    Total inserted : {inserted}")
    print(f"    Skipped (dupes): {duplicates}")

def create_mock_users():
    """Create a few mock users to test the Recommendation Engine later."""
    print("[*] Creating mock user profiles...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    mock_users = [
        ("alice@example.com", "Alice Sharma", "Undergraduate", 250000, "General", "Hindu", "Female"),
        ("bob@example.com", "Bob Singh", "Postgraduate", 150000, "OBC", "Sikh", "Male"),
        ("rahul@example.com", "Rahul Kumar", "School", 80000, "SC", "Hindu", "Male")
    ]
    
    for user in mock_users:
        try:
            cursor.execute('''
            INSERT INTO users (email, name, education_level, family_income, category, religion, gender)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', user)
        except sqlite3.IntegrityError:
            pass # Ignore if already exists
            
    # Add baseline recommendation rules
    rules = [
        ("education_match_score", 50),
        ("income_match_score", 30),
        ("demographic_match_score", 20)
    ]
    
    for rule in rules:
        try:
            cursor.execute('INSERT INTO recommendation_weights (parameter, weight_score) VALUES (?, ?)', rule)
        except sqlite3.IntegrityError:
            pass
            
    conn.commit()
    conn.close()
    print("[+] Mock users and rules created.")

if __name__ == "__main__":
    init_db()
    insert_data()
    create_mock_users()
