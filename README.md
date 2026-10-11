# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps an owner plan care tasks across multiple pets.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

The project follows a design-first workflow: UML, Python scheduling logic, and a connected Streamlit UI.

## Implementation Summary

### Architecture

The [final system architecture UML](diagrams/uml_final.mmd) shows the four classes, their attributes and methods, and their relationships. Owner manages pets, Pet contains tasks, and Scheduler uses their information without inheritance. The Streamlit UI calls these backend methods and keeps the objects in session state.

The logic layer in `pawpal_system.py` uses four classes. `Task` stores an activity's name, duration, priority, recurrence, last completion date, optional scheduled time, and optional due date. Its `completed` property reports whether completion has ever been recorded; `is_due(on_date)` checks whether the task is pending and its due date is absent or on/before that day. `Pet` manages its tasks, and `Owner` manages pets. `Owner.get_all_tasks()` returns `(pet, task)` pairs so tasks stay associated with their pets.

`Scheduler.generate_plan(owner, on_date=None)` retrieves all tasks through that Owner method, orders them by priority, and fits whole tasks into one shared time budget. The short-task preference breaks ties within a priority; otherwise, collection order is preserved. Tasks that do not fit or are not due are skipped with reasons, and the scheduler continues checking other tasks. One-time, daily, and weekly tasks are supported, and generating a plan does not mark tasks complete.

The plan is a dictionary with `selected`, `skipped`, `total_minutes`, and `remaining_minutes`. Each selected or skipped entry contains `pet`, `task`, and `reason`. The plan allocates a total time budget; it does not assign or enforce appointment times. Chronological sorting and conflict detection are separate methods, so the plan dictionary stays unchanged.

The backend has no Streamlit dependency. The app in `app.py` connects task entry, sorting, filtering, completion, conflict warnings, and schedule generation to the backend. Data stays in the current Streamlit session; adding pets or tasks, completing tasks, or changing scheduling settings clears the saved plan so it can be regenerated. Run the app with `streamlit run app.py`.

Task inputs and owner scheduling settings are validated when created or updated through their methods. `main.py` demonstrates the system, and `tests/test_pawpal.py` checks completion, task addition, multi-pet scheduling through the Owner accessor, priorities, time limits, recurrence, and validation.

## Features

- Add multiple pets and create tasks for a selected pet with a duration, priority, optional scheduled `HH:MM` time, and optional due date.
- Generate today's plan across all pets using one time budget, priority ordering, and an optional preference for shorter tasks when priorities match. See selected tasks, skipped-task reasons, and time totals.
- Browse tasks automatically sorted by scheduled time, with untimed tasks last; filter by full pet name (ignoring case) and completion status.
- Choose `once`, `daily`, or `weekly` recurrence. Use **Complete today** buttons to record completion and automatically create the next daily or weekly occurrence.
- See readable warnings for pending tasks with identical start times on the same effective date, including tasks belonging to different pets. Warnings check all tasks regardless of the display filters.
- Use validated inputs and a backend covered by 97 pytest cases. The UI supports task creation and completion; editing and removal remain backend methods.

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

Run the terminal demo with `python main.py`. Its first demo creates an owner with two pets and four tasks. **Sample excerpt from an actual run:** the opening output is shown below; separate sorting/filtering, recurring-task, and conflict demos follow.

```text
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

## Testing PawPal+

Run the full pytest suite from the project directory:

```bash
python -m pytest

# Optional coverage report (requires pytest-cov):
pytest --cov
```

The tests cover chronological sorting (including minutes, tied times, and untimed tasks), filtering by pet and completion status, daily/weekly recurrence chains, and exact same-time conflict detection across pets and dates. They also check duplicate prevention by object identity, strict owner-setting validation, and rejected updates leaving settings unchanged. Edge cases include empty inputs, zero time budgets, invalid task details and times, completed tasks, repeated completion, leap days, and year changes.

Full terminal output from the successful `python -m pytest` run for Phase 5:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\crisu\Downloads\ai110-module2show-pawpal-starter-main\ai110-module2show-pawpal-starter
plugins: anyio-4.12.1
collected 97 items

tests\test_pawpal.py ................................................... [ 52%]
..............................................                           [100%]

============================= 97 passed in 0.13s ==============================
```

This run completed without Windows cache-permission errors; no fallback was needed. If cache permissions interfere with a later run, use `python -m pytest -p no:cacheprovider` to run the same tests without pytest's cache plugin.

**Confidence Level: 4/5 stars (★★★★☆).** All 97 tests pass, which gives me confidence in the backend behaviors covered by the suite. Exact-time conflict detection does not check overlapping task durations, and the Streamlit UI is not comprehensively covered by automated tests, so these results do not verify every possible scheduling or user-interface scenario.

## Smarter Scheduling

These four features are implemented in `pawpal_system.py`, available in the Streamlit UI, and demonstrated in `main.py`:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Chronological sorting | `Scheduler.sort_tasks_by_time(task_pairs)` | Returns a new list ordered by scheduled `HH:MM` time (24-hour format). Untimed tasks go last, and ties keep their original order. This sorts by time of day, not due date. |
| Filtering | `Scheduler.filter_tasks(owner, pet_name=None, completed=None)` | Returns matching `(pet, task)` pairs. Pet names match exactly, ignoring case. Use `completed=True` for completed tasks, `False` for pending tasks, or `None` for either. Both filters can be combined. |
| Recurring tasks | `Pet.complete_task(task, on_date=None)` | Marks an owned task complete and automatically adds and returns its next pending occurrence: one day after completion for `daily`, seven days for `weekly`. The original stays completed; the new task keeps its care details and scheduled time. One-time tasks and repeated completion calls create no new occurrence. The completion date defaults to today. |
| Conflict detection | `Scheduler.detect_conflicts(task_pairs, on_date=None)` | Returns one readable warning per group of pending tasks with an identical starting time on the same effective date, including tasks across pets. Uses each task's due date, otherwise the planning date (default: today). Ignores completed and untimed tasks, returns `[]` when none conflict, and never changes tasks. |

Use `Owner.get_all_tasks()` to collect pairs for sorting or conflict detection. Use `Pet.complete_task()` for recurring tasks; `Task.mark_complete()` only records completion and does not create a next occurrence.

Conflict detection checks **identical start times on the same effective date only**, not overlapping durations. The effective date is the task's due date when set, otherwise the planning date (today in the UI). For example, 09:00–09:30 and 09:15–09:45 do not trigger a warning. It reports conflicts without deleting or rescheduling tasks and runs separately from `generate_plan()`.

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

## Demo Walkthrough

1. After setup, run `streamlit run app.py` from the project directory and open the local URL shown in the terminal.
2. Enter the owner name **Jordan**. Add **Biscuit** as a dog and **Mochi** as a cat using **Add pet**.
3. Select **Task's pet**, enter each task below, and click **Add task** once for each row. Leave due dates blank or select today so these tasks are eligible for today's plan.

| Pet | Task title | Minutes | Priority | Scheduled time | Recurrence |
|-----|------------|---------|----------|----------------|------------|
| Biscuit | Morning walk | 25 | high | 07:30 | daily |
| Mochi | Feeding | 5 | high | 07:30 | daily |
| Mochi | Playtime | 10 | medium | 12:00 | once |
| Biscuit | Grooming | 20 | low | Leave blank | weekly |

4. In **Browse tasks**, confirm that 07:30 tasks appear before 12:00 and untimed Grooming appears last. Enter `mochi` in **Filter by pet name** and choose **Pending** to see Mochi's pending tasks. Clear the pet filter to show all pets again. Sorting is automatic; filters only change the task list.
5. Under **Build Schedule**, set **Available time (minutes)** to **40**, enable **Prefer shorter tasks when priorities match**, and click **Generate schedule**. Feeding, Morning walk, and Playtime fill the budget; Grooming is skipped with a reason. The generated plan follows priorities and the time budget, while the browse list follows scheduled times.
6. Review **Same-time conflicts**. A warning identifies Biscuit's Morning walk and Mochi's Feeding at 07:30 on the same effective date. It appears automatically, even before generating a plan or while filtering to one pet. Warnings do not reschedule tasks or remove them from the plan.
7. Expand **Complete a task** and click the **Complete today** button for Mochi's Feeding. A success message confirms completion and a new daily Feeding task due tomorrow. Choose **Completed** to see the original or **Pending** to see the new occurrence. Completing weekly Grooming would create its next occurrence seven days after completion. The saved plan is cleared; click **Generate schedule** again to update it. Future-dated occurrences are skipped until due.
