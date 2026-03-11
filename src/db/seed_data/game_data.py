"""Default game data for seeding the database."""

from __future__ import annotations

from typing import Any

# Fish data
FISH_DATA: list[dict[str, Any]] = [
    # Common - Pond
    {"id": 1, "name": "Minnow", "rarity": "common", "base_price": 5, "xp_reward": 2, "min_weight": 0.01, "max_weight": 0.05, "habitat": "pond"},
    {"id": 2, "name": "Bluegill", "rarity": "common", "base_price": 8, "xp_reward": 3, "min_weight": 0.05, "max_weight": 0.3, "habitat": "pond"},
    {"id": 3, "name": "Crappie", "rarity": "common", "base_price": 10, "xp_reward": 4, "min_weight": 0.1, "max_weight": 0.5, "habitat": "pond"},

    # Common - River
    {"id": 4, "name": "Creek Chub", "rarity": "common", "base_price": 6, "xp_reward": 2, "min_weight": 0.02, "max_weight": 0.1, "habitat": "river"},
    {"id": 5, "name": "Fallfish", "rarity": "common", "base_price": 7, "xp_reward": 3, "min_weight": 0.05, "max_weight": 0.3, "habitat": "river"},

    # Common - Lake
    {"id": 6, "name": "Yellow Perch", "rarity": "common", "base_price": 12, "xp_reward": 4, "min_weight": 0.1, "max_weight": 0.6, "habitat": "lake"},
    {"id": 7, "name": "Rock Bass", "rarity": "common", "base_price": 15, "xp_reward": 5, "min_weight": 0.1, "max_weight": 0.4, "habitat": "lake"},

    # Common - Ocean
    {"id": 8, "name": "Sardine", "rarity": "common", "base_price": 8, "xp_reward": 3, "min_weight": 0.05, "max_weight": 0.2, "habitat": "ocean"},
    {"id": 9, "name": "Mackerel", "rarity": "common", "base_price": 15, "xp_reward": 5, "min_weight": 0.2, "max_weight": 1.0, "habitat": "ocean"},

    # Uncommon
    {"id": 10, "name": "Trout", "rarity": "uncommon", "base_price": 25, "xp_reward": 10, "min_weight": 0.2, "max_weight": 2.0, "habitat": "river"},
    {"id": 11, "name": "Bass", "rarity": "uncommon", "base_price": 30, "xp_reward": 12, "min_weight": 0.3, "max_weight": 3.0, "habitat": "lake"},
    {"id": 12, "name": "Walleye", "rarity": "uncommon", "base_price": 28, "xp_reward": 11, "min_weight": 0.5, "max_weight": 4.0, "habitat": "lake"},
    {"id": 13, "name": "Snapper", "rarity": "uncommon", "base_price": 35, "xp_reward": 14, "min_weight": 0.5, "max_weight": 3.0, "habitat": "ocean"},

    # Rare
    {"id": 14, "name": "Salmon", "rarity": "rare", "base_price": 80, "xp_reward": 30, "min_weight": 2.0, "max_weight": 15.0, "habitat": "river"},
    {"id": 15, "name": "Pike", "rarity": "rare", "base_price": 75, "xp_reward": 28, "min_weight": 1.0, "max_weight": 8.0, "habitat": "lake"},
    {"id": 16, "name": "Tuna", "rarity": "rare", "base_price": 100, "xp_reward": 40, "min_weight": 5.0, "max_weight": 50.0, "habitat": "ocean"},
    {"id": 17, "name": "Swordfish", "rarity": "rare", "base_price": 120, "xp_reward": 45, "min_weight": 10.0, "max_weight": 100.0, "habitat": "ocean"},

    # Legendary
    {"id": 18, "name": "Golden Koi", "rarity": "legendary", "base_price": 500, "xp_reward": 200, "min_weight": 1.0, "max_weight": 5.0, "habitat": "pond"},
    {"id": 19, "name": "Arapaima", "rarity": "legendary", "base_price": 400, "xp_reward": 150, "min_weight": 50.0, "max_weight": 200.0, "habitat": "river"},
    {"id": 20, "name": "Blue Whale", "rarity": "legendary", "base_price": 1000, "xp_reward": 500, "min_weight": 80000.0, "max_weight": 150000.0, "habitat": "ocean"},
]

# Crop data
CROPS_DATA: list[dict[str, Any]] = [
    {"id": 1, "name": "Wheat", "growth_time": 300, "delay_time": 60, "base_price": 15, "xp_reward": 5},
    {"id": 2, "name": "Corn", "growth_time": 600, "delay_time": 120, "base_price": 30, "xp_reward": 10},
    {"id": 3, "name": "Carrot", "growth_time": 450, "delay_time": 90, "base_price": 25, "xp_reward": 8},
    {"id": 4, "name": "Potato", "growth_time": 540, "delay_time": 100, "base_price": 28, "xp_reward": 9},
    {"id": 5, "name": "Tomato", "growth_time": 480, "delay_time": 80, "base_price": 22, "xp_reward": 7},
    {"id": 6, "name": "Strawberry", "growth_time": 720, "delay_time": 150, "base_price": 50, "xp_reward": 18},
    {"id": 7, "name": "Pumpkin", "growth_time": 1800, "delay_time": 300, "base_price": 100, "xp_reward": 35},
    {"id": 8, "name": "Watermelon", "growth_time": 2400, "delay_time": 400, "base_price": 150, "xp_reward": 50},
]

# Seed data
SEEDS_DATA: list[dict[str, Any]] = [
    {"id": 1, "name": "Wheat Seeds", "crop_id": 1, "price": 5},
    {"id": 2, "name": "Corn Seeds", "crop_id": 2, "price": 10},
    {"id": 3, "name": "Carrot Seeds", "crop_id": 3, "price": 8},
    {"id": 4, "name": "Potato Seeds", "crop_id": 4, "price": 9},
    {"id": 5, "name": "Tomato Seeds", "crop_id": 5, "price": 7},
    {"id": 6, "name": "Strawberry Seeds", "crop_id": 6, "price": 20},
    {"id": 7, "name": "Pumpkin Seeds", "crop_id": 7, "price": 40},
    {"id": 8, "name": "Watermelon Seeds", "crop_id": 8, "price": 60},
]

# Animal data
ANIMALS_DATA: list[dict[str, Any]] = [
    {"id": 1, "name": "Chicken", "type": "poultry"},
    {"id": 2, "name": "Cow", "type": "livestock"},
    {"id": 3, "name": "Pig", "type": "livestock"},
    {"id": 4, "name": "Sheep", "type": "livestock"},
    {"id": 5, "name": "Duck", "type": "poultry"},
    {"id": 6, "name": "Goat", "type": "livestock"},
    {"id": 7, "name": "Rabbit", "type": "small"},
    {"id": 8, "name": "Bee", "type": "small"},
]

# Animal products data
ANIMAL_PRODUCTS_DATA: list[dict[str, Any]] = [
    # Chicken
    {"id": 1, "animal_id": 1, "name": "Egg", "base_price": 10, "xp_reward": 3, "is_optional": False},
    {"id": 2, "animal_id": 1, "name": "Feather", "base_price": 2, "xp_reward": 1, "is_optional": True},

    # Cow
    {"id": 3, "animal_id": 2, "name": "Milk", "base_price": 25, "xp_reward": 8, "is_optional": False},

    # Pig
    {"id": 4, "animal_id": 3, "name": "Truffle", "base_price": 100, "xp_reward": 35, "is_optional": False},

    # Sheep
    {"id": 5, "animal_id": 4, "name": "Wool", "base_price": 20, "xp_reward": 6, "is_optional": False},

    # Duck
    {"id": 6, "animal_id": 5, "name": "Duck Egg", "base_price": 15, "xp_reward": 4, "is_optional": False},
    {"id": 7, "animal_id": 5, "name": "Down Feather", "base_price": 5, "xp_reward": 2, "is_optional": True},

    # Goat
    {"id": 8, "animal_id": 6, "name": "Goat Milk", "base_price": 30, "xp_reward": 10, "is_optional": False},
    {"id": 9, "animal_id": 6, "name": "Cashmere", "base_price": 50, "xp_reward": 15, "is_optional": True},

    # Rabbit
    {"id": 10, "animal_id": 7, "name": "Rabbit Foot", "base_price": 75, "xp_reward": 25, "is_optional": False},
    {"id": 11, "animal_id": 7, "name": "Rabbit Fur", "base_price": 12, "xp_reward": 4, "is_optional": True},

    # Bee
    {"id": 12, "animal_id": 8, "name": "Honey", "base_price": 40, "xp_reward": 12, "is_optional": False},
    {"id": 13, "animal_id": 8, "name": "Beeswax", "base_price": 20, "xp_reward": 6, "is_optional": True},
    {"id": 14, "animal_id": 8, "name": "Royal Jelly", "base_price": 150, "xp_reward": 50, "is_optional": True},
]

# Items (tools, rods, bait, consumables)
ITEMS_DATA: list[dict[str, Any]] = [
    # Tools
    {"id": 1, "type": "tool", "name": "Basic Shovel", "price": 50, "description": "A simple shovel for digging", "attributes": {"durability": 100}},
    {"id": 2, "type": "tool", "name": "Steel Shovel", "price": 150, "description": "A sturdy steel shovel", "attributes": {"durability": 250}},
    {"id": 3, "type": "tool", "name": "Golden Shovel", "price": 500, "description": "A fancy golden shovel", "attributes": {"durability": 500, "luck_bonus": 0.1}},

    # Fishing Rods
    {"id": 10, "type": "rod", "name": "Basic Rod", "price": 100, "description": "A simple fishing rod", "attributes": {"strength": 1, "sensitivity": 1}},
    {"id": 11, "type": "rod", "name": "Fiberglass Rod", "price": 250, "description": "Lightweight fiberglass rod", "attributes": {"strength": 2, "sensitivity": 2}},
    {"id": 12, "type": "rod", "name": "Carbon Fiber Rod", "price": 600, "description": "Professional carbon fiber rod", "attributes": {"strength": 3, "sensitivity": 3}},
    {"id": 13, "type": "rod", "name": "Golden Rod", "price": 1500, "description": "Legendary golden fishing rod", "attributes": {"strength": 5, "sensitivity": 5, "luck_bonus": 0.2}},

    # Bait
    {"id": 20, "type": "bait", "name": "Worms", "price": 5, "description": "Basic fishing bait", "attributes": {"effectiveness": 1}},
    {"id": 21, "type": "bait", "name": "Cricket", "price": 10, "description": "Live cricket bait", "attributes": {"effectiveness": 1.5}},
    {"id": 22, "type": "bait", "name": "Artificial Lure", "price": 25, "description": "Fancy artificial lure", "attributes": {"effectiveness": 2}},
    {"id": 23, "type": "bait", "name": "Magic Bait", "price": 100, "description": "Attracts rare fish", "attributes": {"effectiveness": 3, "rarity_bonus": 0.15}},

    # Feed
    {"id": 30, "type": "feed", "name": "Basic Feed", "price": 10, "description": "Standard animal feed", "attributes": {"nutrition": 1}},
    {"id": 31, "type": "feed", "name": "Premium Feed", "price": 30, "description": "High-quality animal feed", "attributes": {"nutrition": 2}},
    {"id": 32, "type": "feed", "name": "Organic Feed", "price": 50, "description": "Organic premium feed", "attributes": {"nutrition": 2.5, "happiness_bonus": 5}},
    {"id": 33, "type": "feed", "name": "Golden Feed", "price": 150, "description": "Magical feed for legendary results", "attributes": {"nutrition": 5, "happiness_bonus": 10, "product_quality": 1.5}},

    # Consumables
    {"id": 40, "type": "consumable", "name": "Health Potion", "price": 50, "description": "Restores health to crops", "attributes": {"health_restore": 50}},
    {"id": 41, "type": "consumable", "name": "Growth Serum", "price": 100, "description": "Speeds up crop growth", "attributes": {"growth_speed": 2.0}},
    {"id": 42, "type": "consumable", "name": "Fertilizer", "price": 30, "description": "Boosts crop yield", "attributes": {"yield_bonus": 0.25}},
]

# Export all data for seeding
def get_all_seed_data() -> dict[str, list[dict[str, Any]]]:
    """Get all seed data as a dictionary."""
    return {
        "fish": FISH_DATA,
        "crops": CROPS_DATA,
        "seeds": SEEDS_DATA,
        "animals": ANIMALS_DATA,
        "animal_products": ANIMAL_PRODUCTS_DATA,
        "items": ITEMS_DATA,
    }
