"""Farm/farming data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional


class GrowthStage(Enum):
    """Crop growth stages."""

    EMPTY = 0
    SEED = 1
    GROWING = 2
    READY = 3
    WITHERED = 4


@dataclass
class FieldPlot:
    """Single field plot for farming."""

    id: int = 0
    user_id: str = ""
    plot_number: int = 0
    crop_id: Optional[int] = None
    planted_at: Optional[datetime] = None
    last_watered: Optional[datetime] = None
    growth_stage: GrowthStage = GrowthStage.EMPTY
    health: int = 100
    # Crop attributes at planting (for consistency)
    crop_growth_time: int = 0
    crop_delay_time: int = 0

    def plant(self, crop_id: int, growth_time: int, delay_time: int) -> None:
        """Plant a crop in this plot."""
        self.crop_id = crop_id
        self.planted_at = datetime.now()
        self.last_watered = datetime.now()
        self.growth_stage = GrowthStage.SEED
        self.health = 100
        self.crop_growth_time = growth_time
        self.crop_delay_time = delay_time

    def water(self) -> None:
        """Water the crop."""
        self.last_watered = datetime.now()
        self.health = min(100, self.health + 10)

    def update_growth(self) -> None:
        """Update growth stage based on time elapsed."""
        if self.growth_stage in (GrowthStage.EMPTY, GrowthStage.WITHERED):
            return

        if not self.planted_at:
            return

        now = datetime.now()
        elapsed = (now - self.planted_at).total_seconds()

        # Check for withering (not watered in 48 hours)
        if self.last_watered:
            time_since_water = (now - self.last_watered).total_seconds()
            if time_since_water > 48 * 3600:  # 48 hours
                self.health = max(0, self.health - int(time_since_water / 3600))

        if self.health <= 0:
            self.growth_stage = GrowthStage.WITHERED
            return

        # Update stage based on growth time
        if elapsed >= self.crop_growth_time + self.crop_delay_time:
            self.growth_stage = GrowthStage.READY
        elif elapsed >= self.crop_delay_time:
            self.growth_stage = GrowthStage.GROWING

    def harvest(self) -> dict[str, Any] | None:
        """Harvest the crop if ready.

        Returns:
            Harvest data if successful, None if not ready
        """
        if self.growth_stage != GrowthStage.READY:
            return None

        result = {
            "crop_id": self.crop_id,
            "health": self.health,
        }

        # Reset plot
        self.crop_id = None
        self.planted_at = None
        self.last_watered = None
        self.growth_stage = GrowthStage.EMPTY
        self.health = 100

        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plot_number": self.plot_number,
            "crop_id": self.crop_id,
            "planted_at": self.planted_at.isoformat() if self.planted_at else None,
            "last_watered": self.last_watered.isoformat() if self.last_watered else None,
            "growth_stage": self.growth_stage.value,
            "health": self.health,
            "crop_growth_time": self.crop_growth_time,
            "crop_delay_time": self.crop_delay_time,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FieldPlot:
        plot = cls(
            id=data.get("id", 0),
            user_id=data.get("user_id", ""),
            plot_number=data.get("plot_number", 0),
            crop_id=data.get("crop_id"),
            health=data.get("health", 100),
            growth_stage=GrowthStage(data.get("growth_stage", 0)),
            crop_growth_time=data.get("crop_growth_time", 0),
            crop_delay_time=data.get("crop_delay_time", 0),
        )
        if data.get("planted_at"):
            plot.planted_at = datetime.fromisoformat(data["planted_at"])
        if data.get("last_watered"):
            plot.last_watered = datetime.fromisoformat(data["last_watered"])
        return plot


@dataclass
class BarnSlot:
    """Barn slot for animals/livestock."""

    id: int = 0
    user_id: str = ""
    slot_number: int = 0
    animal_id: Optional[int] = None
    acquired_at: Optional[datetime] = None
    last_fed: Optional[datetime] = None
    happiness: int = 50
    product_ready_at: Optional[datetime] = None

    def add_animal(self, animal_id: int) -> None:
        """Add animal to this slot."""
        self.animal_id = animal_id
        self.acquired_at = datetime.now()
        self.last_fed = datetime.now()
        self.happiness = 50
        self._schedule_product()

    def feed(self) -> None:
        """Feed the animal."""
        self.last_fed = datetime.now()
        self.happiness = min(100, self.happiness + 15)

    def _schedule_product(self, hours: int = 24) -> None:
        """Schedule next product collection."""
        self.product_ready_at = datetime.now() + timedelta(hours=hours)

    def collect_product(self) -> dict[str, Any] | None:
        """Collect product if ready.

        Returns:
            Product data if ready, None otherwise
        """
        if not self.product_ready_at or datetime.now() < self.product_ready_at:
            return None

        result = {
            "animal_id": self.animal_id,
            "happiness": self.happiness,
        }

        # Reschedule
        self._schedule_product()

        return result

    def update_happiness(self) -> None:
        """Update happiness based on feeding status."""
        if not self.last_fed:
            return

        hours_since_fed = (datetime.now() - self.last_fed).total_seconds() / 3600
        if hours_since_fed > 24:
            self.happiness = max(0, self.happiness - int(hours_since_fed - 24))

    def remove_animal(self) -> dict[str, Any] | None:
        """Remove animal from slot.

        Returns:
            Animal data if there was one, None if empty
        """
        if not self.animal_id:
            return None

        result = {
            "animal_id": self.animal_id,
            "happiness": self.happiness,
        }

        self.animal_id = None
        self.acquired_at = None
        self.last_fed = None
        self.happiness = 50
        self.product_ready_at = None

        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "slot_number": self.slot_number,
            "animal_id": self.animal_id,
            "acquired_at": self.acquired_at.isoformat() if self.acquired_at else None,
            "last_fed": self.last_fed.isoformat() if self.last_fed else None,
            "happiness": self.happiness,
            "product_ready_at": self.product_ready_at.isoformat() if self.product_ready_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BarnSlot:
        slot = cls(
            id=data.get("id", 0),
            user_id=data.get("user_id", ""),
            slot_number=data.get("slot_number", 0),
            animal_id=data.get("animal_id"),
            happiness=data.get("happiness", 50),
        )
        if data.get("acquired_at"):
            slot.acquired_at = datetime.fromisoformat(data["acquired_at"])
        if data.get("last_fed"):
            slot.last_fed = datetime.fromisoformat(data["last_fed"])
        if data.get("product_ready_at"):
            slot.product_ready_at = datetime.fromisoformat(data["product_ready_at"])
        return slot
