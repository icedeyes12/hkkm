"""Static game data models (fish, crops, animals, items)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Rarity(Enum):
    """Item/fish rarity levels."""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    LEGENDARY = "legendary"


class Habitat(Enum):
    """Fishing habitats."""

    POND = "pond"
    RIVER = "river"
    LAKE = "lake"
    OCEAN = "ocean"


@dataclass
class Fish:
    """Fish data for fishing system."""

    id: int
    name: str
    rarity: Rarity
    base_price: int
    xp_reward: int
    min_weight: float
    max_weight: float
    habitat: Habitat

    @property
    def avg_weight(self) -> float:
        """Calculate average weight."""
        return (self.min_weight + self.max_weight) / 2

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "rarity": self.rarity.value,
            "base_price": self.base_price,
            "xp_reward": self.xp_reward,
            "min_weight": self.min_weight,
            "max_weight": self.max_weight,
            "habitat": self.habitat.value,
        }


@dataclass
class Crop:
    """Crop growing data."""

    id: int
    name: str
    growth_time: int  # seconds
    delay_time: int  # seconds between growth stages
    base_price: int
    xp_reward: int

    @property
    def total_growth_time(self) -> int:
        """Total time from seed to harvest."""
        return self.growth_time + self.delay_time

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "growth_time": self.growth_time,
            "delay_time": self.delay_time,
            "base_price": self.base_price,
            "xp_reward": self.xp_reward,
        }


@dataclass
class Seed:
    """Seed item data."""

    id: int
    name: str
    crop_id: int
    price: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "crop_id": self.crop_id,
            "price": self.price,
        }


@dataclass
class Animal:
    """Animal data for livestock."""

    id: int
    name: str
    type: str  # e.g., "chicken", "cow", "pig"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
        }


@dataclass
class AnimalProduct:
    """Product from animals (eggs, milk, etc.)."""

    id: int
    animal_id: int
    name: str
    base_price: int
    xp_reward: int
    is_optional: bool = False  # Some animals produce multiple things

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "animal_id": self.animal_id,
            "name": self.name,
            "base_price": self.base_price,
            "xp_reward": self.xp_reward,
            "is_optional": self.is_optional,
        }


@dataclass
class Item:
    """Generic shop item."""

    id: int
    type: str  # 'tool', 'rod', 'bait', 'seed', 'feed', 'consumable'
    name: str
    price: int
    description: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "attributes": self.attributes,
        }
