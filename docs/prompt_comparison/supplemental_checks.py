"""Evaluator-only AppTest probes; separate from the unchanged frozen tests.

Run once per candidate in a fresh Python process, passing its absolute root.
Results describe observations; they do not revise the frozen 19-test score.
"""
from datetime import date
import json
from pathlib import Path
import sys

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
from streamlit.testing.v1 import AppTest
from pawpal_system import Owner, Pet, Scheduler, Task


def start(tasks=None):
    task = Task('Care', 10, scheduled_time='09:00', due_date=date.today())
    pet = Pet('Mochi', 'cat', tasks=tasks if tasks is not None else [task])
    owner = Owner('Jordan', 30, pets=[pet])
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=15)
    plan = Scheduler().generate_plan(owner)
    at.session_state['owner'] = owner
    at.session_state['scheduler'] = Scheduler()
    at.session_state['plan'] = plan
    at.run()
    assert not at.exception
    return at, owner, pet, pet.tasks[0], plan


def observations(at, owner, before, plan):
    return {
        'exceptions': [str(e.value) for e in at.exception],
        'tasks_unchanged': [vars(t).copy() for _, t in owner.get_all_tasks()] == before,
        'plan_retained': 'plan' in at.session_state and at.session_state['plan'] is plan,
        'errors': [str(e.value) for e in at.error],
        'successes': [str(e.value) for e in at.success],
        'info': [str(e.value) for e in at.info],
    }


results = []
for value in (None, 0, -1, 2.5):
    at, owner, pet, task, plan = start()
    before = [vars(t).copy() for _, t in owner.get_all_tasks()]
    try:
        at.text_input(key='edit_title').set_value('Proposed title')
        at.number_input(key='edit_duration').set_value(value)
        at.button(key='edit_save').click().run()
        result = observations(at, owner, before, plan)
        result['saved_title'] = task.name
        result['saved_duration'] = task.duration_minutes
        result['atomic_rejection'] = bool(result['errors']) and result['tasks_unchanged'] and result['plan_retained'] and not result['exceptions']
    except Exception as error:
        result = {'harness_exception': f'{type(error).__name__}: {error}',
                  'note': 'AppTest did not submit this input; no browser behavior inferred.'}
    results.append({'probe': 'invalid_duration', 'value': value, **result})

# Stale completion with no other pending task (frozen test leaves other tasks).
at, owner, pet, task, plan = start()
at.text_input(key='edit_title').set_value('Stale draft')
task.mark_complete()
before = [vars(t).copy() for _, t in owner.get_all_tasks()]
at.button(key='edit_save').click().run()
results.append({'probe': 'last_pending_completed_before_save', **observations(at, owner, before, plan),
                'active_save_buttons': sum(not b.disabled for b in at.button if b.key == 'edit_save')})

# A nonfirst task remains selected after its displayed title changes.
first, second = Task('Care', 10), Task('Care', 10)
at, owner, pet, task, plan = start([first, second])
at.selectbox(key='edit_task').select(at.selectbox(key='edit_task').options[1]).run()
at.text_input(key='edit_title').set_value('Renamed second')
at.button(key='edit_save').click().run()
at.text_input(key='edit_title').set_value('Renamed again')
at.button(key='edit_save').click().run()
results.append({'probe': 'repeated_rename_nonfirst_task', 'exceptions': [str(e.value) for e in at.exception],
                'first_unchanged': first.name == 'Care', 'second_updated': second.name == 'Renamed again',
                'same_objects': pet.tasks[0] is first and pet.tasks[1] is second and len(pet.tasks) == 2})

# Date navigation bounds are an observation, not a browser test.
at, owner, pet, task, plan = start()
control = at.date_input(key='edit_due_date')
results.append({'probe': 'date_control_bounds', 'minimum': control.proto.min, 'maximum': control.proto.max})

print(json.dumps({'candidate_root': str(ROOT), 'local_test_date': str(date.today()), 'results': results}, indent=2, default=str))
