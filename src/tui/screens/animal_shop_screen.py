"""Animal shop screen for buying animals."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Label, Static

from src.core.models.user import User
from src.core.repositories.game_data_repository import GameDataRepository
from src.core.repositories.farm_repository import FarmRepository
from src.core.repositories.user_repository import UserRepository


class AnimalShopScreen(Screen):
    """Screen for buying animals."""

    def __init__(self, user: User, slot_id: int):
        super().__init__()
        self.user = user
        self.slot_id = slot_id
        self.game_data_repo = GameDataRepository()
        self.farm_repo = FarmRepository()
        self.user_repo = UserRepository()

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog"):
            yield Label("🐄 Animal Shop", classes="dialog-title")
            yield Static(f"Your balance: {self.user.balance} 🪙")

            table = DataTable(id="animal-table")
            table.cursor_type = "row"
            yield table

            yield Static("", id="buy-result")
            yield Button("Close", id="btn-close")

    def on_mount(self):
        """Load animals."""
        table = self.query_one("#animal-table", DataTable)
        table.add_columns("Animal", "Type", "Price", "Product", "Action")

        animals = self.game_data_repo.get_all_animals()
        for animal in animals:
            products = self.game_data_repo.get_animal_products(animal.id)
            product_names = ", ".join([p.name for p in products[:2]]) if products else "None"

            table.add_row(
                animal.name,
                animal.type,
                f"{animal.price} 🪙" if hasattr(animal, 'price') else "N/A",
                product_names,
                "Buy",
                key=f"buy-{animal.id}",
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle buy selection."""
        row_key = str(event.row_key)
        result = self.query_one("#buy-result", Static)

        if row_key.startswith("buy-"):
            animal_id = int(row_key.replace("buy-", ""))
            self._buy_animal(animal_id, result)

    def _buy_animal(self, animal_id: int, result: Static):
        """Buy an animal."""
        animal = self.game_data_repo.get_animal(animal_id)
        if not animal:
            result.update("❌ Animal not found")
            return

        # Determine price (use a default if not set)
        price = getattr(animal, 'price', 500)

        if self.user.balance < price:
            result.update(f"❌ Not enough coins (need {price} 🪙)")
            return

        # Update slot
        from datetime import datetime
        slot = self.farm_repo.get_barn_slot(self.slot_id)
        if slot:
            from datetime import timedelta
            slot.animal_id = animal_id
            slot.acquired_at = datetime.now()
            slot.last_fed = datetime.now()
            slot.happiness = 50
            slot.product_ready_at = datetime.now() + timedelta(hours=1)
            self.farm_repo.update_barn_slot(slot)

            # Deduct coins
            self.user.deduct(price)
            self.user_repo.update(self.user)

            result.update(f"✅ Bought {animal.name} for {price} 🪙")
            self.set_timer(1.5, self.dismiss)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle buttons."""
        if event.button.id == "btn-close":
            self.dismiss()
