"""Unit tests for User model."""

import pytest
from src.core.models.user import User
from src.core.exceptions import InsufficientFundsError


class TestUser:
    """Tests for User model."""

    def test_create_user(self):
        """Test user creation."""
        user = User.create("testuser", "Test User", "password123")
        assert user.username == "testuser"
        assert user.nickname == "Test User"
        assert user.level == 1
        assert user.balance == 500
        assert user.xp == 0
        assert user.verify_password("password123")

    def test_password_hashing(self):
        """Test password is properly hashed."""
        user = User.create("test", "Test", "mypassword")
        assert not user.verify_password("wrongpassword")
        assert user.verify_password("mypassword")

    def test_add_coins(self):
        """Test adding coins."""
        user = User.create("test", "Test", "pass")
        user.add_coins(100)
        assert user.balance == 600

    def test_deduct_coins(self):
        """Test deducting coins."""
        user = User.create("test", "Test", "pass")
        assert user.deduct(100)
        assert user.balance == 400

    def test_deduct_insufficient(self):
        """Test deducting more than balance."""
        user = User.create("test", "Test", "pass")
        assert not user.deduct(1000)

    def test_add_xp_level_up(self):
        """Test XP and level up mechanics."""
        user = User.create("test", "Test", "pass")
        # Add enough XP to level up
        leveled_up = user.add_xp(150)  # Need 100 for level 1->2
        assert leveled_up
        assert user.level == 2

    def test_xp_for_next_level(self):
        """Test XP calculation for levels."""
        user = User.create("test", "Test", "pass")
        assert user.xp_for_next_level() == 100

        user.level = 5
        assert user.xp_for_next_level() == 500

    def test_guest_user(self):
        """Test guest user creation."""
        guest = User.create_guest()
        assert guest.is_guest
        assert guest.username.startswith("guest_")

    def test_can_afford(self):
        """Test can_afford helper."""
        user = User.create("test", "Test", "pass")
        assert user.can_afford(500)
        assert user.can_afford(100)
        assert not user.can_afford(501)
