"""Check task management and the most important scheduling behaviors."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_completion():
    task = Task("Grooming", 15)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True
    assert task.last_completed_date == date.today()
    assert task.is_due() is False


def test_task_addition():
    pet = Pet("Biscuit", "dog")
    task = Task("Walk", 20)
    count_before = len(pet.tasks)

    pet.add_task(task)

    assert len(pet.tasks) == count_before + 1
    assert pet.tasks[-1] is task


def test_task_addition_rejects_same_object_but_allows_identical_details():
    pet = Pet("Biscuit", "dog")
    first = Task("Walk", 20)
    second = Task("Walk", 20)
    assert first == second
    assert first is not second
    pet.add_task(first)

    with pytest.raises(ValueError, match="already in the pet's task list"):
        pet.add_task(first)

    assert len(pet.tasks) == 1
    assert pet.tasks[0] is first

    pet.add_task(second)

    assert len(pet.tasks) == 2
    assert pet.tasks[0] is first
    assert pet.tasks[1] is second


def test_pet_addition_rejects_same_object_but_allows_identical_details():
    owner = Owner("Jordan")
    first = Pet("Mochi", "cat")
    second = Pet("Mochi", "cat")
    assert first == second
    assert first is not second
    owner.add_pet(first)

    with pytest.raises(ValueError, match="already in the owner's pet list"):
        owner.add_pet(first)

    assert len(owner.pets) == 1
    assert owner.pets[0] is first

    owner.add_pet(second)

    assert len(owner.pets) == 2
    assert owner.pets[0] is first
    assert owner.pets[1] is second


def test_owner_collects_tasks_from_multiple_pets():
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    walk, feeding = Task("Walk", 20), Task("Feeding", 5)
    dog.add_task(walk)
    cat.add_task(feeding)
    owner = Owner("Jordan")
    owner.add_pet(dog)
    owner.add_pet(cat)

    assert owner.get_all_tasks() == [(dog, walk), (cat, feeding)]


def test_scheduler_uses_owner_accessor_for_multiple_pets(monkeypatch):
    owner = Owner("Jordan", available_minutes=25)
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    walk = Task("Walk", 20, "medium")
    feeding = Task("Feeding", 5, "high")
    calls = []

    def collect_tasks():
        calls.append(True)
        return [(dog, walk), (cat, feeding)]

    monkeypatch.setattr(owner, "get_all_tasks", collect_tasks)
    plan = Scheduler().generate_plan(owner)

    assert calls == [True]
    assert [entry["task"] for entry in plan["selected"]] == [feeding, walk]
    assert [entry["pet"] for entry in plan["selected"]] == [cat, dog]
    assert plan["total_minutes"] == 25
    assert plan["remaining_minutes"] == 0
    assert walk.completed is False
    assert feeding.completed is False


def test_scheduler_skips_long_task_and_continues():
    long_task = Task("Long walk", 30, "high")
    short_task = Task("Feeding", 5, "medium")
    owner = Owner("Jordan", 10, pets=[Pet("Biscuit", "dog", tasks=[long_task, short_task])])

    plan = Scheduler().generate_plan(owner)

    assert [entry["task"] for entry in plan["selected"]] == [short_task]
    assert plan["skipped"][0]["task"] is long_task
    assert "only 10 min remain" in plan["skipped"][0]["reason"]
    assert plan["total_minutes"] == 5
    assert plan["remaining_minutes"] == 5


@pytest.mark.parametrize("prefer_short, expected", [(False, ["Long", "Short"]), (True, ["Short", "Long"])])
def test_short_task_preference_breaks_priority_ties(prefer_short, expected):
    tasks = [Task("Long", 20, "high"), Task("Short", 5, "high"), Task("Low", 1, "low")]
    owner = Owner("Jordan", 26, prefer_short, [Pet("Biscuit", "dog", tasks=tasks)])

    plan = Scheduler().generate_plan(owner)

    assert [entry["task"].name for entry in plan["selected"]] == expected + ["Low"]


def test_recurrence_and_completed_task_filtering():
    today = date(2026, 10, 11)
    daily = Task("Feeding", 5, recurrence="daily")
    once = Task("Grooming", 10)
    assert daily.is_due(today)
    pet = Pet("Mochi", "cat", tasks=[daily, once])
    next_daily = pet.complete_task(daily, today)
    pet.complete_task(once, today)
    owner = Owner("Jordan", 15, pets=[pet])

    today_plan = Scheduler().generate_plan(owner, today)
    tomorrow_plan = Scheduler().generate_plan(owner, today + timedelta(days=1))

    assert today_plan["selected"] == []
    assert len(today_plan["skipped"]) == 3
    assert [entry["task"] for entry in tomorrow_plan["selected"]] == [next_daily]
    assert next_daily is not daily
    assert not daily.is_due(today + timedelta(days=1))
    assert not once.is_due(today + timedelta(days=1))


def test_empty_owner_and_zero_time_budget():
    owner = Owner("Jordan")
    assert Scheduler().generate_plan(owner) == {
        "selected": [], "skipped": [], "total_minutes": 0, "remaining_minutes": 0,
    }
    owner.add_pet(Pet("Mochi", "cat", tasks=[Task("Feeding", 5)]))

    plan = Scheduler().generate_plan(owner)

    assert plan["selected"] == []
    assert len(plan["skipped"]) == 1
    assert plan["remaining_minutes"] == 0


@pytest.mark.parametrize("changes", [
    {"name": " "}, {"duration_minutes": 0}, {"duration_minutes": -1},
    {"duration_minutes": True}, {"priority": "urgent"}, {"recurrence": "monthly"},
])
def test_task_validation_on_creation_and_update(changes):
    details = {"name": "Walk", "duration_minutes": 10}
    with pytest.raises(ValueError):
        Task(**(details | changes))
    task = Task(**details)
    with pytest.raises(ValueError):
        task.update_details(**changes)
    assert task == Task(**details)


def test_valid_updates_preserve_unspecified_fields():
    task = Task("Walk", 10)
    task.update_details(duration_minutes=20, priority="high", recurrence="daily")
    assert (task.name, task.duration_minutes, task.priority, task.recurrence) == ("Walk", 20, "high", "daily")
    owner = Owner("Jordan", 30, True)
    owner.update_settings(available_minutes=45)
    assert (owner.available_minutes, owner.prefer_short_tasks) == (45, True)
    owner.update_settings(prefer_short_tasks=False)
    assert owner.prefer_short_tasks is False


def test_owner_rejects_invalid_time_on_creation_and_update():
    with pytest.raises(ValueError):
        Owner("Jordan", -1)
    owner = Owner("Jordan", 30)
    with pytest.raises(ValueError):
        owner.update_settings(available_minutes=-1)
    assert owner.available_minutes == 30


@pytest.mark.parametrize("minutes, preference, error", [
    (True, False, "Available time"),
    (False, False, "Available time"),
    (2.5, False, "Available time"),
    (45, 0, "short-task preference"),
    (45, 1, "short-task preference"),
    (45, "yes", "short-task preference"),
])
def test_owner_rejects_invalid_setting_types_without_partial_updates(minutes, preference, error):
    with pytest.raises(ValueError, match=error):
        Owner("Jordan", available_minutes=minutes, prefer_short_tasks=preference)

    owner = Owner("Jordan", available_minutes=30, prefer_short_tasks=True)
    # Even the valid setting must stay unchanged if the other setting is invalid.
    with pytest.raises(ValueError, match=error):
        owner.update_settings(available_minutes=minutes, prefer_short_tasks=preference)

    assert owner.available_minutes == 30
    assert type(owner.available_minutes) is int
    assert owner.prefer_short_tasks is True


def test_removal_targets_the_selected_instance():
    first, second = Task("Feeding", 5), Task("Feeding", 5)
    pet = Pet("Mochi", "cat", tasks=[first, second])

    pet.remove_task(second)

    assert len(pet.tasks) == 1
    assert pet.tasks[0] is first
    with pytest.raises(ValueError):
        pet.remove_task(second)


def test_mutable_defaults_are_independent():
    first, second = Owner("First"), Owner("Second")
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    first.add_pet(dog)
    dog.add_task(Task("Walk", 20))
    assert second.pets == []
    assert cat.tasks == []


@pytest.mark.parametrize("scheduled_time", [None, "00:00", "09:05", "12:30", "23:59"])
def test_valid_scheduled_times_on_creation_and_update(scheduled_time):
    task = Task("Walk", 10, scheduled_time=scheduled_time)
    assert task.scheduled_time == scheduled_time

    task = Task("Walk", 10, scheduled_time="18:00")
    task.update_details(scheduled_time=scheduled_time)
    assert task.scheduled_time == scheduled_time


@pytest.mark.parametrize("scheduled_time", [
    "", "9:05", "09:5", "24:00", "12:60", "-1:00", "09:00:00",
    " 09:00", "09:00 ", "09:00\n", "9 AM", "０９:００", 900,
])
def test_invalid_scheduled_times_on_creation_and_update(scheduled_time):
    with pytest.raises(ValueError, match="Scheduled time"):
        Task("Walk", 10, scheduled_time=scheduled_time)

    task = Task("Walk", 10, scheduled_time="09:00")
    with pytest.raises(ValueError, match="Scheduled time"):
        task.update_details(name="Changed", scheduled_time=scheduled_time)
    assert task.name == "Walk"
    assert task.scheduled_time == "09:00"


def test_omitted_time_update_preserves_time_and_none_clears_it():
    task = Task("Walk", 10, scheduled_time="09:00")
    task.update_details(priority="high")
    assert task.scheduled_time == "09:00"
    task.update_details(scheduled_time=None)
    assert task.scheduled_time is None


def test_existing_positional_task_constructor_still_works():
    completed_on = date(2026, 10, 11)
    task = Task("Walk", 10, "high", "daily", completed_on)
    assert task.last_completed_date == completed_on
    assert task.scheduled_time is None


def test_time_sort_is_chronological_and_does_not_mutate_input():
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    pairs = [
        (dog, Task("Evening", 10, scheduled_time="18:00")),
        (cat, Task("Morning", 5, scheduled_time="09:00")),
        (dog, Task("Midnight", 5, scheduled_time="00:00")),
        (cat, Task("Late", 5, scheduled_time="23:59")),
        (dog, Task("Later morning", 5, scheduled_time="09:45")),
        (cat, Task("Earlier morning", 5, scheduled_time="09:05")),
    ]
    original = list(pairs)

    result = Scheduler().sort_tasks_by_time(pairs)

    assert [task.name for _, task in result] == [
        "Midnight", "Morning", "Earlier morning", "Later morning", "Evening", "Late",
    ]
    assert pairs == original
    assert result is not pairs
    assert result[0] is pairs[2]


def test_time_sort_preserves_ties_and_puts_untimed_tasks_last():
    pet = Pet("Mochi", "cat")
    pairs = [
        (pet, Task("Untimed first", 5)),
        (pet, Task("Timed first", 5, scheduled_time="09:00")),
        (pet, Task("Untimed second", 5)),
        (pet, Task("Timed second", 5, scheduled_time="09:00")),
    ]

    result = Scheduler().sort_tasks_by_time(pairs)

    assert [task.name for _, task in result] == [
        "Timed first", "Timed second", "Untimed first", "Untimed second",
    ]


@pytest.mark.parametrize("pet_name, completed, expected_names", [
    (None, None, ["Walk", "Feeding", "Playtime"]),
    ("mochi", None, ["Feeding", "Playtime"]),
    ("MOCHI", None, ["Feeding", "Playtime"]),
    ("Moch", None, []),
    ("Unknown", None, []),
    (None, True, ["Feeding"]),
    (None, False, ["Walk", "Playtime"]),
    ("mochi", True, ["Feeding"]),
    ("MOCHI", False, ["Playtime"]),
    ("Biscuit", True, []),
])
def test_pet_and_completion_filters(pet_name, completed, expected_names):
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    dog.add_task(Task("Walk", 20))
    feeding = Task("Feeding", 5)
    feeding.mark_complete(date(2026, 10, 11))
    cat.add_task(feeding)
    cat.add_task(Task("Playtime", 10))
    owner = Owner("Jordan", pets=[dog, cat])
    original = owner.get_all_tasks()

    result = Scheduler().filter_tasks(owner, pet_name=pet_name, completed=completed)

    assert [task.name for _, task in result] == expected_names
    assert owner.get_all_tasks() == original
    assert all(any(pet is source_pet and task is source_task for source_pet, source_task in original)
               for pet, task in result)


def test_filter_tasks_retrieves_pairs_through_owner_method(monkeypatch):
    owner = Owner("Jordan")
    pet = Pet("Mochi", "cat")
    task = Task("Feeding", 5)
    calls = []

    def collect_tasks():
        calls.append(True)
        return [(pet, task)]

    monkeypatch.setattr(owner, "get_all_tasks", collect_tasks)

    assert Scheduler().filter_tasks(owner, "mochi", False) == [(pet, task)]
    assert calls == [True]


def test_sorting_and_filtering_empty_inputs():
    scheduler = Scheduler()
    assert scheduler.sort_tasks_by_time([]) == []
    assert scheduler.filter_tasks(Owner("Jordan")) == []


@pytest.mark.parametrize("recurrence, days", [("daily", 1), ("weekly", 7)])
@pytest.mark.parametrize("completion_date", [date(2026, 12, 31), date(2028, 2, 28)])
def test_recurring_completion_creates_one_next_occurrence(recurrence, days, completion_date):
    original_due = completion_date - timedelta(days=3)
    task = Task("Feeding", 5, "high", recurrence, scheduled_time="07:30", due_date=original_due)
    pet = Pet("Mochi", "cat", tasks=[task])

    next_task = pet.complete_task(task, completion_date)

    assert len(pet.tasks) == 2
    assert pet.tasks[0] is task
    assert pet.tasks[1] is next_task
    assert next_task is not task
    assert task.completed is True
    assert task.last_completed_date == completion_date
    assert task.due_date == original_due
    assert next_task.due_date == completion_date + timedelta(days=days)
    assert (next_task.name, next_task.duration_minutes, next_task.priority,
            next_task.recurrence, next_task.scheduled_time) == (
        "Feeding", 5, "high", recurrence, "07:30",
    )
    assert next_task.completed is False
    assert next_task.last_completed_date is None
    assert not next_task.is_due(completion_date)
    assert next_task.is_due(next_task.due_date)
    assert not task.is_due(next_task.due_date)


@pytest.mark.parametrize("recurrence, second_date, third_date", [
    ("daily", date(2026, 10, 12), date(2026, 10, 13)),
    ("weekly", date(2026, 10, 18), date(2026, 10, 25)),
])
def test_recurring_completion_continues_chain_without_duplicates(recurrence, second_date, third_date):
    first_date = date(2026, 10, 11)
    original = Task("Feeding", 5, recurrence=recurrence, scheduled_time="07:30", due_date=first_date)
    pet = Pet("Mochi", "cat", tasks=[original])

    second = pet.complete_task(original, first_date)

    assert second is not None
    assert second.due_date == second_date
    assert len(pet.tasks) == 2

    third = pet.complete_task(second, second_date)

    assert third is not None
    assert third.due_date == third_date
    assert third.recurrence == recurrence
    assert third.scheduled_time == "07:30"
    assert third.completed is False
    assert original.last_completed_date == first_date
    assert second.last_completed_date == second_date
    assert original is not second
    assert third is not original
    assert third is not second

    # Completing either earlier occurrence again must not add a fourth task.
    assert pet.complete_task(original, third_date) is None
    assert pet.complete_task(second, third_date) is None
    assert len(pet.tasks) == 3
    assert pet.tasks[0] is original
    assert pet.tasks[1] is second
    assert pet.tasks[2] is third
    pending = [task for task in pet.tasks if not task.completed]
    assert len(pending) == 1
    assert pending[0] is third


@pytest.mark.parametrize("recurrence", ["once", "daily", "weekly"])
def test_repeated_completion_does_not_add_tasks_or_change_original_date(recurrence):
    completed_on = date(2026, 10, 11)
    task = Task("Care", 10, recurrence=recurrence)
    pet = Pet("Mochi", "cat", tasks=[task])
    pet.complete_task(task, completed_on)
    count = len(pet.tasks)

    assert pet.complete_task(task, completed_on) is None
    assert pet.complete_task(task, completed_on + timedelta(days=1)) is None
    assert len(pet.tasks) == count
    assert task.last_completed_date == completed_on


def test_one_time_completion_creates_no_next_occurrence():
    task = Task("Vet visit", 30)
    pet = Pet("Mochi", "cat", tasks=[task])

    assert pet.complete_task(task) is None
    assert task.completed is True
    assert task.last_completed_date == date.today()
    assert len(pet.tasks) == 1


@pytest.mark.parametrize("recurrence, days", [("daily", 1), ("weekly", 7)])
def test_recurring_completion_defaults_to_today(recurrence, days):
    task = Task("Care", 10, recurrence=recurrence)
    pet = Pet("Mochi", "cat", tasks=[task])

    next_task = pet.complete_task(task)

    assert task.last_completed_date == date.today()
    assert next_task.due_date == date.today() + timedelta(days=days)
    assert next_task.scheduled_time is None


def test_completion_rejects_equal_but_unowned_task_by_identity():
    owned = Task("Feeding", 5, recurrence="daily")
    unowned = Task("Feeding", 5, recurrence="daily")
    pet = Pet("Mochi", "cat", tasks=[owned])
    assert owned == unowned

    with pytest.raises(ValueError, match="not in the pet's task list"):
        pet.complete_task(unowned)

    assert len(pet.tasks) == 1
    assert not owned.completed
    assert not unowned.completed


@pytest.mark.parametrize("recurrence", ["once", "daily", "weekly"])
def test_mark_complete_only_records_completion(recurrence):
    task = Task("Care", 10, recurrence=recurrence)
    pet = Pet("Mochi", "cat", tasks=[task])
    completed_on = date(2026, 10, 11)

    assert task.mark_complete(completed_on) is None

    assert task.last_completed_date == completed_on
    assert len(pet.tasks) == 1
    assert not task.is_due(completed_on + timedelta(days=10))


@pytest.mark.parametrize("due_date, expected", [
    (None, True),
    (date(2026, 10, 10), True),
    (date(2026, 10, 11), True),
    (date(2026, 10, 12), False),
])
def test_pending_tasks_are_due_when_undated_due_today_or_overdue(due_date, expected):
    task = Task("Care", 10, due_date=due_date)
    assert task.is_due(date(2026, 10, 11)) is expected


def test_scheduler_includes_overdue_tasks_and_skips_future_tasks():
    overdue = Task("Overdue", 10, due_date=date(2026, 10, 10))
    future = Task("Future", 10, due_date=date(2026, 10, 12))
    owner = Owner("Jordan", 20, pets=[Pet("Mochi", "cat", tasks=[overdue, future])])

    plan = Scheduler().generate_plan(owner, date(2026, 10, 11))

    assert [entry["task"] for entry in plan["selected"]] == [overdue]
    assert [entry["task"] for entry in plan["skipped"]] == [future]


def test_weekly_and_due_date_updates_preserve_unspecified_details():
    task = Task("Care", 10, scheduled_time="09:00")
    task.update_details(recurrence="weekly", due_date=date(2026, 10, 11))
    task.update_details(priority="high")
    assert task.recurrence == "weekly"
    assert task.due_date == date(2026, 10, 11)
    assert task.scheduled_time == "09:00"
    task.update_details(due_date=None)
    assert task.due_date is None


def test_due_date_does_not_shift_existing_positional_fields():
    completed_on = date(2026, 10, 11)
    task = Task("Care", 10, "high", "daily", completed_on, "09:00")
    assert task.last_completed_date == completed_on
    assert task.scheduled_time == "09:00"
    assert task.due_date is None


def test_invalid_due_date_does_not_partially_update_task():
    with pytest.raises(ValueError, match="Due date"):
        Task("Care", 10, due_date="2026-10-11")
    task = Task("Care", 10)
    with pytest.raises(ValueError, match="Due date"):
        task.update_details(name="Changed", due_date="2026-10-11")
    assert task.name == "Care"
    assert task.due_date is None


def test_conflicts_for_same_pet():
    pet = Pet("Biscuit", "dog")
    pairs = [
        (pet, Task("Walk", 20, scheduled_time="09:00")),
        (pet, Task("Grooming", 15, scheduled_time="09:00")),
    ]

    warnings = Scheduler().detect_conflicts(pairs, date(2026, 10, 11))

    assert len(warnings) == 1
    assert all(text in warnings[0] for text in (
        "Conflict", "2026-10-11", "09:00", "Biscuit: Walk", "Biscuit: Grooming",
    ))


def test_conflicts_across_pets():
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    pairs = [
        (dog, Task("Walk", 20, scheduled_time="09:00")),
        (cat, Task("Feeding", 5, scheduled_time="09:00")),
    ]

    warnings = Scheduler().detect_conflicts(pairs, date(2026, 10, 11))

    assert len(warnings) == 1
    assert "Biscuit: Walk" in warnings[0]
    assert "Mochi: Feeding" in warnings[0]


def test_different_start_times_do_not_conflict_even_when_durations_overlap():
    pet = Pet("Biscuit", "dog")
    pairs = [
        (pet, Task("Walk", 30, scheduled_time="09:00")),
        (pet, Task("Feeding", 5, scheduled_time="09:10")),
    ]

    assert Scheduler().detect_conflicts(pairs) == []


@pytest.mark.parametrize("first_date, second_date, expected_count", [
    (date(2026, 10, 10), date(2026, 10, 12), 0),
    (date(2026, 10, 12), date(2026, 10, 12), 1),
    (None, date(2026, 10, 11), 1),
    (date(2026, 10, 12), None, 0),
])
def test_conflicts_use_explicit_dates_before_planning_date(first_date, second_date, expected_count):
    pet = Pet("Mochi", "cat")
    pairs = [
        (pet, Task("Feeding", 5, scheduled_time="09:00", due_date=first_date)),
        (pet, Task("Playtime", 10, scheduled_time="09:00", due_date=second_date)),
    ]

    warnings = Scheduler().detect_conflicts(pairs, date(2026, 10, 11))

    assert len(warnings) == expected_count
    if warnings:
        assert str(first_date or second_date) in warnings[0]


def test_conflicts_default_planning_date_to_today():
    pet = Pet("Mochi", "cat")
    pairs = [
        (pet, Task("Feeding", 5, scheduled_time="09:00")),
        (pet, Task("Playtime", 10, scheduled_time="09:00", due_date=date.today())),
    ]

    warnings = Scheduler().detect_conflicts(pairs)

    assert len(warnings) == 1
    assert str(date.today()) in warnings[0]


def test_conflicts_ignore_completed_tasks():
    pet = Pet("Mochi", "cat")
    completed = Task("Feeding", 5, scheduled_time="09:00")
    completed.mark_complete(date(2026, 10, 11))
    pending = Task("Playtime", 10, scheduled_time="09:00")

    assert Scheduler().detect_conflicts([(pet, completed), (pet, pending)]) == []


def test_conflicts_ignore_untimed_tasks():
    pet = Pet("Mochi", "cat")
    pairs = [
        (pet, Task("Feeding", 5)),
        (pet, Task("Grooming", 15)),
        (pet, Task("Playtime", 10, scheduled_time="09:00")),
    ]

    assert Scheduler().detect_conflicts(pairs) == []


def test_no_conflicts_for_empty_or_single_task_input():
    scheduler = Scheduler()
    assert scheduler.detect_conflicts([]) == []
    assert scheduler.detect_conflicts([
        (Pet("Mochi", "cat"), Task("Feeding", 5, scheduled_time="09:00")),
    ]) == []


def test_conflicts_group_all_matching_tasks_without_changing_tasks_or_plan():
    tasks = [
        Task("Walk", 20, scheduled_time="09:00"),
        Task("Feeding", 5, scheduled_time="09:00"),
        Task("Grooming", 15, scheduled_time="09:00"),
        Task("Playtime", 10, scheduled_time="18:00"),
        Task("Training", 10, scheduled_time="18:00"),
    ]
    pet = Pet("Biscuit", "dog", tasks=list(tasks))
    owner = Owner("Jordan", 60, pets=[pet])
    pairs = owner.get_all_tasks()
    original_pairs = list(pairs)
    original_details = [vars(task).copy() for task in tasks]
    scheduler = Scheduler()
    planning_date = date(2026, 10, 11)
    original_plan = scheduler.generate_plan(owner, planning_date)

    warnings = scheduler.detect_conflicts(pairs, planning_date)

    assert len(warnings) == 2
    assert all(task.name in warnings[0] for task in tasks[:3])
    assert all(task.name in warnings[1] for task in tasks[3:])
    assert pairs == original_pairs
    assert len(pet.tasks) == len(tasks)
    assert all(current is original for current, original in zip(pet.tasks, tasks))
    assert [vars(task) for task in tasks] == original_details
    assert scheduler.generate_plan(owner, planning_date) == original_plan
    assert set(original_plan) == {"selected", "skipped", "total_minutes", "remaining_minutes"}
