# utils/db.py
import json
import os
from datetime import datetime

def read_db(file_name):
    """Read a JSON file from the db folder (supports .txt or .json)"""
    # Try both extensions
    json_path = f"db/{file_name}.json"
    txt_path = f"db/{file_name}.txt"
    
    if os.path.exists(json_path):
        path = json_path
    elif os.path.exists(txt_path):
        path = txt_path
    else:
        return {}  # File doesn't exist
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return {}

def write_db(file_name, data):
    """Write data to a JSON file in db folder (always uses .json)"""
    path = f"db/{file_name}.json"
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error writing {path}: {e}")
        return False

def update_user_data(user_id, updates):
    """Update specific user data in the database"""
    users = read_db("users")
    if user_id in users:
        users[user_id].update(updates)
        if write_db("users", users):
            return True
    return False

def update_leaderboard(user_id, username, xp=None, balance=None):
    """Update leaderboard with user's latest stats"""
    leaderboard = read_db("leaderboard")
    
    # Initialize leaderboard if it doesn't exist
    if not leaderboard:
        leaderboard = {
            "top_xp": [],
            "top_wealth": [],
            "last_updated": datetime.now().isoformat()
        }
    
    if xp is not None:
        # Update XP leaderboard
        xp_updated = False
        for entry in leaderboard.get("top_xp", []):
            if entry["user_id"] == user_id:
                entry["xp"] = xp
                entry["username"] = username
                xp_updated = True
                break
        
        if not xp_updated:
            leaderboard.setdefault("top_xp", []).append({
                "user_id": user_id,
                "username": username,
                "xp": xp,
                "rank": 0
            })
    
    if balance is not None:
        # Update wealth leaderboard
        wealth_updated = False
        for entry in leaderboard.get("top_wealth", []):
            if entry["user_id"] == user_id:
                entry["balance"] = balance
                entry["username"] = username
                wealth_updated = True
                break
        
        if not wealth_updated:
            leaderboard.setdefault("top_wealth", []).append({
                "user_id": user_id,
                "username": username,
                "balance": balance,
                "rank": 0
            })
    
    # Sort and rank
    if "top_xp" in leaderboard:
        leaderboard["top_xp"].sort(key=lambda x: x["xp"], reverse=True)
        for i, entry in enumerate(leaderboard["top_xp"][:5], 1):
            entry["rank"] = i
    
    if "top_wealth" in leaderboard:
        leaderboard["top_wealth"].sort(key=lambda x: x["balance"], reverse=True)
        for i, entry in enumerate(leaderboard["top_wealth"][:5], 1):
            entry["rank"] = i
    
    # Update timestamp
    leaderboard["last_updated"] = datetime.now().isoformat()
    
    return write_db("leaderboard", leaderboard)
    # Add these functions to your existing utils/db.py

def get_leaderboard():
    """Get the current leaderboard data"""
    return read_db("leaderboard")

def update_leaderboard_entry(user_id, username, xp=None, balance=None):
    """Update a user's entry in the leaderboard"""
    leaderboard = get_leaderboard()
    
    # Initialize if leaderboard doesn't exist
    if not leaderboard:
        leaderboard = {
            "top_xp": [],
            "top_wealth": [],
            "last_updated": datetime.now().isoformat()
        }
    
    # Update XP leaderboard
    if xp is not None:
        update_leaderboard_category(leaderboard, "top_xp", user_id, username, xp, "xp")
    
    # Update wealth leaderboard
    if balance is not None:
        update_leaderboard_category(leaderboard, "top_wealth", user_id, username, balance, "balance")
    
    # Sort and rank both categories
    sort_and_rank_leaderboard(leaderboard)
    
    # Update timestamp
    leaderboard["last_updated"] = datetime.now().isoformat()
    
    return write_db("leaderboard", leaderboard)

def update_leaderboard_category(leaderboard, category, user_id, username, value, value_key):
    """Update a specific leaderboard category"""
    if category not in leaderboard:
        leaderboard[category] = []
    
    # Find existing entry
    entry_index = -1
    for i, entry in enumerate(leaderboard[category]):
        if entry["user_id"] == user_id:
            entry_index = i
            break
    
    if entry_index >= 0:
        # Update existing entry
        leaderboard[category][entry_index][value_key] = value
        leaderboard[category][entry_index]["username"] = username
    else:
        # Add new entry
        leaderboard[category].append({
            "user_id": user_id,
            "username": username,
            value_key: value,
            "rank": 0
        })

def sort_and_rank_leaderboard(leaderboard):
    """Sort and rank all leaderboard categories"""
    for category in ["top_xp", "top_wealth"]:
        if category in leaderboard:
            # Sort by value (descending)
            leaderboard[category].sort(key=lambda x: x["xp" if category == "top_xp" else "balance"], reverse=True)
            
            # Assign ranks
            for i, entry in enumerate(leaderboard[category][:10], 1):  # Top 10 only
                entry["rank"] = i
            
            # Keep only top 10 entries
            leaderboard[category] = leaderboard[category][:10]