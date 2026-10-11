"""Versioned JSON storage for the four PawPal+ domain classes."""

from dataclasses import asdict
from datetime import date
import json
import os
from pathlib import Path
import tempfile

from pawpal_system import Owner, Pet, Task


DEFAULT_PATH = Path(__file__).resolve().parent / "data" / "pawpal.json"


def _fields(value, expected: set[str]) -> dict:
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError("Saved data has missing or unexpected fields.")
    return value


def _text(value, *, allow_empty=False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ValueError("Saved names and species must be nonempty text.")
    return value


def _date(value) -> date | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Saved dates must use YYYY-MM-DD or null.")
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("Saved dates must use YYYY-MM-DD.")
    return parsed


def _decode(document) -> Owner:
    """Validate the whole document before returning a new object graph."""
    _fields(document, {"version", "owner"})
    if type(document["version"]) is not int or document["version"] != 1:
        raise ValueError("Unsupported save version; expected version 1.")
    record = _fields(document["owner"], {"name", "available_minutes", "prefer_short_tasks", "pets"})
    if not isinstance(record["pets"], list):
        raise ValueError("Saved pets must be a list.")
    owner = Owner(_text(record["name"]), record["available_minutes"], record["prefer_short_tasks"])
    for pet_record in record["pets"]:
        _fields(pet_record, {"name", "species", "breed", "tasks"})
        if not isinstance(pet_record["tasks"], list):
            raise ValueError("Saved tasks must be a list.")
        pet = Pet(_text(pet_record["name"]), _text(pet_record["species"]),
                  _text(pet_record["breed"], allow_empty=True))
        for task_record in pet_record["tasks"]:
            _fields(task_record, {"name", "duration_minutes", "priority", "recurrence",
                                  "last_completed_date", "scheduled_time", "due_date"})
            values = dict(task_record)
            values["due_date"] = _date(values["due_date"])
            values["last_completed_date"] = _date(values["last_completed_date"])
            pet.add_task(Task(**values))
        owner.add_pet(pet)
    return owner


def load_owner(path: str | Path | None = None) -> Owner:
    """Load validated pets, tasks and settings; never modify a live owner."""
    source = DEFAULT_PATH if path is None else Path(path)
    return _decode(json.loads(source.read_text(encoding="utf-8")))


def save_owner(owner: Owner, path: str | Path | None = None) -> None:
    """Validate and atomically replace a JSON save, preserving it on failure."""
    destination = DEFAULT_PATH if path is None else Path(path)
    payload = json.dumps({"version": 1, "owner": asdict(owner)},
                         default=lambda value: value.isoformat(), ensure_ascii=False, indent=2)
    _decode(json.loads(payload))
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destination.parent,
                                         prefix=".pawpal-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(payload + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
