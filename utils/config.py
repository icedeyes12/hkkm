# utils/config.py
from utils.db import read_db

def get_config():
    """Load the game configuration"""
    return read_db("config")

def get_economy_settings():
    """Get economy-related settings"""
    config = get_config()
    return config.get("economy", {})

def get_unlock_requirements(feature_type, feature_name):
    """Get unlock requirements for a specific feature"""
    config = get_config()
    return config.get("unlocks", {}).get(feature_type, {}).get(feature_name, {})

def get_casino_limits():
    """Get casino betting limits"""
    config = get_config()
    casino_config = config.get("casino", {})
    return casino_config.get("min_bet", 10), casino_config.get("max_bet", 500)

def get_xp_for_level(level):
    """Calculate XP needed for a specific level using configurable curve"""
    economy = get_economy_settings()
    xp_curve = economy.get("xp_curve", {})
    base = xp_curve.get("base", 100)
    scaling = xp_curve.get("scaling", 1.2)
    
    if level <= 1:
        return 0
    elif level == 2:
        return base
    else:
        return int(base * (scaling ** (level - 2)))