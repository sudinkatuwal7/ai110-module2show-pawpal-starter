"""Class skeletons for the PawPal+ pet care planner."""

from dataclasses import dataclass, field
from datetime import date
from typing import ClassVar


@dataclass
class Task:
    """A pet care activity with a duration, priority, and recurrence."""

    name: str
    duration_minutes: int
    priority: str = "medium"
    recurrence: str = "once"
    last_completed_date: date | None = None

    def update_details(
        self,
        *,
        name: str | None = None,
        duration_minutes: int | None = None,
        priority: str | None = None,
        recurrence: str | None = None,
    ) -> None:
        """Update supplied task details; leave unspecified details unchanged."""
        raise NotImplementedError

    def is_due(self, on_date: date) -> bool:
        """Check whether this task needs to be done on the given date."""
        raise NotImplementedError

    def mark_complete(self, on_date: date) -> None:
        """Record the date when this task was completed."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet belonging to an owner, with its own list of care tasks."""

    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet's task list."""
        raise NotImplementedError


@dataclass
class Owner:
    """A pet owner with pets, a daily time budget, and a task preference."""

    name: str
    available_minutes: int = 0
    prefer_short_tasks: bool = False
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        raise NotImplementedError

    def update_settings(
        self,
        *,
        available_minutes: int | None = None,
        prefer_short_tasks: bool | None = None,
    ) -> None:
        """Update supplied settings; leave unspecified settings unchanged."""
        raise NotImplementedError

    def get_all_tasks(self) -> list[Task]:
        """Collect care tasks from all of this owner's pets."""
        raise NotImplementedError


class Scheduler:
    """Use an owner's time and task information to build a daily plan."""

    priority_order: ClassVar[dict[str, int]] = {
        "high": 0,
        "medium": 1,
        "low": 2,
    }

    def generate_plan(self, owner: Owner, on_date: date) -> dict[str, object]:
        """Return selected tasks, skipped tasks with reasons, and time totals."""
        raise NotImplementedError
