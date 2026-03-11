"""Trading screen for buy/sell transactions."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Label, Static

from src.core.models.user import User
from src.core.repositories.inventory_repository import InventoryRepository
from src.core.repositories.game_data_repository import GameDataRepository
from src.core.repositories.user_repository import UserRepository
from src.core.services.economy_service import EconomyService


class TradingScreen(Screen):
    """Trading post screen."""

    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.inventory_repo = InventoryRepository()
        self.game_data_repo = GameDataRepository()
        self.user_repo = UserRepository()
        self.economy = EconomyService()
        self.mode = "buy"  # or "sell"

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog"):
            yield Label("📊 Trading Post", classes="dialog-title")
            yield Static(f"Your balance: {self.user.balance} 🪙", id="balance-display")

            with Horizontal():
                yield Button("Buy", id="btn-buy", variant="primary" if self.mode == "buy" else "default")
                yield Button("Sell", id="btn-sell", variant="primary" if self.mode == "sell" else "default")

            table = DataTable(id="trading-table")
            table.cursor_type = "row"
            yield table

            yield Static("", id="trade-result")
            yield Button("Close", id="btn-close")

    def on_mount(self):
        """Load initial data."""
        self._load_buy_table()

    def _load_buy_table(self):
        """Load items available to buy."""
        table = self.query_one("#trading-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Item", "Type", "Price", "Action")

        items = self.game_data_repo.get_all_items()
        for item in items:
            table.add_row(
                item.name,
                item.type,
                f"{item.price} 🪙",
                "Buy",
                key=f"buy-{item.id}",
            )

    def _load_sell_table(self):
        """Load items in inventory to sell."""
        table = self.query_one("#trading-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Item", "Type", "Qty", "Sell Price", "Action")

        inventory = self.inventory_repo.get_user_inventory(self.user.id)
        for item in inventory:
            # Get item details
            item_details = self.game_data_repo.get_item(item.item_id)
            if item_details:
                sell_price = self.economy.get_sell_price(item_details)
                table.add_row(
                    item_details.name,
                    item.item_type_str,
                    str(item.quantity),
                    f"{sell_price} 🪙",
                    "Sell",
                    key=f"sell-{item.id}-{item.item_type_str}-{item.item_id}",
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        if btn_id == "btn-buy":
            self.mode = "buy"
            self._load_buy_table()
        elif btn_id == "btn-sell":
            self.mode = "sell"
            self._load_sell_table()
        elif btn_id == "btn-close":
            self.dismiss()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection for trading."""
        row_key = str(event.row_key)
        result_static = self.query_one("#trade-result", Static)

        if row_key.startswith("buy-"):
            item_id = int(row_key.replace("buy-", ""))
            self._buy_item(item_id, result_static)
        elif row_key.startswith("sell-"):
            parts = row_key.split("-")
            item_id = int(parts[1])
            item_type = parts[2]
            self._sell_item(item_id, item_type, result_static)

    def _buy_item(self, item_id: int, result_static: Static):
        """Buy an item."""
        item = self.game_data_repo.get_item(item_id)
        if not item:
            result_static.update("❌ Item not found")
            return

        if self.user.balance < item.price:
            result_static.update(f"❌ Not enough coins (need {item.price} 🪙)")
            return

        # Deduct coins and add to inventory
        self.user.deduct(item.price)
        self.inventory_repo.add_item(
            self.user.id,
            self.inventory_repo._item_type_from_string(item.type),
            item.id,
            1,
        )
        self.user_repo.update(self.user)

        result_static.update(f"✅ Bought {item.name} for {item.price} 🪙")
        self._update_balance_display()

    def _sell_item(self, item_id: int, item_type: str, result_static: Static):
        """Sell an item."""
        # Find item in inventory
        inventory = self.inventory_repo.get_user_inventory(self.user.id)
        inv_item = None
        for inv in inventory:
            if inv.item_id == item_id and inv.item_type_str == item_type:
                inv_item = inv
                break

        if not inv_item or inv_item.quantity < 1:
            result_static.update("❌ You don't have this item")
            return

        # Get sell price
        item_details = self.game_data_repo.get_item(item_id)
        if not item_details:
            result_static.update("❌ Item details not found")
            return

        sell_price = self.economy.get_sell_price(item_details)

        # Remove from inventory and add coins
        self.inventory_repo.remove_item(self.user.id, inv_item.item_type, item_id, 1)
        self.user.add_coins(sell_price)
        self.user_repo.update(self.user)

        result_static.update(f"✅ Sold {item_details.name} for {sell_price} 🪙")
        self._update_balance_display()
        self._load_sell_table()  # Refresh inventory display

    def _update_balance_display(self):
        """Update balance display."""
        balance_static = self.query_one("#balance-display", Static)
        balance_static.update(f"Your balance: {self.user.balance} 🪙")
