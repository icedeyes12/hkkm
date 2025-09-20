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