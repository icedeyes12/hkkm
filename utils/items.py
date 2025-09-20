# utils/items.py
from utils.db import read_db

def get_all_items():
    """Get all items from the database"""
    return read_db("items")

def get_items_by_type(item_type):
    """Get items of a specific type"""
    items = get_all_items()
    return items.get(item_type, [])

def get_item_by_id(item_id):
    """Get a specific item by ID"""
    items = get_all_items()
    for item_type in items.values():
        for item in item_type:
            if item.get("id") == item_id:
                return item
    return None

def get_item_price(item_id):
    """Get price of an item"""
    item = get_item_by_id(item_id)
    return item.get("price", 0) if item else 0

def get_seed_info(seed_id):
    """Get information about a seed"""
    seeds = get_items_by_type("seeds")
    for seed in seeds:
        if seed["id"] == seed_id:
            return seed
    return None

def get_tool_info(tool_id):
    """Get information about a tool"""
    tools = get_items_by_type("tools")
    for tool in tools:
        if tool["id"] == tool_id:
            return tool
    return None

def get_rod_info(rod_id):
    """Get information about a fishing rod"""
    rods = get_items_by_type("rods")
    for rod in rods:
        if rod["id"] == rod_id:
            return rod
    return None

def get_bait_info(bait_id):
    """Get information about a bait"""
    baits = get_items_by_type("baits")
    for bait in baits:
        if bait["id"] == bait_id:
            return bait
    return None

def get_feed_info(feed_id):
    """Get information about an animal feed"""
    feeds = get_items_by_type("feeds")
    for feed in feeds:
        if feed["id"] == feed_id:
            return feed
    return None