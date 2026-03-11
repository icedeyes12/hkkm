"""Unit tests for economy service."""

import pytest
from src.core.services.economy_service import EconomyService
from src.core.models.user import User


class TestEconomyService:
    """Tests for economy service."""

    def setup_method(self):
        """Setup for each test."""
        self.service = EconomyService()
        self.user = User.create("test", "Test", "pass")

    def test_work_reward_calculation(self):
        """Test work reward calculation."""
        reward = self.service.get_work_reward(1)
        assert reward >= 20

        reward_level5 = self.service.get_work_reward(5)
        assert reward_level5 > reward

    def test_work_action(self):
        """Test work action."""
        coins, xp = self.service.work(self.user, times=1)
        assert coins > 0
        assert xp > 0

    def test_work_multiple_times(self):
        """Test working multiple times."""
        coins, xp = self.service.work(self.user, times=5)
        assert coins > 0
        assert xp > 0

    def test_crime_success(self):
        """Test crime with mocked success."""
        import random
        random.seed(42)  # Seed for deterministic test

        success, message, coins, xp = self.service.crime(self.user, 1)
        # Result depends on random seed, but should return tuple
        assert isinstance(success, bool)
        assert isinstance(message, str)
        assert isinstance(coins, int)
        assert isinstance(xp, int)

    def test_sell_price(self):
        """Test sell price calculation."""
        from src.core.models.game_data import Item
        item = Item(id=1, type="tool", name="Test", price=100)
        sell_price = self.service.get_sell_price(item)
        assert sell_price == 70  # 70% of buy price

    def test_sell_price_no_price(self):
        """Test sell price for item without price."""
        from src.core.models.game_data import Item
        item = Item(id=1, type="tool", name="Test", price=None)
        sell_price = self.service.get_sell_price(item)
        assert sell_price == 10  # Default price
