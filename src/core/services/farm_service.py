"""Farm service for crop and livestock management."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from src.core.models.farm import BarnSlot, FieldPlot, GrowthStage
from src.core.repositories.farm_repository import FarmRepository
from src.core.repositories.game_data_repository import GameDataRepository


class FarmService:
    """Service for farming operations."""

    # Growth stages and their durations (as percentage of total growth time)
    STAGE_DURATIONS = {
        GrowthStage.SEED: 0.1,      # 10% of time as seed
        GrowthStage.GROWING: 0.7,    # 70% of time growing
        GrowthStage.READY: float('inf'),  # Ready until harvested
    }

    # Wither time after ready (hours)
    WITHER_TIME_HOURS = 24

    # Animal product interval (hours)
    ANIMAL_PRODUCT_INTERVAL = 4

    def __init__(self):
        self.farm_repo = FarmRepository()
        self.game_repo = GameDataRepository()

    def plant_crop(self, plot: FieldPlot, crop_id: int) -> bool:
        """Plant a crop in a plot."""
        plot.crop_id = crop_id
        plot.growth_stage = GrowthStage.SEED
        plot.planted_at = datetime.now()
        plot.last_watered = datetime.now()
        plot.health = 100

        # Get crop data for growth time
        crop = self.game_repo.get_crop(crop_id)
        if crop:
            plot.crop_growth_time = crop.growth_time

        self.farm_repo.update_field_plot(plot)
        return True

    def water_plot(self, plot: FieldPlot) -> None:
        """Water a plot to maintain health."""
        plot.last_watered = datetime.now()

        # Restore some health if not withered
        if plot.growth_stage != GrowthStage.WITHERED:
            plot.health = min(100, plot.health + 20)

        self.farm_repo.update_field_plot(plot)

    def update_crop_growth(self, plot: FieldPlot) -> None:
        """Update the growth stage of a crop based on time."""
        if plot.growth_stage in (GrowthStage.EMPTY, GrowthStage.WITHERED, GrowthStage.READY):
            return

        if not plot.planted_at or not plot.crop_growth_time:
            return

        now = datetime.now()
        elapsed = (now - plot.planted_at).total_seconds()
        growth_time = plot.crop_growth_time

        # Check water status - reduce health if not watered
        if plot.last_watered:
            hours_since_water = (now - plot.last_watered).total_seconds() / 3600
            if hours_since_water > 6:  # Needs water every 6 hours
                plot.health = max(0, plot.health - int(hours_since_water - 6) * 5)

        # Check if crop withered due to neglect
        if plot.health <= 0:
            plot.growth_stage = GrowthStage.WITHERED
            self.farm_repo.update_field_plot(plot)
            return

        # Update growth stage
        seed_time = growth_time * self.STAGE_DURATIONS[GrowthStage.SEED]
        growing_time = growth_time * self.STAGE_DURATIONS[GrowthStage.GROWING]

        if elapsed < seed_time:
            plot.growth_stage = GrowthStage.SEED
        elif elapsed < (seed_time + growing_time):
            plot.growth_stage = GrowthStage.GROWING
        else:
            plot.growth_stage = GrowthStage.READY

        self.farm_repo.update_field_plot(plot)

    def check_withering(self, plot: FieldPlot) -> None:
        """Check if a ready crop has withered."""
        if plot.growth_stage != GrowthStage.READY:
            return

        if not plot.planted_at:
            return

        now = datetime.now()
        crop = self.game_repo.get_crop(plot.crop_id) if plot.crop_id else None

        if crop:
            # Total time = growth time + delay time
            total_time = crop.growth_time + crop.delay_time
            ready_time = timedelta(seconds=total_time)
            wither_deadline = plot.planted_at + ready_time + timedelta(hours=self.WITHER_TIME_HOURS)

            if now > wither_deadline:
                plot.growth_stage = GrowthStage.WITHERED
                self.farm_repo.update_field_plot(plot)

    def feed_animal(self, slot: BarnSlot) -> None:
        """Feed an animal to increase happiness."""
        slot.last_fed = datetime.now()
        slot.happiness = min(100, slot.happiness + 25)
        self.farm_repo.update_barn_slot(slot)

    def update_animal_products(self, slot: BarnSlot) -> None:
        """Update animal product readiness."""
        if not slot.animal_id:
            return

        now = datetime.now()

        # Calculate happiness penalty
        happiness_factor = slot.happiness / 100
        interval_hours = self.ANIMAL_PRODUCT_INTERVAL / happiness_factor

        # Check if product is ready
        if slot.product_ready_at:
            if now >= slot.product_ready_at:
                # Product is ready, don't update
                return
        else:
            # Set initial product time
            slot.product_ready_at = now + timedelta(hours=interval_hours)
            self.farm_repo.update_barn_slot(slot)

    def collect_product(self, slot: BarnSlot) -> Optional[int]:
        """Collect an animal product.

        Returns:
            Product ID if collected, None if not ready
        """
        if not slot.product_ready_at or datetime.now() < slot.product_ready_at:
            return None

        # Get animal product
        if slot.animal_id:
            products = self.game_repo.get_animal_products(slot.animal_id)
            if products:
                product = products[0]  # Main product

                # Reset timer
                happiness_factor = slot.happiness / 100
                interval_hours = self.ANIMAL_PRODUCT_INTERVAL / happiness_factor
                slot.product_ready_at = datetime.now() + timedelta(hours=interval_hours)
                self.farm_repo.update_barn_slot(slot)

                return product.id

        return None

    def update_all_farm_states(self, user_id: str) -> None:
        """Update all farm states for a user."""
        # Update crops
        plots = self.farm_repo.get_field_plots(user_id)
        for plot in plots:
            self.update_crop_growth(plot)
            self.check_withering(plot)

        # Update animals
        slots = self.farm_repo.get_barn_slots(user_id)
        for slot in slots:
            self.update_animal_products(slot)

    def get_crop_progress(self, plot: FieldPlot) -> float:
        """Get crop growth progress as percentage."""
        if plot.growth_stage == GrowthStage.EMPTY:
            return 0.0
        if plot.growth_stage == GrowthStage.READY:
            return 100.0
        if not plot.planted_at or not plot.crop_growth_time:
            return 0.0

        elapsed = (datetime.now() - plot.planted_at).total_seconds()
        return min(100.0, (elapsed / plot.crop_growth_time) * 100)
