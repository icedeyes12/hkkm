# utils/game_data.py
from utils.db import read_db

def get_all_fish():
    """Get all fish data"""
    return read_db("fishdb").get("fish", [])

def get_fish_by_habitat(habitat):
    """Get fish available in a specific habitat"""
    all_fish = get_all_fish()
    return [fish for fish in all_fish if fish.get("habitat") == habitat]

def get_fish_by_id(fish_id):
    """Get a specific fish by ID"""
    all_fish = get_all_fish()
    for fish in all_fish:
        if fish["id"] == fish_id:
            return fish
    return None

def get_fish_by_rarity(rarity):
    """Get fish of a specific rarity"""
    all_fish = get_all_fish()
    return [fish for fish in all_fish if fish.get("rarity") == rarity]

def get_all_crops():
    """Get all crops data"""
    return read_db("cropsdb").get("crops", [])

def get_crop_by_name(crop_name):
    """Get crop data by name"""
    crops = get_all_crops()
    for crop in crops:
        if crop["name"].lower() == crop_name.lower():
            return crop
    return None

def get_crop_by_id(crop_id):
    """Get crop data by ID"""
    crops = get_all_crops()
    for crop in crops:
        if crop["id"] == crop_id:
            return crop
    return None

def get_all_seeds():
    """Get all seeds data"""
    return read_db("cropsdb").get("seeds", [])

def get_seed_by_crop(crop_name):
    """Get seed data for a specific crop"""
    seeds = get_all_seeds()
    for seed in seeds:
        if seed["crop"].lower() == crop_name.lower():
            return seed
    return None

def get_all_animals():
    """Get all animals data"""
    return read_db("animals").get("animals", [])

def get_animal_by_id(animal_id):
    """Get a specific animal by ID"""
    animals = get_all_animals()
    for animal in animals:
        if animal["id"] == animal_id:
            return animal
    return None

def get_animal_by_name(animal_name):
    """Get animal data by name"""
    animals = get_all_animals()
    for animal in animals:
        if animal["name"].lower() == animal_name.lower():
            return animal
    return None

def get_animal_products(animal_id):
    """Get products for a specific animal"""
    animal = get_animal_by_id(animal_id)
    return animal.get("products", []) if animal else []