import sqlite3
import json
import re
import os

DB_NAME = "scholarships.db"
# If running from src/, path is ../scholarships.db. If from root, it's just scholarships.db.
db_path = DB_NAME if os.path.exists(DB_NAME) else os.path.join("..", DB_NAME)


def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Allow dictionary-like access to columns
    return conn

def get_weights():
    """Fetch scoring weights from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT parameter, weight_score FROM recommendation_weights")
    weights = {row['parameter']: row['weight_score'] for row in cursor.fetchall()}
    conn.close()
    
    # Defaults in case DB is missing them
    if not weights:
        weights = {
            "education_match_score": 50,
            "income_match_score": 30,
            "demographic_match_score": 20
        }
    return weights

def extract_income_limit(income_text):
    """
    Attempt to convert natural language income limits into a numeric threshold.
    E.g., "2.5 lakh" -> 250000
    """
    if not income_text:
        return None
        
    text = income_text.lower().replace(',', '')
    text = text.replace('rs', '').replace('inr', '').replace('₹', '').strip()
    
    # Look for a number
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return None
        
    number = float(match.group(1))
    
    # Scale it
    if 'lakh' in text or 'lpa' in text:
        return number * 100000
    if 'k' in text or 'thousand' in text:
        return number * 1000
        
    # If the number is incredibly small, assume it means LPA (e.g. "8.0" meaning 8 Lakhs)
    if number < 50:
        return number * 100000
        
    return number

def score_education(user_education, scholarship_education_json, max_score):
    if not scholarship_education_json:
        return max_score * 0.5  # Neutral score if scholarship doesn't specify
    
    levels = json.loads(scholarship_education_json)
    if not levels:
        return max_score * 0.5
        
    upper_levels = [l.upper() for l in levels]
    if user_education.upper() in upper_levels:
        return max_score
        
    # If the scholarship explicitly states an education level and user doesn't match, disqualify them.
    return -100

def score_income(user_income, scholarship_income_text, max_score):
    if not scholarship_income_text:
         return max_score * 0.5 # Neutral if not specified
         
    limit = extract_income_limit(scholarship_income_text)
    if not limit:
         return max_score * 0.5
         
    if user_income <= limit:
        return max_score
    return 0

def score_demographics(user_category, user_religion, user_gender, scholarship_demographics_json, max_score):
    if not scholarship_demographics_json:
        return max_score * 0.5 # Neutral if open to all
        
    demographics = json.loads(scholarship_demographics_json)
    if not demographics:
        return max_score * 0.5
        
    score = 0
    upper_demo = [d.upper() for d in demographics]
    
    # Strict checks: If scholarship is EXPLICITLY for a gender, punish mismatches heavily
    if "FEMALE" in upper_demo and user_gender.upper() != "FEMALE":
        return -100 # Disqualify
    if "MALE" in upper_demo and "FEMALE" not in upper_demo and user_gender.upper() != "MALE":
        return -100 # Disqualify
        
    # Category / Caste
    if user_category.upper() in upper_demo:
        score += max_score * 0.5
    elif "GENERAL" in upper_demo:
        score += max_score * 0.25
        
    # Religion / Minority
    if "MINORITY" in upper_demo and user_religion.upper() in ["MUSLIM", "CHRISTIAN", "SIKH", "BUDDHIST", "PARSI", "JAIN"]:
        score += max_score * 0.25
    if user_religion.upper() in upper_demo:
         score += max_score * 0.25
         
    # Gender (if it matches explicitly and wasn't disqualified)
    if user_gender.upper() in upper_demo:
         score += max_score * 0.25
         
    return min(score, max_score)

def get_recommendations_for_user(user):
    """
    Accepts a user dictionary (matching the UserProfile pydantic model in our API)
    and returns a sorted list of matched scholarship dictionaries.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    weights = get_weights()
    
    # Fetch all scholarships to score against
    cursor.execute("SELECT * FROM scholarships")
    scholarships = cursor.fetchall()
    
    matches = []
    for s in scholarships:
        ed_score = score_education(user['education_level'], s['education_levels'], weights['education_match_score'])
        inc_score = score_income(user['family_income'], s['income_limit'], weights['income_match_score'])
        dem_score = score_demographics(user['category'], user['religion'], user['gender'], s['target_demographics'], weights['demographic_match_score'])
        
        total_score = ed_score + inc_score + dem_score
        
        if total_score >= 60:
            # We convert the sqlite3.Row object to a standard dict for JSON serialization
            matches.append({
                "id": s['id'],
                "title": s['title'],
                "score": total_score,
                "url": s['url'],
                "description_snippet": s['description_snippet'],
                "application_links": s['application_links'],
                "important_dates": s['important_dates']
            })
    
    conn.close()
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches

def generate_recommendations():
    """Legacy terminal testing function."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch Mock Users
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    with open("recommendation_test_output.txt", "w", encoding="utf-8") as out:
        out.write("=== Scholarship Recommendation Engine ===\n")
        
        for user_row in users:
            # Convert DB row to a dict for our generic function
            user_dict = dict(user_row)
            
            out.write(f"\n[+] Processing recommendations for: {user_dict['name']} ({user_dict['email']})\n")
            out.write(f"    Profile: {user_dict['education_level']} | Income: {user_dict['family_income']} | {user_dict['category']} | {user_dict['religion']} | {user_dict['gender']}\n")
            
            matches = get_recommendations_for_user(user_dict)
            
            if not matches:
                out.write("    [-] No strong matches found.\n")
            else:
                out.write(f"    [*] Found {len(matches)} strong matches. Top 5:\n")
                for m in matches[:5]:
                    out.write(f"        -> [Score: {m['score']:>4.1f}] {m['title'][:80]}... (ID: {m['id']})\n")
        
    conn.close()
    print("[+] Wrote test output to recommendation_test_output.txt")

if __name__ == "__main__":
    generate_recommendations()
