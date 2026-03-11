"""Fishing widget for catching fish."""

from __future__ import annotations

import random
from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Label, ProgressBar, Static

from src.core.models.user import User
from src.core.repositories.activity_repository import ActivityRepository
from src.core.repositories.game_data_repository import GameDataRepository
from src.core.repositories.inventory_repository import InventoryRepository, ItemType
from src.core.repositories.user_repository import UserRepository
from src.core.services.fishing_service import FishingService


class FishingWidget(Static):
    """Fishing section with different locations and rods."""

    fishing = reactive(False)
    cast_progress = reactive(0.0)

    LOCATIONS = [
        ("🌊 Pond", "pond", "Beginner-friendly, common fish"),
        ("🏞️ River", "river", "Medium difficulty, variety of fish"),
        ("🌅 Lake", "lake", "Harder, bigger rewards"),
        ("🌊 Ocean", "ocean", "Expert only, legendary fish"),
    ]

    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.fishing_service = FishingService()
        self.game_data_repo = GameDataRepository()
        self.inventory_repo = InventoryRepository()
        self.user_repo = UserRepository()
        self.activity_repo = ActivityRepository()
        self.current_location = "pond"

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("🎣 Fishing", classes="section-title")

            with Horizontal():
                yield Label("Location:")
                for name, key, _ in self.LOCATIONS:
                    variant = "primary" if key == self.current_location else "default"
                    yield Button(name, id=f"loc-{key}", variant=variant)

            location_desc = next((desc for _, key, desc in self.LOCATIONS if key == self.current_location), "")
            yield Static(location_desc, id="location-desc")

            yield Static("", id="fishing-status")

            with Horizontal():
                yield Button("🎣 Cast Line", id="btn-cast", variant="primary")
                yield Button("📦 Check Tackle Box", id="btn-tackle")

            yield Static("", id="catch-result")

            yield Label("🎣 Your Catches:")
            catches = self.inventory_repo.get_items_by_type(self.user.id, ItemType.FISH)
            if catches:
                for catch in catches:
                    fish = self.game_data_repo.get_fish(catch.item_id)
                    if fish:
                        yield Static(f"  {fish.rarity.value} {fish.name} x{catch.quantity}")
            else:
                yield Static("  No fish caught yet!")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        if btn_id and btn_id.startswith("loc-"):
            self.current_location = btn_id.replace("loc-", "")
            self._update_location_buttons()
        elif btn_id == "btn-cast":
            self._cast_line()
        elif btn_id == "btn-tackle":
            self._show_tackle_box()

    def _update_location_buttons(self):
        """Update location button styling."""
        for name, key, _ in self.LOCATIONS:
            btn = self.query_one(f"#loc-{key}", Button)
            btn.variant = "primary" if key == self.current_location else "default"

        desc = next((desc for _, key, desc in self.LOCATIONS if key == self.current_location), "")
        self.query_one("#location-desc", Static).update(desc)

    def _cast_line(self):
        """Cast fishing line."""
        if self.fishing:
            return

        result = self.query_one("#catch-result", Static)

        # Check for rod
        rods = self.inventory_repo.get_items_by_type(self.user.id, ItemType.ROD)
        if not rods:
            result.update("❌ You need a fishing rod! Buy one from the shop.")
            return

        self.fishing = True
        status = self.query_one("#fishing-status", Static)
        status.update("🎣 Casting line...")

        # Simulate fishing
        import asyncio

        async def do_fish():
            await asyncio.sleep(2)  # Wait for bite

            # Catch logic
            fish = self.fishing_service.catch_fish(self.current_location, self.user.level)

            if fish:
                # Calculate weight
                weight = random.uniform(fish.min_weight or 0.1, fish.max_weight or 1.0)
                value = int(fish.base_price * weight)
                xp = fish.xp_reward

                # Add to inventory
                self.inventory_repo.add_item(self.user.id, ItemType.FISH, fish.id, 1,
                    metadata={"weight": weight, "caught_at": datetime.now().isoformat()})

                # Rewards
                self.user.add_coins(value)
                self.user.add_xp(xp)
                self.user_repo.update(self.user)

                self.activity_repo.log(self.user.id, "fish_caught",
                    {"fish": fish.name, "weight": weight, "value": value, "location": self.current_location})

                status.update("")
                result.update(f"🎣 Caught a {weight:.1f}kg {fish.rarity.value} {fish.name}!\n   💰 {value} 🪙 | ⭐ {xp} XP")
            else:
                status.update("")
                result.update("🎣 The fish got away...")

            self.fishing = False
            self._refresh_stats()

        self.run_worker(do_fish())

    def _show_tackle_box(self):
        """Show fishing equipment."""
        rods = self.inventory_repo.get_items_by_type(self.user.id, ItemType.ROD)
        baits = self.inventory_repo.get_items_by_type(self.user.id, ItemType.BAIT)

        msg = "🎣 Tackle Box:\n"
        if rods:
            for rod in rods:
                rod_data = self.game_data_repo.get_item(rod.item_id)
                name = rod_data.name if rod_data else f"Rod #{rod.item_id}"
                msg += f"  Rod: {name}\n"
        else:
            msg += "  No rods!\n"

        if baits:
            msg += f"  Baits: {sum(b.quantity for b in baits)}\n"
        else:
            msg += "  No bait\n"

        self.notify(msg)

    def _refresh_stats(self):
        """Refresh parent stats."""
        try:
            parent = self.parent
            if parent and hasattr(parent, "refresh_user_stats"):
                parent.refresh_user_stats()
        except:
            pass
