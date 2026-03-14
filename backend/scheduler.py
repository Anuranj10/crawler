import schedule
import time
import datetime
import subprocess
import os
import sys

# Get absolute path to project root (now inside backend folder or /app container)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def run_automation_job():
    """
    Executes the web crawler to fetch new scholarships,
    then automatically merges them into the SQLite database.
    """
    print(f"\n[{datetime.datetime.now()}] --- STARTING AUTOMATED SCHOLARSHIP CRAWL ---")
    
    # 1. Run the Crawler (main.py)
    try:
        print("[*] Running crawler (scraper/src/main.py)...")
        # Ensure we run using the active python (virtual env or system)
        result1 = subprocess.run(
            [sys.executable, "scraper/src/main.py"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        if result1.returncode != 0:
            print(f"[!] Crawler failed:\n{result1.stderr}")
            return
            
        print("[+] Crawler finished successfully.")
        
    except Exception as e:
        print(f"[!] Error executing crawler: {e}")
        return

    # 2. Run Database Migration (database_setup.py)
    try:
        print("[*] Syncing findings with SQLite database...")
        result2 = subprocess.run(
            [sys.executable, "database_setup.py"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        if result2.returncode != 0:
            print(f"[!] Database sync failed:\n{result2.stderr}")
            return
            
        print("[+] Database sync finished successfully.")
        
    except Exception as e:
        print(f"[!] Error executing database setup: {e}")
        return

    print(f"[{datetime.datetime.now()}] --- AUTOMATED CRAWL COMPLETE ---\n")

def start_scheduler():
    print(f"[*] Scholarship Scheduler started at {datetime.datetime.now()}.")
    print("[*] Waiting for scheduled jobs...")
    
    # Run the job immediately once on startup for sanity checking
    # run_automation_job()
    
    # --- CONFIGURE SCHEDULE INTERVAL HERE ---
    
    # For Production: Run once a day at 2:00 AM
    schedule.every().day.at("02:00").do(run_automation_job)
    
    # For Testing/Development: Run every 10 minutes
    # schedule.every(10).minutes.do(run_automation_job)
    
    while True:
        schedule.run_pending()
        time.sleep(60) # Only wake up once a minute to check schedule

if __name__ == "__main__":
    start_scheduler()
