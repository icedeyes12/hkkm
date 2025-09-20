# utils/unlocks.py
from utils.config import get_unlock_requirements
from utils.economy import deduct_balance

def can_unlock(profile, feature_type, feature_name):
    """Check if user can unlock a feature"""
    requirements = get_unlock_requirements(feature_type, feature_name)
    
    if not requirements:
        return True  # No requirements means it's unlocked by default
    
    # Check level requirement
    if profile.get("level", 1) < requirements.get("level", 1):
        return False
    
    # Check if already unlocked
    unlocked_features = profile.get("unlocked_features", {})
    if unlocked_features.get(feature_type, {}).get(feature_name, False):
        return True
    
    return True  # Can attempt to purchase

def unlock_feature(profile, feature_type, feature_name):
    """Unlock a feature for the user"""
    requirements = get_unlock_requirements(feature_type, feature_name)
    
    if not requirements:
        return True, "Feature unlocked!"
    
    # Check if we can deduct the cost
    cost = requirements.get("cost", 0)
    if cost > 0 and not deduct_balance(profile, cost):
        return False, "Not enough money to unlock this feature!"
    
    # Update user's unlocked features
    if "unlocked_features" not in profile:
        profile["unlocked_features"] = {}
    
    if feature_type not in profile["unlocked_features"]:
        profile["unlocked_features"][feature_type] = {}
    
    profile["unlocked_features"][feature_type][feature_name] = True
    
    return True, f"Unlocked {feature_name} for {format_currency(cost)}!"

def get_unlocked_plots(profile):
    """Get number of unlocked field plots"""
    return profile.get("unlocked_features", {}).get("field", {}).get("plots", 1)

def get_unlocked_barn_slots(profile):
    """Get number of unlocked barn slots"""
    return profile.get("unlocked_features", {}).get("barn", {}).get("slots", 1)

def get_unlocked_fishing_sites(profile):
    """Get list of unlocked fishing sites"""
    return profile.get("unlocked_features", {}).get("fishing_sites", ["pond"])