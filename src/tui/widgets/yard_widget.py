"""Yard widget for farming and livestock management."""

from __future__ import annotations

from datetime import datetime, timedelta

from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Label, Static

from src.core.models.farm import BarnSlot, FieldPlot, GrowthStage
from src.core.models.user import User
from src.core.repositories.farm_repository import FarmRepository
from src.core.repositories.game_data_repository import GameDataRepository
from src.core.repositories.inventory_repository import InventoryRepository, ItemType
from src.core.repositories.user_repository import UserRepository
from src.core.services.farm_service import FarmService


class YardWidget(Static):
    """Yard section for farming and livestock."""

    selected_tab = reactive("fields")

    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.farm_repo = FarmRepository()
        self.game_data_repo = GameDataRepository()
        self.inventory_repo = InventoryRepository()
        self.user_repo = UserRepository()
        self.farm_service = FarmService()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("🌾 Your Yard", classes="section-title")

            with Horizontal():
                yield Button("🌱 Fields", id="btn-fields", variant="primary")
                yield Button("🐄 Barn", id="btn-barn")
                yield Button("📦 Inventory", id="btn-inventory")

            with Vertical(id="yard-content"):
                self._render_fields()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle tab buttons."""
        btn_id = event.button.id
        content = self.query_one("#yard-content", Vertical)
        content.remove_children()

        if btn_id == "btn-fields":
            self._render_fields()
        elif btn_id == "btn-barn":
            self._render_barn()
        elif btn_id == "btn-inventory":
            self._render_inventory()

    def _render_fields(self):
        """Render farming fields."""
        content = self.query_one("#yard-content", Vertical)

        plots = self.farm_repo.get_field_plots(self.user.id)
        if not plots:
            # Initialize plots
            for i in range(6):
                plot = FieldPlot(user_id=self.user.id, plot_number=i + 1)
                self.farm_repo.create_field_plot(plot)
            plots = self.farm_repo.get_field_plots(self.user.id)

        with content:
            yield Label("🌱 Farming Fields")
            yield Static(f"You have {len(plots)} plots")

            with Grid(classes="plot-grid"):
                for plot in plots:
                    yield self._create_plot_widget(plot)

    def _create_plot_widget(self, plot: FieldPlot):
        """Create widget for a field plot."""
        classes = "plot"
        content = []

        if plot.growth_stage == GrowthStage.EMPTY:
            classes += " empty"
            content = ["🟫 Empty Plot", f"Plot #{plot.plot_number}", Button("Plant", id=f"plant-{plot.id}")]
        elif plot.growth_stage == GrowthStage.SEED:
            classes += " seed"
            crop = self.game_data_repo.get_crop(plot.crop_id) if plot.crop_id else None
            content = [f"🌱 {crop.name if crop else 'Unknown'}", "Just planted", "Water soon!"]
        elif plot.growth_stage == GrowthStage.GROWING:
            classes += " growing"
            crop = self.game_data_repo.get_crop(plot.crop_id) if plot.crop_id else None
            content = [f"🌿 {crop.name if crop else 'Unknown'}", "Growing...", Button("Water", id=f"water-{plot.id}")]
        elif plot.growth_stage == GrowthStage.READY:
            classes += " ready"
            crop = self.game_data_repo.get_crop(plot.crop_id) if plot.crop_id else None
            content = [f"🌾 {crop.name if crop else 'Unknown'}", "Ready to harvest!", Button("Harvest", id=f"harvest-{plot.id}")]
        else:  # WITHERED
            classes += " withered"
            content = ["🥀 Withered", "Crop died", Button("Clear", id=f"clear-{plot.id}")]

        container = Vertical(classes=classes)
        for item in content:
            container.mount(item)
        return container

    def _render_barn(self):
        """Render barn with animals."""
        content = self.query_one("#yard-content", Vertical)

        slots = self.farm_repo.get_barn_slots(self.user.id)
        if not slots:
            for i in range(4):
                slot = BarnSlot(user_id=self.user.id, slot_number=i + 1)
                self.farm_repo.create_barn_slot(slot)
            slots = self.farm_repo.get_barn_slots(self.user.id)

        with content:
            yield Label("🐄 Barn")
            yield Static(f"You have {len(slots)} animal slots")

            with Grid(classes="barn-grid"):
                for slot in slots:
                    yield self._create_barn_widget(slot)

    def _create_barn_widget(self, slot: BarnSlot):
        """Create widget for a barn slot."""
        container = Vertical(classes="barn-slot")

        if not slot.animal_id:
            container.mount(Label("🏠 Empty"))
            container.mount(Static(f"Slot #{slot.slot_number}"))
            container.mount(Button("Add Animal", id=f"add-animal-{slot.id}"))
        else:
            animal = self.game_data_repo.get_animal(slot.animal_id)
            name = animal.name if animal else "Unknown"

            # Get product status
            product_ready = slot.product_ready_at and slot.product_ready_at <= datetime.now()
            happiness_bar = "█" * (slot.happiness // 10) + "░" * (10 - slot.happiness // 10)

            container.mount(Label(f"🐮 {name}"))
            container.mount(Static(f"Slot #{slot.slot_number}"))
            container.mount(Static(f"Happiness: [{happiness_bar}]"))

            if product_ready:
                container.mount(Button("Collect", id=f"collect-{slot.id}", variant="success"))
            else:
                container.mount(Button("Feed", id=f"feed-{slot.id}"))

        return container

    def _render_inventory(self):
        """Render seeds/feeds inventory."""
        content = self.query_one("#yard-content", Vertical)

        inventory = self.inventory_repo.get_user_inventory(self.user.id)
        seeds = [i for i in inventory if i.item_type == ItemType.SEED]
        feeds = [i for i in inventory if i.item_type == ItemType.FEED]

        with content:
            yield Label("📦 Farming Inventory")

            yield Label("Seeds:")
            if seeds:
                for seed in seeds:
                    seed_data = self.game_data_repo.get_seed(seed.item_id)
                    name = seed_data.name if seed_data else f"Seed #{seed.item_id}"
                    yield Static(f"  🌱 {name} x{seed.quantity}")
            else:
                yield Static("  No seeds. Buy some from the shop!")

            yield Label("Feeds:")
            if feeds:
                for feed in feeds:
                    feed_data = self.game_data_repo.get_item(feed.item_id)
                    name = feed_data.name if feed_data else f"Feed #{feed.item_id}"
                    yield Static(f"  🌾 {name} x{feed.quantity}")
            else:
                yield Static("  No animal feed. Buy some from the shop!")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle action buttons."""
        btn_id = event.button.id
        if not btn_id:
            return

        if btn_id.startswith("plant-"):
            plot_id = int(btn_id.replace("plant-", ""))
            self._show_plant_dialog(plot_id)
        elif btn_id.startswith("water-"):
            plot_id = int(btn_id.replace("water-", ""))
            self._water_plot(plot_id)
        elif btn_id.startswith("harvest-"):
            plot_id = int(btn_id.replace("harvest-", ""))
            self._harvest_plot(plot_id)
        elif btn_id.startswith("clear-"):
            plot_id = int(btn_id.replace("clear-", ""))
            self._clear_plot(plot_id)
        elif btn_id.startswith("feed-"):
            slot_id = int(btn_id.replace("feed-", ""))
            self._feed_animal(slot_id)
        elif btn_id.startswith("collect-"):
            slot_id = int(btn_id.replace("collect-", ""))
            self._collect_product(slot_id)
        elif btn_id.startswith("add-animal-"):
            slot_id = int(btn_id.replace("add-animal-", ""))
            self._show_add_animal_dialog(slot_id)

    def _water_plot(self, plot_id: int):
        """Water a plot."""
        plot = self.farm_repo.get_field_plot(plot_id)
        if plot:
            plot.last_watered = datetime.now()
            self.farm_repo.update_field_plot(plot)
            self._refresh()

    def _harvest_plot(self, plot_id: int):
        """Harvest a plot."""
        plot = self.farm_repo.get_field_plot(plot_id)
        if plot and plot.crop_id:
            crop = self.game_data_repo.get_crop(plot.crop_id)
            if crop:
                # Add crop to inventory
                self.inventory_repo.add_item(self.user.id, ItemType.CROP, crop.id, 1)
                # Give XP
                self.user.add_xp(crop.xp_reward)
                self.user_repo.update(self.user)

            # Reset plot
            plot.growth_stage = GrowthStage.EMPTY
            plot.crop_id = None
            self.farm_repo.update_field_plot(plot)
            self._refresh()

    def _clear_plot(self, plot_id: int):
        """Clear a withered plot."""
        plot = self.farm_repo.get_field_plot(plot_id)
        if plot:
            plot.growth_stage = GrowthStage.EMPTY
            plot.crop_id = None
            self.farm_repo.update_field_plot(plot)
            self._refresh()

    def _feed_animal(self, slot_id: int):
        """Feed an animal."""
        # Check for feed in inventory
        feeds = self.inventory_repo.get_items_by_type(self.user.id, ItemType.FEED)
        if not feeds:
            self.notify("No feed in inventory! Buy some from the shop.", severity="error")
            return

        # Use first available feed
        feed = feeds[0]
        if self.inventory_repo.remove_item(self.user.id, ItemType.FEED, feed.item_id, 1):
            slot = self.farm_repo.get_barn_slot(slot_id)
            if slot:
                slot.last_fed = datetime.now()
                slot.happiness = min(100, slot.happiness + 20)
                self.farm_repo.update_barn_slot(slot)
                self._refresh()

    def _collect_product(self, slot_id: int):
        """Collect animal product."""
        slot = self.farm_repo.get_barn_slot(slot_id)
        if slot and slot.animal_id:
            animal = self.game_data_repo.get_animal(slot.animal_id)
            products = self.game_data_repo.get_animal_products(slot.animal_id)
            if products:
                product = products[0]  # Get main product
                self.inventory_repo.add_item(self.user.id, ItemType.PRODUCT, product.id, 1)
                self.user.add_xp(product.xp_reward)
                self.user_repo.update(self.user)

            # Reset product timer
            slot.product_ready_at = None
            self.farm_repo.update_barn_slot(slot)
            self._refresh()

    def _show_plant_dialog(self, plot_id: int):
        """Show plant dialog - simplified for now."""
        seeds = self.inventory_repo.get_items_by_type(self.user.id, ItemType.SEED)
        if not seeds:
            self.notify("No seeds! Buy some from the shop.", severity="error")
            return

        # Use first seed
        seed = seeds[0]
        seed_data = self.game_data_repo.get_seed(seed.item_id)
        if seed_data:
            if self.inventory_repo.remove_item(self.user.id, ItemType.SEED, seed.item_id, 1):
                plot = self.farm_repo.get_field_plot(plot_id)
                if plot:
                    plot.crop_id = seed_data.crop_id
                    plot.growth_stage = GrowthStage.SEED
                    plot.planted_at = datetime.now()
                    self.farm_repo.update_field_plot(plot)
                    self._refresh()

    def _show_add_animal_dialog(self, slot_id: int):
        """Show add animal dialog."""
        self.app.push_screen(AnimalShopScreen(self.user, slot_id))

    def _refresh(self):
        """Refresh the view."""
        content = self.query_one("#yard-content", Vertical)
        content.remove_children()
        self._render_fields()

    def on_mount(self):
        """Auto-refresh farming state."""
        self.set_interval(30, self._update_farm_states)

    def _update_farm_states(self):
        """Update growth stages and animal products."""
        self.farm_service.update_all_farm_states(self.user.id)
