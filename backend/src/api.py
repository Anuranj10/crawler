from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import os
import hashlib
import jwt
from datetime import datetime, timedelta
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.recommendation import get_recommendations_for_user
from src.document_processor import process_document
DB_NAME = "scholarships.db"
# Use absolute path resolving locally towards the top folder, or rely on Docker WD
db_path = DB_NAME if os.path.exists(DB_NAME) else os.path.join("..", DB_NAME)

app = FastAPI(title="Scholarship Recommendation API")

# Add CORS so a React frontend can call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            education_level TEXT,
            family_income REAL,
            category TEXT,
            religion TEXT,
            gender TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

SECRET_KEY = "a1b2c3d4e5f6789012345678abcdef01a1b2c3d4e5f6789012345678abcdef01"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 1 week

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()

class UserSignup(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    name: str
    email: str
    education_level: str
    family_income: float
    category: str
    religion: str
    gender: str

@app.get("/scholarships")
def get_scholarships(limit: int = 50, offset: int = 0):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scholarships LIMIT ? OFFSET ?", (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@app.post("/upload-document/")
async def upload_document(file: UploadFile = File(...)):
    """
    Accepts an uploaded image file, processes it via OCR,
    and returns detected keywords/document match confidence.
    """
    try:
        # Read the file contents as bytes
        contents = await file.read()
        
        # Pass to out document processor from Phase 8
        result = process_document(contents)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@app.post("/recommendations")
def get_recommendations(profile: UserProfile):
    try:
        # Convert Pydantic model to dictionary
        user_data = profile.model_dump()
        
        # Call our robust matching logic algorithm
        matches = get_recommendations_for_user(user_data)
        
        return {
            "status": "success",
            "matches": matches
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/signup")
def signup(user: UserSignup):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT email FROM users WHERE email = ?", (user.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
        
    salt = os.urandom(16).hex()
    password_hash = hash_password(user.password, salt)
    
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, salt)
        VALUES (?, ?, ?, ?)
    """, (user.name, user.email, password_hash, salt))
    conn.commit()
    conn.close()
    return {"message": "User created successfully"}

@app.post("/api/auth/login")
def login(user: UserLogin):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    db_user = cursor.fetchone()
    conn.close()
    
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    db_user = dict(db_user)
    
    if hash_password(user.password, db_user['salt']) != db_user['password_hash']:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": db_user['email'], "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "access_token": encoded_jwt, 
        "token_type": "bearer", 
        "user": {"name": db_user['name'], "email": db_user['email']}
    }

@app.get("/api/user/me")
def get_user_me(email: str = Depends(verify_token)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, education_level, family_income, category, religion, gender FROM users WHERE email = ?", (email,))
    db_user = cursor.fetchone()
    conn.close()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(db_user)

@app.post("/api/user/profile")
def update_user_profile(profile: UserProfile, email: str = Depends(verify_token)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET education_level = ?, family_income = ?, category = ?, religion = ?, gender = ?, name = ?
        WHERE email = ?
    """, (profile.education_level, profile.family_income, profile.category, profile.religion, profile.gender, profile.name, email))
    conn.commit()
    conn.close()
    return {"message": "Profile updated successfully"}

# Entrypoint for quick testing if run directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
