import os
import json
import uuid
import hashlib
from getpass import getpass
from datetime import datetime
from utils.db import read_db, write_db

DB_FILE = "users"

# ---------------- HELPERS ----------------
def hash_password(password: str) -> str:
    """Return a SHA256 hash of the password."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from database"""
    return read_db(DB_FILE)

def save_users(users):
    """Save users to database"""
    write_db(DB_FILE, users)

def find_user_by_username(username):
    """Find user by username, returns user data or None"""
    users = load_users()
    for user_data in users.values():
        if user_data["username"] == username:
            return user_data
    return None

# ---------------- LOGIN / ACCOUNT ----------------
def login():
    """Handle user login with clear error messages"""
    username = input("username: ")
    password = getpass("password: ")
    
    user_data = find_user_by_username(username)
    
    if user_data is None:
        print(f"\n❌ Account '{username}' doesn't exist.")
        choice = input("Would you like to create a new account? (y/n): ").lower().strip()
        
        if choice in ['y', 'yes']:
            return create_account()
        else:
            print("Returning to login menu...")
            return None, None
    
    # Check password
    if user_data["password"] == hash_password(password):
        print(f"\n✅ Welcome back, {user_data['nickname']}!")
        return user_data['id'], user_data
    else:
        print("\n❌ Incorrect password. Please try again.")
        return None, None

def create_account():
    """Create a new user account"""
    users = load_users()
    
    # Get account details
    nickname = input("nickname: ")
    
    # Get username with duplicate check
    while True:
        username = input("username: ")
        if find_user_by_username(username):
            print("⚠️ Username already taken. Please choose another.")
        else:
            break
    
    # Password handling
    while True:
        password = getpass("Create password: ")
        
        # Password validation
        if len(password) < 4:
            print("⚠️ Password must be at least 4 characters long.")
            continue
            
        confirm = getpass("Confirm password: ")
        
        if password != confirm:
            print("⚠️ Passwords don't match. Try again.\n")
        else:
            break
    
    # Create user profile
    uid = str(uuid.uuid4())[:8]
    profile = {
        "id": uid,
        "username": username,
        "nickname": nickname,
        "password": hash_password(password),
        "xp": 0,
        "level": 1,
        "balance": 500,
        "inventory": {},
        "created_at": str(datetime.now())
    }
    
    # Save user
    users[uid] = profile
    save_users(users)
    
    print(f"\n🎉 Account created successfully!")
    print(f"Welcome to Hikikimo Life, {nickname}!")
    
    return uid, profile

def guest():
    """Create a guest profile"""
    profile = {
        "id": "guest",
        "username": "guest",
        "nickname": "Guest",
        "password": None,
        "xp": 0,
        "level": 1,
        "balance": 500,
        "inventory": {},
        "is_guest": True
    }
    print("\n👤 Playing as Guest (progress won't be saved).")
    return "guest", profile