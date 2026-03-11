"""Repository for static game data (fish, crops, animals, items)."""

from __future__ import annotations

from typing import Optional

from src.core.models.game_data import Animal, AnimalProduct, Crop, Fish, Habitat, Item, Rarity, Seed
from src.db.sqlite_manager import SQLiteManager


class GameDataRepository:
    """Repository for static game content."""

    def __init__(self, db: Optional[SQLiteManager] = None) -> None:
        """Initialize with database manager."""
        self.db = db or SQLiteManager()

    # Fish operations

    def get_all_fish(self) -> list[Fish]:
        """Get all fish definitions."""
        rows = self.db.fetchall("SELECT * FROM fish ORDER BY rarity, name")
        return [self._row_to_fish(row) for row in rows]

    def get_fish_by_id(self, fish_id: int) -> Optional[Fish]:
        """Get fish by ID."""
        row = self.db.fetchone("SELECT * FROM fish WHERE id = ?", (fish_id,))
        if not row:
            return None
        return self._row_to_fish(row)

    def get_fish_by_habitat(self, habitat: Habitat | str) -> list[Fish]:
        """Get fish by habitat."""
        habitat_str = habitat.value if isinstance(habitat, Habitat) else habitat
        rows = self.db.fetchall(
            "SELECT * FROM fish WHERE habitat = ? ORDER BY rarity, name",
            (habitat_str,),
        )
        return [self._row_to_fish(row) for row in rows]

    def get_fish_by_rarity(self, rarity: Rarity | str) -> list[Fish]:
        """Get fish by rarity."""
        rarity_str = rarity.value if isinstance(rarity, Rarity) else rarity
        rows = self.db.fetchall(
            "SELECT * FROM fish WHERE rarity = ? ORDER BY name",
            (rarity_str,),
        )
        return [self._row_to_fish(row) for row in rows]

    # Crop operations

    def get_all_crops(self) -> list[Crop]:
        """Get all crop definitions."""
        rows = self.db.fetchall("SELECT * FROM crops ORDER BY name")
        return [self._row_to_crop(row) for row in rows]

    def get_crop_by_id(self, crop_id: int) -> Optional[Crop]:
        """Get crop by ID."""
        row = self.db.fetchone("SELECT * FROM crops WHERE id = ?", (crop_id,))
        if not row:
            return None
        return self._row_to_crop(row)

    # Seed operations

    def get_all_seeds(self) -> list[Seed]:
        """Get all seed definitions."""
        rows = self.db.fetchall("SELECT * FROM seeds ORDER BY name")
        return [self._row_to_seed(row) for row in rows]

    def get_seed_by_id(self, seed_id: int) -> Optional[Seed]:
        """Get seed by ID."""
        row = self.db.fetchone("SELECT * FROM seeds WHERE id = ?", (seed_id,))
        if not row:
            return None
        return self._row_to_seed(row)

    def get_seeds_for_crop(self, crop_id: int) -> list[Seed]:
        """Get seeds that produce a specific crop."""
        rows = self.db.fetchall(
            "SELECT * FROM seeds WHERE crop_id = ? ORDER BY price",
            (crop_id,),
        )
        return [self._row_to_seed(row) for row in rows]

    # Animal operations

    def get_all_animals(self) -> list[Animal]:
        """Get all animal definitions."""
        rows = self.db.fetchall("SELECT * FROM animals ORDER BY type, name")
        return [self._row_to_animal(row) for row in rows]

    def get_animal_by_id(self, animal_id: int) -> Optional[Animal]:
        """Get animal by ID."""
        row = self.db.fetchone("SELECT * FROM animals WHERE id = ?", (animal_id,))
        if not row:
            return None
        return self._row_to_animal(row)

    def get_animals_by_type(self, animal_type: str) -> list[Animal]:
        """Get animals by type."""
        rows = self.db.fetchall(
            "SELECT * FROM animals WHERE type = ? ORDER BY name",
            (animal_type,),
        )
        return [self._row_to_animal(row) for row in rows]

    # Animal Product operations

    def get_all_animal_products(self) -> list[AnimalProduct]:
        """Get all animal product definitions."""
        rows = self.db.fetchall(
            "SELECT * FROM animal_products ORDER BY animal_id, name"
        )
        return [self._row_to_product(row) for row in rows]

    def get_products_by_animal(self, animal_id: int) -> list[AnimalProduct]:
        """Get products produced by a specific animal."""
        rows = self.db.fetchall(
            "SELECT * FROM animal_products WHERE animal_id = ? ORDER BY is_optional, name",
            (animal_id,),
        )
        return [self._row_to_product(row) for row in rows]

    def get_product_by_id(self, product_id: int) -> Optional[AnimalProduct]:
        """Get product by ID."""
        row = self.db.fetchone(
            "SELECT * FROM animal_products WHERE id = ?", (product_id,)
        )
        if not row:
            return None
        return self._row_to_product(row)

    # Item operations

    def get_all_items(self) -> list[Item]:
        """Get all shop items."""
        import json

        rows = self.db.fetchall("SELECT * FROM items ORDER BY type, name")
        return [self._row_to_item(row) for row in rows]

    def get_items_by_type(self, item_type: str) -> list[Item]:
        """Get items by type."""
        import json

        rows = self.db.fetchall(
            "SELECT * FROM items WHERE type = ? ORDER BY name",
            (item_type,),
        )
        return [self._row_to_item(row) for row in rows]

    def get_item_by_id(self, item_id: int) -> Optional[Item]:
        """Get item by ID."""
        import json

        row = self.db.fetchone("SELECT * FROM items WHERE id = ?", (item_id,))
        if not row:
            return None
        return self._row_to_item(row)

    def search_items(self, query: str) -> list[Item]:
        """Search items by name."""
        import json

        rows = self.db.fetchall(
            "SELECT * FROM items WHERE name LIKE ? ORDER BY name",
            (f"%{query}%",),
        )
        return [self._row_to_item(row) for row in rows]

    # Conversion methods

    def _row_to_fish(self, row: dict) -> Fish:
        """Convert row to Fish model."""
        return Fish(
            id=row["id"],
            name=row["name"],
            rarity=Rarity(row["rarity"]),
            base_price=row["base_price"],
            xp_reward=row["xp_reward"],
            min_weight=row["min_weight"],
            max_weight=row["max_weight"],
            habitat=Habitat(row["habitat"]),
        )

    def _row_to_crop(self, row: dict) -> Crop:
        """Convert row to Crop model."""
        return Crop(
            id=row["id"],
            name=row["name"],
            growth_time=row["growth_time"],
            delay_time=row["delay_time"],
            base_price=row["base_price"],
            xp_reward=row["xp_reward"],
        )

    def _row_to_seed(self, row: dict) -> Seed:
        """Convert row to Seed model."""
        return Seed(
            id=row["id"],
            name=row["name"],
            crop_id=row["crop_id"],
            price=row["price"],
        )

    def _row_to_animal(self, row: dict) -> Animal:
        """Convert row to Animal model."""
        return Animal(
            id=row["id"],
            name=row["name"],
            type=row["type"],
        )

    def _row_to_product(self, row: dict) -> AnimalProduct:
        """Convert row to AnimalProduct model."""
        return AnimalProduct(
            id=row["id"],
            animal_id=row["animal_id"],
            name=row["name"],
            base_price=row["base_price"],
            xp_reward=row["xp_reward"],
            is_optional=bool(row["is_optional"]),
        )

    def _row_to_item(self, row: dict) -> Item:
        """Convert row to Item model."""
        import json

        return Item(
            id=row["id"],
            type=row["type"],
            name=row["name"],
            price=row["price"],
            description=row["description"] or "",
            attributes=json.loads(row["attributes"] or "{}"),
        )
