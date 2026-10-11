# Frozen shared specification: pending-task editing

Baseline commit: `98805949bffcb69f5e5299a4deaafe6b8bdb3623`.

This specification and the supplied acceptance tests are identical for both
candidates. Only the strategy instruction at the end of each prompt differs.
The comparison has not been run. No winner has been selected.

## Acceptance criteria

| ID | Acceptance criterion |
| --- | --- |
| AC1 | Select one specific pending task across all pets. Distinguish separate objects even when pet names or task details match. Completed tasks are not editable. |
| AC2 | Prepopulate title, duration, priority, recurrence, scheduled time, and due date from the selected task. Switching tasks must not carry another task's values into the editor. |
| AC3 | Support editing all seven fields. Title maps to `Task.name`; recurrence supports `once`, `daily`, and `weekly`. Blank scheduled time or due date clears that optional value. |
| AC4 | Change task data only when **Save changes** is submitted. Opening the editor, typing, switching selection, and ordinary reruns must not modify tasks. |
| AC5 | Save through `Task.update_details()`. Invalid input must show a readable error and leave every task field unchanged, including otherwise valid proposed edits. |
| AC6 | Preserve the selected Task object, its owning Pet, completion state, and position in the pet's task collection. Do not replace, append, remove, or complete tasks during editing. |
| AC7 | Clear the cached plan only after a successful save that changes task data. Invalid submissions, navigation, and unchanged submissions retain the existing plan. Existing invalidation for other app actions remains intact. |
| AC8 | After saving, the displayed chronological order and same-start-time warnings reflect the updated data without another user action. Untimed tasks remain last. |
| AC9 | Changing recurrence does not create another task. Later completion still creates exactly one next occurrence using the existing backend behavior. |
| AC10 | Repeated saves and reruns do not create duplicates. If the selected task becomes completed before submission, reject the stale edit safely. |
| AC11 | No-pet, no-task, and all-completed states display helpful guidance without exceptions. |
| AC12 | Preserve existing creation, completion, filtering, priority scheduling, time budgets, exact-time conflict semantics, and all 97 baseline tests. |

The earlier wording "all seven fields" is retained. It means title, duration,
priority, recurrence, scheduled time, and due date: six editable task attributes.
Selection is the seventh editor control, not a new task attribute. Both
candidates receive this explicit clarification; do not invent another field.

## Shared behavior details

- The editor lists all pending tasks independently of browse filters.
- Selecting another task discards unsaved edits and loads that task's values.
- Normalize title and time whitespace as in the existing UI/backend. A blank
  scheduled time becomes `None`. A cleared single-date input becomes `None`.
- Compare normalized saved values when deciding whether anything changed.
  An unchanged submission preserves the current plan.
- Preserve current session objects. Do not move a task between pets, change its
  completion date, or alter any nonselected task.
- Completion after an edit remains the existing `Pet.complete_task()` workflow.
- On stale submission, do not redirect the submitted values to a different task.
  Leave the completed task and all other tasks unchanged, and show guidance.
- A successful change shows `st.success`; rejected values show `st.error`.
  Existing conflict warnings continue to use `st.warning`.
- No persistence, deletion, interval-overlap detection, or unrelated UI redesign.

## Common black-box test interface

These controls make the exact same AppTest file usable against both candidates.
They prescribe a small user-facing interface, not a helper function, callback,
form layout, task lookup algorithm, or storage implementation.

| Streamlit control | Fixed key | Values / behavior |
| --- | --- | --- |
| `st.selectbox` | `edit_task` | Unique string options in pending `Owner.get_all_tasks()` order. Each displayed string includes pet and task names and a distinguishing number/token. Use strings as the actual selectbox options so AppTest can select by the displayed string. |
| `st.text_input` | `edit_title` | Selected task name |
| `st.number_input` | `edit_duration` | Positive whole minutes; prevent invalid numeric values at the widget or reject them atomically |
| `st.selectbox` | `edit_priority` | `high`, `medium`, `low` |
| `st.selectbox` | `edit_recurrence` | `once`, `daily`, `weekly` |
| `st.text_input` | `edit_scheduled_time` | HH:MM or blank |
| `st.date_input` | `edit_due_date` | Single date or `None`, clearable |
| Button or form submit button | `edit_save` | Label `Save changes` |

When pending tasks exist, expose one editor with these keys. Default selection
may be the first pending task. With none, hide/disable the editor and show useful
`st.info` guidance. Keep existing widget keys and state entries (`owner`,
`scheduler`, and cached `plan`) working. Keep browse-table column names `Task`,
`Pet`, `Time`, and `Status`; either a table or dataframe is accepted.

The tests inspect visible controls, displayed rows/warnings, public backend
objects, and the existing cached plan. They do not call candidate helper
functions. One test wraps and delegates to the real `Task.update_details()` to
verify required API use; it does not mock its behavior.

## Scope and execution controls

- Read `app.py`, `pawpal_system.py`, `tests/test_pawpal.py`, `README.md`, and
  `ai_interactions.md` before editing.
- Modify only `app.py`. Preserve backend APIs and the existing 97 tests exactly.
  Do not modify the supplied acceptance test file.
- Do not install packages, change dependencies, edit documentation, commit,
  merge, push, or inspect another candidate's worktree, branch, or output.
- If a backend issue prevents integration, report it without changing backend
  code. Otherwise finish within the approved candidate worktree.
- Use a fresh session for each candidate with the same exposed model/version,
  reasoning setting, permissions, tools, and time allowance. The executor must
  record these before either run. If model information is unavailable, say so.
- Use one initial request per candidate, at most 30 minutes of active run time,
  no human hints. Self-correction using test results is allowed equally. Record
  approval/infrastructure pauses separately. Do not extend one candidate's
  allowance based on the other candidate's result.
- Run candidates sequentially using the same recorded Python executable and
  dependency environment. Record the chosen order before starting. Do not run
  them until the user explicitly authorizes the next step.
- Tests capture `date.today()` for each fixture and use relative dates. Record
  the local test date; do not compare runs crossing local midnight without
  rerunning verification for both under the same date conditions.
- Preserve original candidate output before any human repairs or integration.
- Report actual commands, results, changes, and limitations. AppTest is not a
  visual browser review; do not claim unperformed checks.

## Identical verification commands

From the candidate worktree, using the recorded Python executable:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python -m pytest tests/test_pawpal.py -p no:cacheprovider
python -m pytest tests/test_pending_task_editing.py -p no:cacheprovider
python -m pytest -p no:cacheprovider
python main.py
python -c "from pathlib import Path; compile(Path('app.py').read_text(encoding='utf-8'), 'app.py', 'exec'); print('app.py syntax OK')"
git diff --check
git diff --stat
git status --short
```

All 97 baseline cases must pass separately. Report acceptance failures honestly;
do not skip, weaken, or rewrite the frozen tests. Preserve the protected file
hashes. The evaluator also checks that only `app.py` differs from the baseline
(apart from the identical untracked acceptance test supplied during preparation).

## Comparison and evidence

Correctness gates: baseline preservation, task identity, atomicity, and no
duplicate creation. Report AC1-AC12 individually as PASS, FAIL, or NOT VERIFIED.
Among candidates passing the gates, review clarity, usability, scope, and human
correction effort. Runtime and diff size are descriptive, not automatic winners.
One run per strategy is a case study, not a universal model-performance claim.
