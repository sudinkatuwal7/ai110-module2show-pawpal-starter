# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## Implementation Summary

The logic layer in `pawpal_system.py` uses four classes. `Task` stores an activity's name, duration, priority, recurrence, last completion date, optional scheduled time, and optional due date. Its `completed` property reports whether completion has ever been recorded; `is_due(on_date)` checks whether the task is pending and its due date is absent or on/before that day. `Pet` manages its tasks, and `Owner` manages pets. `Owner.get_all_tasks()` returns `(pet, task)` pairs so tasks stay associated with their pets.

`Scheduler.generate_plan(owner, on_date=None)` retrieves all tasks through that Owner method, orders them by priority, and fits whole tasks into one shared time budget. The short-task preference breaks ties within a priority; otherwise, collection order is preserved. Tasks that do not fit or are not due are skipped with reasons, and the scheduler continues checking other tasks. One-time, daily, and weekly tasks are supported, and generating a plan does not mark tasks complete.

The plan is a dictionary with `selected`, `skipped`, `total_minutes`, and `remaining_minutes`. Each selected or skipped entry contains `pet`, `task`, and `reason`. The plan allocates a total time budget; it does not assign or enforce appointment times. Chronological sorting and conflict detection are separate methods, so the plan dictionary stays unchanged.

The backend has no Streamlit dependency. The Streamlit app in `app.py` is connected to it: users can add pets and tasks, set available minutes and the short-task preference, and generate a plan with selected tasks, skipped-task explanations, and time totals. Data stays in the current Streamlit session. Phase 4 features are available through Python methods and terminal demos; the app does not yet have controls for scheduled times, task filtering, completion/recurrence, or conflict warnings. Run the app with `streamlit run app.py`.

Task inputs and owner scheduling settings are validated when created or updated through their methods. `main.py` demonstrates the system, and `tests/test_pawpal.py` checks completion, task addition, multi-pet scheduling through the Owner accessor, priorities, time limits, recurrence, and validation.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Run the terminal demo with `python main.py`. Its first demo creates an owner with two pets and four tasks. This is the opening output; separate sorting/filtering, recurring-task, and conflict demos follow:

```
Today's Schedule
Owner: Jordan | Available time: 40 min

1. Mochi: Feeding (5 min) [high]
   High priority; fits the remaining time.
2. Biscuit: Morning walk (25 min) [high]
   High priority; fits the remaining time.
3. Mochi: Playtime (10 min) [medium]
   Medium priority; fits the remaining time.

Planned: 40 min | Remaining: 0 min

Skipped:
- Biscuit: Grooming - Needs 20 min; only 0 min remain.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest -p no:cacheprovider

# Run with coverage:
pytest --cov
```

Sample test output:

```
87 passed in 0.11s
```

## Smarter Scheduling

These four features are implemented in `pawpal_system.py` and demonstrated in `main.py`:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Chronological sorting | `Scheduler.sort_tasks_by_time(task_pairs)` | Returns a new list ordered by scheduled `HH:MM` time (24-hour format). Untimed tasks go last, and ties keep their original order. This sorts by time of day, not due date. |
| Filtering | `Scheduler.filter_tasks(owner, pet_name=None, completed=None)` | Returns matching `(pet, task)` pairs. Pet names match exactly, ignoring case. Use `completed=True` for completed tasks, `False` for pending tasks, or `None` for either. Both filters can be combined. |
| Recurring tasks | `Pet.complete_task(task, on_date=None)` | Marks an owned task complete and automatically adds and returns its next pending occurrence: one day after completion for `daily`, seven days for `weekly`. The original stays completed; the new task keeps its care details and scheduled time. One-time tasks and repeated completion calls create no new occurrence. The completion date defaults to today. |
| Conflict detection | `Scheduler.detect_conflicts(task_pairs, on_date=None)` | Returns one readable warning per group of pending tasks with an identical starting time on the same effective date, including tasks across pets. Uses each task's due date, otherwise the planning date (default: today). Ignores completed and untimed tasks, returns `[]` when none conflict, and never changes tasks. |

Use `Owner.get_all_tasks()` to collect pairs for sorting or conflict detection. Use `Pet.complete_task()` for recurring tasks; `Task.mark_complete()` only records completion and does not create a next occurrence.

Conflict detection checks **identical start times only**, not overlapping durations. For example, 09:00–09:30 and 09:15–09:45 do not trigger a warning. It reports conflicts without deleting or rescheduling tasks and runs separately from `generate_plan()`.

### Python example

Run this from the project directory, where `pawpal_system.py` can be imported:

```python
from datetime import date
from pawpal_system import Owner, Pet, Scheduler, Task

day = date(2026, 10, 11)
dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
owner = Owner("Jordan", pets=[dog, cat])
scheduler = Scheduler()
grooming = Task("Grooming", 15, recurrence="weekly", scheduled_time="09:00")
feeding = Task("Feeding", 5, recurrence="daily", scheduled_time="09:00")
dog.add_task(grooming)
cat.add_task(Task("Playtime", 10, scheduled_time="18:00"))
cat.add_task(feeding)

pairs = scheduler.sort_tasks_by_time(owner.get_all_tasks())
print([task.name for pet, task in pairs])  # ['Grooming', 'Feeding', 'Playtime']
pending = scheduler.filter_tasks(owner, pet_name="MOCHI", completed=False)
print([task.name for pet, task in pending])  # ['Playtime', 'Feeding']
for warning in scheduler.detect_conflicts(pairs, on_date=day):
    print(warning)  # Warns about Biscuit's Grooming and Mochi's Feeding at 09:00.

next_feeding = cat.complete_task(feeding, on_date=day)
next_grooming = dog.complete_task(grooming, on_date=day)
print(next_feeding.due_date, next_grooming.due_date)  # 2026-10-12 2026-10-18
done = scheduler.filter_tasks(owner, completed=True)
print([task.name for pet, task in done])  # ['Grooming', 'Feeding']
print(scheduler.detect_conflicts(owner.get_all_tasks(), on_date=day))  # []
```

The last call returns no warnings because the original tasks are completed and their next occurrences have different due dates.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
