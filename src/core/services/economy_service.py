"""Economy service for work, trade, and crime mechanics."""

from __future__ import annotations

import random
from typing import Optional, Tuple

from src.core.models.user import User
from src.core.models.game_data import Item


class EconomyService:
    """Service for economy-related operations."""

    # Work rewards by level
    WORK_BASE_REWARD = 20
    WORK_XP_BASE = 5

    # Crime settings
    CRIME_SETTINGS = {
        1: {"name": "Pickpocket", "min_reward": 10, "max_reward": 50, "risk": 0.3, "xp": 5},
        2: {"name": "Heist", "min_reward": 50, "max_reward": 200, "risk": 0.6, "xp": 15},
    }

    def get_work_reward(self, level: int) -> int:
        """Calculate expected work reward based on level."""
        return self.WORK_BASE_REWARD + (level * 5)

    def work(self, user: User, times: int = 1) -> Tuple[int, int]:
        """Perform work action.

        Returns:
            Tuple of (coins_earned, xp_earned)
        """
        base_reward = self.get_work_reward(user.level)

        # Add some variance
        variance = random.randint(-base_reward // 10, base_reward // 10)
        coins = max(1, (base_reward + variance) * times)

        xp = (self.WORK_XP_BASE + user.level) * times

        return coins, xp

    def crime(self, user: User, crime_type: int) -> Tuple[bool, str, int, int]:
        """Attempt a crime.

        Returns:
            Tuple of (success, message, coins, xp)
        """
        settings = self.CRIME_SETTINGS.get(crime_type, self.CRIME_SETTINGS[1])

        # Roll for success
        roll = random.random()
        success = roll > settings["risk"]

        if success:
            coins = random.randint(settings["min_reward"], settings["max_reward"])
            # Level bonus
            coins = int(coins * (1 + user.level * 0.1))
            xp = settings["xp"]
            message = f"{settings['name']} successful!"
            return True, message, coins, xp
        else:
            # Failed - possible penalty
            penalty_chance = random.random()
            if penalty_chance < 0.5:
                # Lose some coins
                penalty = random.randint(10, 50)
                message = f"Caught! Paid {penalty} 🪙 fine"
                return False, message, -penalty, 0
            else:
                message = f"{settings['name']} failed, but you got away"
                return False, message, 0, 0

    def get_sell_price(self, item: Item) -> int:
        """Calculate sell price for an item (70% of buy price)."""
        if item.price:
            return int(item.price * 0.7)
        return 10  # Default sell price

    def calculate_trade_profit(self, buy_price: int, sell_price: int) -> int:
        """Calculate trade profit/loss."""
        return sell_price - buy_price
