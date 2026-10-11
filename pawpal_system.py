"""Pet care tasks and daily planning, independent of the user interface."""

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

    def __post_init__(self) -> None:
        """Validate the initial task details."""
        self.update_details()

    @property
    def completed(self) -> bool:
        """Report whether completion has been recorded at least once."""
        return self.last_completed_date is not None

    def update_details(
        self,
        *,
        name: str | None = None,
        duration_minutes: int | None = None,
        priority: str | None = None,
        recurrence: str | None = None,
    ) -> None:
        """Update supplied task details; leave unspecified details unchanged."""
        new_name = self.name if name is None else name
        new_duration = self.duration_minutes if duration_minutes is None else duration_minutes
        new_priority = self.priority if priority is None else priority
        new_recurrence = self.recurrence if recurrence is None else recurrence

        if not isinstance(new_name, str) or not new_name.strip():
            raise ValueError("Task name must not be empty.")
        if type(new_duration) is not int or new_duration <= 0:
            raise ValueError("Task duration must be a positive whole number of minutes.")
        if new_priority not in ("high", "medium", "low"):
            raise ValueError("Priority must be high, medium, or low.")
        if new_recurrence not in ("once", "daily"):
            raise ValueError("Recurrence must be once or daily.")

        self.name = new_name.strip()
        self.duration_minutes = new_duration
        self.priority = new_priority
        self.recurrence = new_recurrence

    def is_due(self, on_date: date | None = None) -> bool:
        """Check whether this task needs to be done on the given date."""
        on_date = date.today() if on_date is None else on_date
        if not self.completed:
            return True
        if self.recurrence == "once":
            return False
        return self.last_completed_date < on_date

    def mark_complete(self, on_date: date | None = None) -> None:
        """Record the date when this task was completed."""
        self.last_completed_date = date.today() if on_date is None else on_date


@dataclass
class Pet:
    """A pet belonging to an owner, with its own list of care tasks."""

    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        if any(existing is task for existing in self.tasks):
            raise ValueError("This task is already in the pet's task list.")
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet's task list."""
        for index, existing in enumerate(self.tasks):
            if existing is task:
                self.tasks.pop(index)
                return
        raise ValueError("This task is not in the pet's task list.")


@dataclass
class Owner:
    """A pet owner with pets, a daily time budget, and a task preference."""

    name: str
    available_minutes: int = 0
    prefer_short_tasks: bool = False
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate the owner's initial scheduling settings."""
        self.update_settings()

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        if any(existing is pet for existing in self.pets):
            raise ValueError("This pet is already in the owner's pet list.")
        self.pets.append(pet)

    def update_settings(
        self,
        *,
        available_minutes: int | None = None,
        prefer_short_tasks: bool | None = None,
    ) -> None:
        """Update supplied settings; leave unspecified settings unchanged."""
        new_minutes = self.available_minutes if available_minutes is None else available_minutes
        new_preference = self.prefer_short_tasks if prefer_short_tasks is None else prefer_short_tasks
        if type(new_minutes) is not int or new_minutes < 0:
            raise ValueError("Available time must be a nonnegative whole number of minutes.")
        if not isinstance(new_preference, bool):
            raise ValueError("The short-task preference must be True or False.")
        self.available_minutes = new_minutes
        self.prefer_short_tasks = new_preference

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Collect (pet, task) pairs from all pets, preserving their order."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Use an owner's time and task information to build a daily plan."""

    priority_order: ClassVar[dict[str, int]] = {
        "high": 0,
        "medium": 1,
        "low": 2,
    }

    def generate_plan(self, owner: Owner, on_date: date | None = None) -> dict[str, object]:
        """Return selected tasks, skipped tasks with reasons, and time totals."""
        on_date = date.today() if on_date is None else on_date
        task_pairs = owner.get_all_tasks()
        task_pairs.sort(
            key=lambda pair: (
                self.priority_order[pair[1].priority],
                pair[1].duration_minutes if owner.prefer_short_tasks else 0,
            )
        )

        selected = []
        skipped = []
        remaining = owner.available_minutes
        for pet, task in task_pairs:
            if not task.is_due(on_date):
                skipped.append({"pet": pet, "task": task, "reason": "Not due on this date."})
            elif task.duration_minutes > remaining:
                skipped.append({
                    "pet": pet,
                    "task": task,
                    "reason": f"Needs {task.duration_minutes} min; only {remaining} min remain.",
                })
            else:
                selected.append({
                    "pet": pet,
                    "task": task,
                    "reason": f"{task.priority.capitalize()} priority; fits the remaining time.",
                })
                remaining -= task.duration_minutes

        return {
            "selected": selected,
            "skipped": skipped,
            "total_minutes": owner.available_minutes - remaining,
            "remaining_minutes": remaining,
        }
