# utils/inventory_utils.py
# (all the inventory helper functions go here)

from utils.db import update_user_data

def add_to_inventory(profile, item_type, item_id, quantity=1):
    """Add an item to the user's inventory"""
    if "inventory" not in profile:
        profile["inventory"] = {}
    
    if item_type not in profile["inventory"]:
        profile["inventory"][item_type] = {}
    
    if item_id not in profile["inventory"][item_type]:
        profile["inventory"][item_type][item_id] = 0
    
    profile["inventory"][item_type][item_id] += quantity
    
    # Update database
    return update_user_data(profile["id"], {"inventory": profile["inventory"]})

def remove_from_inventory(profile, item_type, item_id, quantity=1):
    """Remove an item from the user's inventory"""
    if ("inventory" not in profile or 
        item_type not in profile["inventory"] or 
        item_id not in profile["inventory"][item_type] or
        profile["inventory"][item_type][item_id] < quantity):
        return False
    
    profile["inventory"][item_type][item_id] -= quantity
    
    # Remove if quantity reaches zero
    if profile["inventory"][item_type][item_id] <= 0:
        del profile["inventory"][item_type][item_id]
    
    # Update database
    return update_user_data(profile["id"], {"inventory": profile["inventory"]})

def get_inventory_count(profile, item_type, item_id=None):
    """Get count of specific item or all items of a type in inventory"""
    if "inventory" not in profile or item_type not in profile["inventory"]:
        return 0
    
    if item_id:
        return profile["inventory"][item_type].get(item_id, 0)
    else:
        return sum(profile["inventory"][item_type].values())

def has_item(profile, item_type, item_id, quantity=1):
    """Check if user has enough of a specific item"""
    return get_inventory_count(profile, item_type, item_id) >= quantity

def get_inventory_items(profile, item_type):
    """Get all items of a specific type from inventory"""
    if "inventory" not in profile or item_type not in profile["inventory"]:
        return {}
    
    return profile["inventory"][item_type].copy()