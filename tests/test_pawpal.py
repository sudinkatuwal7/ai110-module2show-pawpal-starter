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
    daily.mark_complete(today)
    once.mark_complete(today)
    owner = Owner("Jordan", 15, pets=[Pet("Mochi", "cat", tasks=[daily, once])])

    today_plan = Scheduler().generate_plan(owner, today)
    tomorrow_plan = Scheduler().generate_plan(owner, today + timedelta(days=1))

    assert today_plan["selected"] == []
    assert len(today_plan["skipped"]) == 2
    assert [entry["task"] for entry in tomorrow_plan["selected"]] == [daily]
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
    {"duration_minutes": True}, {"priority": "urgent"}, {"recurrence": "weekly"},
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
