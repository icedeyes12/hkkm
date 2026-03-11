"""Shop widget for buying items."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Label, Static

from src.core.models.user import User
from src.core.repositories.game_data_repository import GameDataRepository
from src.core.repositories.inventory_repository import InventoryRepository, ItemType
from src.core.repositories.user_repository import UserRepository


class ShopWidget(Static):
    """Shop section for buying items."""

    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.game_data_repo = GameDataRepository()
        self.inventory_repo = InventoryRepository()
        self.user_repo = UserRepository()
        self.current_tab = "tools"

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("🛒 General Shop", classes="section-title")
            yield Static(f"Your balance: {self.user.balance} 🪙")

            with Horizontal(classes="shop-tabs"):
                yield Button("🔧 Tools", id="tab-tools", variant="primary")
                yield Button("🎣 Rods", id="tab-rods")
                yield Button("🪱 Bait", id="tab-baits")
                yield Button("🌱 Seeds", id="tab-seeds")
                yield Button("🌾 Feed", id="tab-feeds")

            with Vertical(classes="shop-content"):
                table = DataTable(id="shop-table")
                table.cursor_type = "row"
                yield table

            yield Static("", id="shop-result")

    def on_mount(self):
        """Load initial shop data."""
        self._load_tab("tools")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle tab buttons."""
        btn_id = event.button.id
        if btn_id and btn_id.startswith("tab-"):
            tab = btn_id.replace("tab-", "")
            self.current_tab = tab
            self._update_tab_buttons()
            self._load_tab(tab)

    def _update_tab_buttons(self):
        """Update tab button styling."""
        tabs = ["tools", "rods", "baits", "seeds", "feeds"]
        for tab in tabs:
            btn = self.query_one(f"#tab-{tab}", Button)
            btn.variant = "primary" if tab == self.current_tab else "default"

    def _load_tab(self, tab: str):
        """Load items for selected tab."""
        table = self.query_one("#shop-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Item", "Description", "Price", "Buy")

        type_map = {
            "tools": "tool",
            "rods": "rod",
            "baits": "bait",
            "seeds": "seed",
            "feeds": "feed",
        }

        item_type = type_map.get(tab, "tool")
        items = self.game_data_repo.get_items_by_type(item_type)

        for item in items:
            desc = item.description or item.attributes.get("description", "No description")
            table.add_row(
                item.name,
                desc[:30] + "..." if len(desc) > 30 else desc,
                f"{item.price} 🪙",
                "Buy",
                key=f"buy-{item.id}",
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle buy selection."""
        row_key = str(event.row_key)
        result = self.query_one("#shop-result", Static)

        if row_key.startswith("buy-"):
            item_id = int(row_key.replace("buy-", ""))
            self._buy_item(item_id, result)

    def _buy_item(self, item_id: int, result: Static):
        """Buy an item."""
        item = self.game_data_repo.get_item(item_id)
        if not item:
            result.update("❌ Item not found")
            return

        if self.user.balance < item.price:
            result.update(f"❌ Not enough coins (need {item.price} 🪙)")
            return

        # Map item type to ItemType enum
        type_mapping = {
            "tool": ItemType.TOOL,
            "rod": ItemType.ROD,
            "bait": ItemType.BAIT,
            "seed": ItemType.SEED,
            "feed": ItemType.FEED,
        }
        item_type = type_mapping.get(item.type, ItemType.TOOL)

        # Add to inventory
        self.inventory_repo.add_item(self.user.id, item_type, item.id, 1)

        # Deduct coins
        self.user.deduct(item.price)
        self.user_repo.update(self.user)

        result.update(f"✅ Bought {item.name} for {item.price} 🪙")

        # Update balance display
        for widget in self.walk_children():
            if isinstance(widget, Static) and "Your balance" in widget.renderable:
                widget.update(f"Your balance: {self.user.balance} 🪙")
                break

        # Refresh parent stats
        try:
            parent = self.parent
            if parent and hasattr(parent, "refresh_user_stats"):
                parent.refresh_user_stats()
        except:
            pass
