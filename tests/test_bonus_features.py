"""Persistence, interval-search and UI regression checks for the bonus features."""

from dataclasses import asdict
from datetime import date, timedelta
import json
from pathlib import Path
import subprocess
import sys

import pytest
from streamlit.testing.v1 import AppTest

import persistence
from pawpal_system import Owner, Pet, Scheduler, Task


DAY = date(2026, 10, 11)
ROOT = Path(__file__).resolve().parents[1]


def sample_owner():
    owner = Owner("Jordán", 90, True, [Pet("Mochi", "cat", ""), Pet("Mochi", "dog", "Mix")])
    daily = Task("Feeding", 5, "high", "daily", scheduled_time="07:30", due_date=DAY)
    owner.pets[0].add_task(daily)
    owner.pets[0].complete_task(daily, DAY)
    owner.pets[1].add_task(Task("Feeding", 25, "low", "weekly"))
    return owner


def test_save_load_round_trip_in_new_process(tmp_path):
    path = tmp_path / "nested" / "pets.json"
    original = sample_owner()
    persistence.save_owner(original, path)
    restored = persistence.load_owner(path)
    assert asdict(restored) == asdict(original)
    assert restored is not original
    assert restored.pets[0].tasks[0].completed
    assert restored.pets[0].complete_task(restored.pets[0].tasks[0], DAY) is None
    assert len(restored.pets[0].tasks) == 2
    result = subprocess.run(
        [sys.executable, "-c", "from persistence import load_owner; import sys; "
         "o=load_owner(sys.argv[1]); print(len(o.pets),len(o.get_all_tasks()),o.available_minutes)", str(path)],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    assert result.stdout.strip() == "2 3 90"


def test_empty_owner_round_trip(tmp_path):
    path = tmp_path / "pets.json"
    persistence.save_owner(Owner("Jordan"), path)
    assert persistence.load_owner(path) == Owner("Jordan")


@pytest.mark.parametrize("mutation", [
    lambda d: d.update(version=2),
    lambda d: d.update(version=True),
    lambda d: d.update(extra="unexpected"),
    lambda d: d["owner"].update(pets={}),
    lambda d: d["owner"].update(name=" "),
    lambda d: d["owner"].update(available_minutes=True),
    lambda d: d["owner"].update(prefer_short_tasks="yes"),
    lambda d: d["owner"]["pets"][0].update(tasks="bad"),
    lambda d: d["owner"]["pets"][0]["tasks"][0].update(duration_minutes=0),
    lambda d: d["owner"]["pets"][0]["tasks"][0].update(priority="urgent"),
    lambda d: d["owner"]["pets"][0]["tasks"][0].update(scheduled_time="25:00"),
    lambda d: d["owner"]["pets"][0]["tasks"][0].update(due_date="2026-02-30"),
    lambda d: d["owner"]["pets"][0]["tasks"][0].update(last_completed_date=123),
    lambda d: d["owner"]["pets"][0]["tasks"][0].pop("recurrence"),
])
def test_invalid_saved_document_rejected(tmp_path, mutation):
    path = tmp_path / "pets.json"
    persistence.save_owner(sample_owner(), path)
    document = json.loads(path.read_text(encoding="utf-8"))
    mutation(document)
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValueError):
        persistence.load_owner(path)


def test_missing_and_broken_json(tmp_path):
    path = tmp_path / "pets.json"
    with pytest.raises(FileNotFoundError):
        persistence.load_owner(path)
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(ValueError):
        persistence.load_owner(path)


def test_failed_save_keeps_previous_file_and_cleans_temporary(tmp_path, monkeypatch):
    path = tmp_path / "pets.json"
    persistence.save_owner(sample_owner(), path)
    previous = path.read_bytes()

    def fail_replace(*args):
        raise OSError("Simulated disk failure")

    monkeypatch.setattr(persistence.os, "replace", fail_replace)
    with pytest.raises(OSError):
        persistence.save_owner(Owner("New owner"), path)
    assert path.read_bytes() == previous
    assert list(tmp_path.iterdir()) == [path]


def test_invalid_live_data_cannot_overwrite_save(tmp_path):
    path = tmp_path / "pets.json"
    owner = sample_owner()
    persistence.save_owner(owner, path)
    previous = path.read_bytes()
    owner.pets[0].tasks[0].duration_minutes = -1
    with pytest.raises(ValueError):
        persistence.save_owner(owner, path)
    assert path.read_bytes() == previous


def test_slot_search_merges_overlaps_across_pets_without_mutation():
    owner = Owner("Jordan", pets=[Pet("Cat", "cat"), Pet("Dog", "dog")])
    owner.pets[0].tasks = [Task("Later", 15, scheduled_time="10:00"),
                           Task("Overlap", 30, scheduled_time="09:15")]
    owner.pets[1].tasks = [Task("First", 30, scheduled_time="09:00"),
                           Task("Nested", 5, scheduled_time="09:20")]
    before = asdict(owner)
    scheduler = Scheduler()
    assert scheduler.next_available_slot(owner, 15, "09:00", "11:00", DAY) == "09:45"
    assert scheduler.next_available_slot(owner, 20, "09:00", "11:00", DAY) == "10:15"
    assert scheduler.next_available_slot(owner, 60, "09:00", "11:00", DAY) is None
    assert asdict(owner) == before


def test_slot_dates_midnight_and_ignored_tasks():
    owner = Owner("Jordan", pets=[Pet("Cat", "cat", tasks=[
        Task("Previous night", 90, scheduled_time="23:30", due_date=DAY - timedelta(days=1)),
        Task("Tomorrow", 1440, scheduled_time="00:00", due_date=DAY + timedelta(days=1)),
        Task("Completed", 1440, scheduled_time="00:00", last_completed_date=DAY),
        Task("Untimed", 1440),
    ])])
    assert Scheduler().next_available_slot(owner, 30, "00:00", "02:00", DAY) == "01:00"
    assert Scheduler().next_available_slot(owner, 30, "23:30", "24:00", DAY) == "23:30"
    assert Scheduler().next_available_slot(owner, 31, "23:30", "24:00", DAY) is None


@pytest.mark.parametrize("duration,start,end", [
    (0, "09:00", "10:00"), (-1, "09:00", "10:00"), (True, "09:00", "10:00"),
    (2.5, "09:00", "10:00"), (10, "9:00", "10:00"), (10, "24:00", "24:00"),
    (10, "09:00", "09:00"), (10, "23:00", "01:00"), (10, "09:00", "25:00"),
])
def test_invalid_slot_inputs(duration, start, end):
    with pytest.raises(ValueError):
        Scheduler().next_available_slot(Owner("Jordan"), duration, start, end, DAY)


def test_slot_search_matches_minute_by_minute_oracle():
    # Exhaustively compare small, unsorted interval combinations to an independent oracle.
    scheduler = Scheduler()
    for first in range(6):
        for second in range(6):
            intervals = [(second, second + 3), (first, first + 2)]
            owner = Owner("Jordan", pets=[Pet("Dog", "dog", tasks=[
                Task(str(i), end - start, scheduled_time=f"09:{start:02d}")
                for i, (start, end) in enumerate(intervals)
            ])])
            for duration in range(1, 11):
                expected = next((f"09:{minute:02d}" for minute in range(11 - duration)
                                 if all(minute + duration <= start or minute >= end
                                        for start, end in intervals)), None)
                assert scheduler.next_available_slot(owner, duration, "09:00", "09:10", DAY) == expected


def run_app(at):
    at = at.run(timeout=15)
    assert not at.exception
    return at


def test_ui_save_restart_load_and_editor_state(tmp_path, monkeypatch):
    path = tmp_path / "pets.json"
    monkeypatch.setattr(persistence, "DEFAULT_PATH", path)
    at = AppTest.from_file(str(ROOT / "app.py"))
    at.session_state["owner"] = sample_owner()
    run_app(at)
    run_app(at.button(key="save_data").click())
    assert path.exists()
    restarted = run_app(AppTest.from_file(str(ROOT / "app.py")))
    assert not restarted.session_state["owner"].pets
    run_app(restarted.button(key="load_data").click())
    assert asdict(restarted.session_state["owner"]) == asdict(sample_owner())
    assert restarted.text_input(key="owner_name").value == "Jordán"
    assert restarted.number_input(key="available_minutes").value == 90
    assert restarted.checkbox(key="prefer_short_tasks").value is True
    # Loading again clears a cached plan, stale draft and references to old objects.
    run_app(restarted.button(key="generate_schedule").click())
    old_owner = restarted.session_state["owner"]
    restarted.text_input(key="edit_title").set_value("Unsaved draft")
    run_app(restarted.button(key="load_data").click())
    assert restarted.session_state["owner"] is not old_owner
    assert "plan" not in restarted.session_state
    assert restarted.text_input(key="edit_title").value == "Feeding"
    restarted.text_input(key="edit_title").set_value("Restored edit")
    run_app(restarted.button(key="edit_save").click())
    assert restarted.session_state["owner"].pets[0].tasks[1].name == "Restored edit"


def test_ui_failed_load_preserves_live_owner_and_plan(tmp_path, monkeypatch):
    path = tmp_path / "pets.json"
    monkeypatch.setattr(persistence, "DEFAULT_PATH", path)
    at = AppTest.from_file(str(ROOT / "app.py"))
    owner = sample_owner()
    at.session_state["owner"] = owner
    run_app(at)
    run_app(at.button(key="generate_schedule").click())
    plan = at.session_state["plan"]
    for content in (None, "{bad json"):
        if content is not None:
            path.write_text(content, encoding="utf-8")
        run_app(at.button(key="load_data").click())
        assert at.session_state["owner"] is owner
        assert at.session_state["plan"] is plan
        assert any("Could not load" in error.value for error in at.error)


def test_ui_slot_search_success_no_fit_and_invalid_input():
    at = AppTest.from_file(str(ROOT / "app.py"))
    at.session_state["owner"] = Owner("Jordan", pets=[Pet("Dog", "dog", tasks=[
        Task("Walk", 30, scheduled_time="09:00"),
    ])])
    run_app(at)
    run_app(at.button(key="find_slot").click())
    assert any("Next available slot: 09:30" in message.value for message in at.success)
    at.text_input(key="slot_end").set_value("09:45")
    run_app(at.button(key="find_slot").click())
    assert any("No free interval" in message.value for message in at.info)
    at.text_input(key="slot_start").set_value("bad")
    run_app(at.button(key="find_slot").click())
    assert any("HH:MM" in message.value for message in at.error)
