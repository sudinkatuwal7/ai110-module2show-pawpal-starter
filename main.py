"""Run a small terminal demo of the PawPal+ logic layer."""

from pawpal_system import Owner, Pet, Scheduler, Task


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


if __name__ == "__main__":
    main()
