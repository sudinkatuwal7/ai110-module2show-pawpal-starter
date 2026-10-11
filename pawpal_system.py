"""Pet care tasks and daily planning, independent of the user interface."""

from dataclasses import dataclass, field
from datetime import date, timedelta
import re
from types import EllipsisType
from typing import ClassVar


@dataclass
class Task:
    """A pet care activity with a duration, priority, and recurrence."""

    name: str
    duration_minutes: int
    priority: str = "medium"
    recurrence: str = "once"
    last_completed_date: date | None = None
    scheduled_time: str | None = None
    due_date: date | None = None

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
        scheduled_time: str | None | EllipsisType = ...,
        due_date: date | None | EllipsisType = ...,
    ) -> None:
        """Update supplied task details; leave unspecified details unchanged."""
        new_name = self.name if name is None else name
        new_duration = self.duration_minutes if duration_minutes is None else duration_minutes
        new_priority = self.priority if priority is None else priority
        new_recurrence = self.recurrence if recurrence is None else recurrence
        # An omitted time keeps its value; explicitly passing None clears it.
        new_time = self.scheduled_time if scheduled_time is ... else scheduled_time
        new_due_date = self.due_date if due_date is ... else due_date

        if not isinstance(new_name, str) or not new_name.strip():
            raise ValueError("Task name must not be empty.")
        if type(new_duration) is not int or new_duration <= 0:
            raise ValueError("Task duration must be a positive whole number of minutes.")
        if new_priority not in ("high", "medium", "low"):
            raise ValueError("Priority must be high, medium, or low.")
        if new_recurrence not in ("once", "daily", "weekly"):
            raise ValueError("Recurrence must be once, daily, or weekly.")
        if new_time is not None and (
            not isinstance(new_time, str)
            or re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", new_time) is None
        ):
            raise ValueError("Scheduled time must be HH:MM from 00:00 to 23:59, or None.")
        if new_due_date is not None and type(new_due_date) is not date:
            raise ValueError("Due date must be a date or None.")

        self.name = new_name.strip()
        self.duration_minutes = new_duration
        self.priority = new_priority
        self.recurrence = new_recurrence
        self.scheduled_time = new_time
        self.due_date = new_due_date

    def is_due(self, on_date: date | None = None) -> bool:
        """Check whether this task needs to be done on the given date."""
        on_date = date.today() if on_date is None else on_date
        return not self.completed and (self.due_date is None or self.due_date <= on_date)

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

    def complete_task(self, task: Task, on_date: date | None = None) -> Task | None:
        """Complete an owned task once and return its added next occurrence, if any."""
        if not any(existing is task for existing in self.tasks):
            raise ValueError("This task is not in the pet's task list.")
        if task.completed:
            return None

        completion_date = date.today() if on_date is None else on_date
        next_task = None
        if task.recurrence in ("daily", "weekly"):
            interval = timedelta(days=1) if task.recurrence == "daily" else timedelta(days=7)
            next_task = Task(
                name=task.name,
                duration_minutes=task.duration_minutes,
                priority=task.priority,
                recurrence=task.recurrence,
                scheduled_time=task.scheduled_time,
                due_date=completion_date + interval,
            )

        task.mark_complete(completion_date)
        if next_task is not None:
            self.add_task(next_task)
        return next_task


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

    def sort_tasks_by_time(self, task_pairs: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Return a stable chronological copy, with untimed tasks last."""
        return sorted(
            task_pairs,
            key=lambda pair: (pair[1].scheduled_time is None, pair[1].scheduled_time or ""),
        )

    def filter_tasks(
        self,
        owner: Owner,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[tuple[Pet, Task]]:
        """Return all matching pet-task pairs in their original order."""
        return [
            (pet, task)
            for pet, task in owner.get_all_tasks()
            if (pet_name is None or pet.name.casefold() == pet_name.casefold())
            and (completed is None or task.completed is completed)
        ]

    def detect_conflicts(
        self,
        task_pairs: list[tuple[Pet, Task]],
        on_date: date | None = None,
    ) -> list[str]:
        """Warn about shared start times without changing tasks; default to today."""
        on_date = date.today() if on_date is None else on_date
        groups = {}
        for pet, task in task_pairs:
            if task.completed or not task.scheduled_time:
                continue

            effective_date = task.due_date if task.due_date is not None else on_date
            key = (effective_date, task.scheduled_time)
            if key not in groups:
                groups[key] = []
            groups[key].append(f"{pet.name}: {task.name}")

        warnings = []
        for (effective_date, scheduled_time), task_names in groups.items():
            if len(task_names) > 1:
                warnings.append(
                    f"Conflict on {effective_date} at {scheduled_time}: "
                    + "; ".join(task_names)
                    + " are scheduled at the same time."
                )
        return warnings

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
