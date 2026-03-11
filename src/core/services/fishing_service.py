"""Fishing service for catching fish mechanics."""

from __future__ import annotations

import random
from typing import List, Optional

from src.core.models.game_data import Fish, Habitat, Rarity
from src.db.sqlite_manager import get_db


class FishingService:
    """Service for fishing operations."""

    # Location difficulty modifiers
    LOCATION_MODIFIERS = {
        "pond": {"rarity_bonus": -0.1, "catch_rate": 0.8},
        "river": {"rarity_bonus": 0.0, "catch_rate": 0.7},
        "lake": {"rarity_bonus": 0.1, "catch_rate": 0.6},
        "ocean": {"rarity_bonus": 0.2, "catch_rate": 0.5},
    }

    # Rarity weights
    RARITY_WEIGHTS = {
        Rarity.COMMON: 50,
        Rarity.UNCOMMON: 30,
        Rarity.RARE: 15,
        Rarity.LEGENDARY: 5,
    }

    def __init__(self):
        self.db = get_db()

    def get_available_fish(self, location: str, player_level: int) -> List[Fish]:
        """Get fish available at a location for a player level."""
        from src.core.repositories.game_data_repository import GameDataRepository

        repo = GameDataRepository()
        all_fish = repo.get_all_fish()

        available = []
        for fish in all_fish:
            if fish.habitat == location or location == "ocean":
                # Level gate for rare fish
                if fish.rarity == Rarity.LEGENDARY and player_level < 5:
                    continue
                if fish.rarity == Rarity.RARE and player_level < 3:
                    continue
                available.append(fish)

        return available

    def catch_fish(self, location: str, player_level: int, rod_bonus: float = 1.0) -> Optional[Fish]:
        """Attempt to catch a fish.

        Args:
            location: Fishing location (pond, river, lake, ocean)
            player_level: Player's current level
            rod_bonus: Multiplier from equipped rod

        Returns:
            Fish if caught, None if failed
        """
        # Get location modifier
        modifier = self.LOCATION_MODIFIERS.get(location, {"rarity_bonus": 0, "catch_rate": 0.7})

        # Base catch rate with modifier
        catch_rate = modifier["catch_rate"] + (player_level * 0.02)
        catch_rate *= rod_bonus

        # Roll for catch
        if random.random() > catch_rate:
            return None  # Failed to catch

        # Get available fish
        available = self.get_available_fish(location, player_level)
        if not available:
            return None

        # Adjust weights based on location rarity bonus
        adjusted_weights = {}
        for fish in available:
            base_weight = self.RARITY_WEIGHTS.get(fish.rarity, 10)
            # Apply location and level modifiers
            if fish.rarity == Rarity.LEGENDARY:
                base_weight += modifier["rarity_bonus"] * 5
            elif fish.rarity == Rarity.RARE:
                base_weight += modifier["rarity_bonus"] * 10

            adjusted_weights[fish] = max(1, int(base_weight))

        # Weighted random selection
        fish_list = list(adjusted_weights.keys())
        weights = list(adjusted_weights.values())

        return random.choices(fish_list, weights=weights, k=1)[0]

    def get_fish_value(self, fish: Fish, weight: float) -> int:
        """Calculate the sell value of a fish based on weight."""
        return int(fish.base_price * weight)

    def get_fish_description(self, fish: Fish) -> str:
        """Get a descriptive string for a fish."""
        return f"{fish.rarity.value.title()} {fish.name} - {fish.base_price} 🪙 base"
