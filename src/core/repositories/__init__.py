"""Repositories for data access layer."""

from __future__ import annotations

from src.core.repositories.user_repository import UserRepository
from src.core.repositories.inventory_repository import InventoryRepository
from src.core.repositories.farm_repository import FarmRepository
from src.core.repositories.game_data_repository import GameDataRepository

__all__ = [
    "UserRepository",
    "InventoryRepository",
    "FarmRepository",
    "GameDataRepository",
]
