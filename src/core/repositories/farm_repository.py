"""Farm/farming repository for field plots and barn slots."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from src.core.exceptions import ValidationError
from src.core.models.farm import BarnSlot, FieldPlot, GrowthStage
from src.db.sqlite_manager import SQLiteManager


class FarmRepository:
    """Repository for farm operations."""

    def __init__(self, db: Optional[SQLiteManager] = None) -> None:
        """Initialize with database manager."""
        self.db = db or SQLiteManager()

    # Field Plot Operations

    def get_plots(self, user_id: str) -> list[FieldPlot]:
        """Get all field plots for a user."""
        rows = self.db.fetchall(
            "SELECT * FROM field_plots WHERE user_id = ? ORDER BY plot_number",
            (user_id,),
        )
        return [self._row_to_plot(row) for row in rows]

    def get_plot(self, user_id: str, plot_number: int) -> Optional[FieldPlot]:
        """Get specific field plot."""
        row = self.db.fetchone(
            "SELECT * FROM field_plots WHERE user_id = ? AND plot_number = ?",
            (user_id, plot_number),
        )
        if not row:
            return None
        return self._row_to_plot(row)

    def create_or_update_plot(self, plot: FieldPlot) -> None:
        """Save field plot to database."""
        self.db.execute(
            """INSERT INTO field_plots
            (user_id, plot_number, crop_id, planted_at, last_watered,
             growth_stage, health, crop_growth_time, crop_delay_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, plot_number) DO UPDATE SET
            crop_id = excluded.crop_id,
            planted_at = excluded.planted_at,
            last_watered = excluded.last_watered,
            growth_stage = excluded.growth_stage,
            health = excluded.health,
            crop_growth_time = excluded.crop_growth_time,
            crop_delay_time = excluded.crop_delay_time""",
            (
                plot.user_id,
                plot.plot_number,
                plot.crop_id,
                plot.planted_at.isoformat() if plot.planted_at else None,
                plot.last_watered.isoformat() if plot.last_watered else None,
                plot.growth_stage.value,
                plot.health,
                plot.crop_growth_time,
                plot.crop_delay_time,
            ),
        )

    def plant_crop(
        self,
        user_id: str,
        plot_number: int,
        crop_id: int,
        growth_time: int,
        delay_time: int,
    ) -> FieldPlot:
        """Plant a crop in a field plot."""
        plot = self.get_plot(user_id, plot_number)
        if not plot:
            plot = FieldPlot(user_id=user_id, plot_number=plot_number)

        if plot.growth_stage != GrowthStage.EMPTY:
            raise ValidationError("Plot is not empty")

        plot.plant(crop_id, growth_time, delay_time)
        self.create_or_update_plot(plot)
        return plot

    def water_plot(self, user_id: str, plot_number: int) -> Optional[FieldPlot]:
        """Water a field plot."""
        plot = self.get_plot(user_id, plot_number)
        if not plot:
            return None

        plot.water()
        self.create_or_update_plot(plot)
        return plot

    def harvest_plot(self, user_id: str, plot_number: int) -> Optional[dict]:
        """Harvest a ready crop from a plot.

        Returns:
            Harvest data if successful, None if not ready
        """
        plot = self.get_plot(user_id, plot_number)
        if not plot or plot.growth_stage != GrowthStage.READY:
            return None

        result = plot.harvest()
        self.create_or_update_plot(plot)
        return result

    def clear_plot(self, user_id: str, plot_number: int) -> bool:
        """Clear a plot (remove dead/withered crops)."""
        plot = self.get_plot(user_id, plot_number)
        if not plot:
            return False

        plot.crop_id = None
        plot.planted_at = None
        plot.last_watered = None
        plot.growth_stage = GrowthStage.EMPTY
        plot.health = 100

        self.create_or_update_plot(plot)
        return True

    def delete_plot(self, user_id: str, plot_number: int) -> bool:
        """Delete a plot entirely."""
        result = self.db.execute(
            "DELETE FROM field_plots WHERE user_id = ? AND plot_number = ?",
            (user_id, plot_number),
        )
        return result.rowcount > 0

    # Barn Slot Operations

    def get_slots(self, user_id: str) -> list[BarnSlot]:
        """Get all barn slots for a user."""
        rows = self.db.fetchall(
            "SELECT * FROM barn_slots WHERE user_id = ? ORDER BY slot_number",
            (user_id,),
        )
        return [self._row_to_slot(row) for row in rows]

    def get_slot(self, user_id: str, slot_number: int) -> Optional[BarnSlot]:
        """Get specific barn slot."""
        row = self.db.fetchone(
            "SELECT * FROM barn_slots WHERE user_id = ? AND slot_number = ?",
            (user_id, slot_number),
        )
        if not row:
            return None
        return self._row_to_slot(row)

    def create_or_update_slot(self, slot: BarnSlot) -> None:
        """Save barn slot to database."""
        self.db.execute(
            """INSERT INTO barn_slots
            (user_id, slot_number, animal_id, acquired_at, last_fed, happiness, product_ready_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, slot_number) DO UPDATE SET
            animal_id = excluded.animal_id,
            acquired_at = excluded.acquired_at,
            last_fed = excluded.last_fed,
            happiness = excluded.happiness,
            product_ready_at = excluded.product_ready_at""",
            (
                slot.user_id,
                slot.slot_number,
                slot.animal_id,
                slot.acquired_at.isoformat() if slot.acquired_at else None,
                slot.last_fed.isoformat() if slot.last_fed else None,
                slot.happiness,
                slot.product_ready_at.isoformat() if slot.product_ready_at else None,
            ),
        )

    def add_animal(self, user_id: str, slot_number: int, animal_id: int) -> BarnSlot:
        """Add an animal to a barn slot."""
        slot = self.get_slot(user_id, slot_number)
        if not slot:
            slot = BarnSlot(user_id=user_id, slot_number=slot_number)

        if slot.animal_id is not None:
            raise ValidationError("Slot is already occupied")

        slot.add_animal(animal_id)
        self.create_or_update_slot(slot)
        return slot

    def feed_animal(self, user_id: str, slot_number: int) -> Optional[BarnSlot]:
        """Feed an animal in a barn slot."""
        slot = self.get_slot(user_id, slot_number)
        if not slot or slot.animal_id is None:
            return None

        slot.feed()
        self.create_or_update_slot(slot)
        return slot

    def collect_product(self, user_id: str, slot_number: int) -> Optional[dict]:
        """Collect product from a barn slot."""
        slot = self.get_slot(user_id, slot_number)
        if not slot or slot.animal_id is None:
            return None

        result = slot.collect_product()
        if result:
            self.create_or_update_slot(slot)
        return result

    def remove_animal(self, user_id: str, slot_number: int) -> Optional[dict]:
        """Remove an animal from a barn slot."""
        slot = self.get_slot(user_id, slot_number)
        if not slot:
            return None

        result = slot.remove_animal()
        if result:
            self.create_or_update_slot(slot)
        return result

    def delete_slot(self, user_id: str, slot_number: int) -> bool:
        """Delete a barn slot entirely."""
        result = self.db.execute(
            "DELETE FROM barn_slots WHERE user_id = ? AND slot_number = ?",
            (user_id, slot_number),
        )
        return result.rowcount > 0

    # Utility Methods

    def count_active_plots(self, user_id: str) -> int:
        """Count non-empty field plots."""
        row = self.db.fetchone(
            "SELECT COUNT(*) as count FROM field_plots WHERE user_id = ? AND growth_stage > 0",
            (user_id,),
        )
        return row["count"] if row else 0

    def count_animals(self, user_id: str) -> int:
        """Count animals in barn."""
        row = self.db.fetchone(
            "SELECT COUNT(*) as count FROM barn_slots WHERE user_id = ? AND animal_id IS NOT NULL",
            (user_id,),
        )
        return row["count"] if row else 0

    def get_ready_crops(self, user_id: str) -> list[FieldPlot]:
        """Get all plots with crops ready for harvest."""
        rows = self.db.fetchall(
            "SELECT * FROM field_plots WHERE user_id = ? AND growth_stage = ?",
            (user_id, GrowthStage.READY.value),
        )
        return [self._row_to_plot(row) for row in rows]

    def get_ready_products(self, user_id: str) -> list[BarnSlot]:
        """Get all slots with products ready to collect."""
        now = datetime.now().isoformat()
        rows = self.db.fetchall(
            "SELECT * FROM barn_slots WHERE user_id = ? AND animal_id IS NOT NULL AND product_ready_at <= ?",
            (user_id, now),
        )
        return [self._row_to_slot(row) for row in rows]

    def _row_to_plot(self, row: dict) -> FieldPlot:
        """Convert database row to FieldPlot."""
        plot = FieldPlot(
            id=row["id"],
            user_id=row["user_id"],
            plot_number=row["plot_number"],
            crop_id=row["crop_id"],
            growth_stage=GrowthStage(row["growth_stage"]),
            health=row["health"],
            crop_growth_time=row["crop_growth_time"],
            crop_delay_time=row["crop_delay_time"],
        )
        if row["planted_at"]:
            plot.planted_at = datetime.fromisoformat(row["planted_at"])
        if row["last_watered"]:
            plot.last_watered = datetime.fromisoformat(row["last_watered"])
        return plot

    def _row_to_slot(self, row: dict) -> BarnSlot:
        """Convert database row to BarnSlot."""
        slot = BarnSlot(
            id=row["id"],
            user_id=row["user_id"],
            slot_number=row["slot_number"],
            animal_id=row["animal_id"],
            happiness=row["happiness"],
        )
        if row["acquired_at"]:
            slot.acquired_at = datetime.fromisoformat(row["acquired_at"])
        if row["last_fed"]:
            slot.last_fed = datetime.fromisoformat(row["last_fed"])
        if row["product_ready_at"]:
            slot.product_ready_at = datetime.fromisoformat(row["product_ready_at"])
        return slot
