"""Run a small terminal demo of the PawPal+ logic layer."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(title: str, task_pairs: list[tuple[Pet, Task]]) -> None:
    """Print pet-task pairs with their scheduled time and completion status."""
    print(f"\n{title}")
    for pet, task in task_pairs:
        status = "completed" if task.completed else "pending"
        print(f"- {task.scheduled_time or 'Untimed'} | {pet.name}: {task.name} [{status}]")


def demo_sorting_and_filtering() -> None:
    """Show chronological sorting and filters using a separate set of tasks."""
    owner = Owner("Jordan")
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task("Evening walk", 20, scheduled_time="18:00"))
    dog.add_task(Task("Grooming", 15))
    feeding = Task("Feeding", 5, scheduled_time="07:30")
    feeding.mark_complete()
    cat.add_task(feeding)
    cat.add_task(Task("Playtime", 10, scheduled_time="12:00"))

    scheduler = Scheduler()
    task_pairs = owner.get_all_tasks()
    print_tasks("Sorting and Filtering Demo - Original order", task_pairs)
    print_tasks("Sorted by scheduled time", scheduler.sort_tasks_by_time(task_pairs))
    print_tasks("Pet filter: mochi", scheduler.filter_tasks(owner, pet_name="mochi"))
    print_tasks("Completed tasks", scheduler.filter_tasks(owner, completed=True))
    print_tasks(
        "Pending tasks for Mochi",
        scheduler.filter_tasks(owner, pet_name="MOCHI", completed=False),
    )


def demo_recurring_tasks() -> None:
    """Show daily and weekly next occurrences and repeated-completion protection."""
    pet = Pet("Mochi", "cat")
    completed_on = date(2026, 10, 11)
    daily = Task("Feeding", 5, "high", "daily", scheduled_time="07:30")
    weekly = Task("Grooming", 15, "medium", "weekly", scheduled_time="18:00")
    pet.add_task(daily)
    pet.add_task(weekly)

    print(f"\nRecurring Tasks Demo - Completed on {completed_on}")
    for task in (daily, weekly):
        next_task = pet.complete_task(task, completed_on)
        print(f"- {pet.name}: {task.name} ({task.recurrence}) - original completed")
        print(f"  Next: {next_task.due_date} at {next_task.scheduled_time} [pending]")

    pet.complete_task(daily, completed_on)
    print(f"Completing Feeding again adds nothing: {len(pet.tasks)} tasks total.")


def demo_task_conflicts() -> None:
    """Print a warning for two pets with tasks at the same start time."""
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    dog.add_task(Task("Morning walk", 20, scheduled_time="07:30"))
    cat.add_task(Task("Feeding", 5, scheduled_time="07:30"))
    owner = Owner("Jordan", pets=[dog, cat])

    print("\nTask Conflicts Demo")
    for warning in Scheduler().detect_conflicts(owner.get_all_tasks(), date(2026, 10, 11)):
        print(f"- {warning}")


def main() -> None:
    """Build and print a daily care plan for two pets."""
    owner = Owner("Jordan", available_minutes=40, prefer_short_tasks=True)
    dog = Pet("Biscuit", "dog", "Golden Retriever")
    cat = Pet("Mochi", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task("Morning walk", 25, priority="high", recurrence="daily"))
    dog.add_task(Task("Grooming", 20, priority="low"))
    cat.add_task(Task("Feeding", 5, priority="high", recurrence="daily"))
    cat.add_task(Task("Playtime", 10, priority="medium", recurrence="daily"))

    plan = Scheduler().generate_plan(owner)
    print("Today's Schedule")
    print(f"Owner: {owner.name} | Available time: {owner.available_minutes} min")
    print()
    for number, entry in enumerate(plan["selected"], start=1):
        pet, task = entry["pet"], entry["task"]
        print(f"{number}. {pet.name}: {task.name} ({task.duration_minutes} min) [{task.priority}]")
        print(f"   {entry['reason']}")
    print(f"\nPlanned: {plan['total_minutes']} min | Remaining: {plan['remaining_minutes']} min")
    if plan["skipped"]:
        print("\nSkipped:")
        for entry in plan["skipped"]:
            print(f"- {entry['pet'].name}: {entry['task'].name} - {entry['reason']}")

    demo_sorting_and_filtering()
    demo_recurring_tasks()
    demo_task_conflicts()


if __name__ == "__main__":
    main()
