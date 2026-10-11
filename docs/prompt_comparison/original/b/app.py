from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task


def complete_task_today(pet: Pet, task: Task) -> None:
    """Complete a task once, clear the old plan, and save a success message."""
    if task.completed:
        return
    next_task = pet.complete_task(task, on_date=date.today())
    st.session_state.pop("plan", None)
    message = f"Completed {pet.name}: {task.name}."
    if next_task is not None:
        message += f" Next {next_task.recurrence} occurrence is due {next_task.due_date}."
    st.session_state.completion_notice = message


def load_task_editor(pet: Pet, task: Task) -> None:
    """Load a fresh draft without changing the selected session objects."""
    st.session_state.edit_target = (pet, task)
    st.session_state.edit_title = task.name
    st.session_state.edit_duration = task.duration_minutes
    st.session_state.edit_priority = task.priority
    st.session_state.edit_recurrence = task.recurrence
    st.session_state.edit_scheduled_time = task.scheduled_time or ""
    st.session_state.edit_due_date = task.due_date


def save_task_changes(pet: Pet, task: Task) -> None:
    """Validate and save the rendered target before the next display rerun."""
    # Capture the rendered objects in callback args: a stale submission must
    # never fall through to whichever pending task now occupies its old index.
    owner = st.session_state.owner
    if task.completed or not any(
        current_pet is pet and current_task is task
        for current_pet, current_task in owner.get_all_tasks()
    ):
        st.session_state.edit_notice = (
            "error", "This task is completed or no longer available. Select a pending task to edit."
        )
        return

    before = vars(task).copy()
    try:
        task.update_details(
            name=st.session_state.edit_title.strip(),
            duration_minutes=st.session_state.edit_duration,
            priority=st.session_state.edit_priority,
            recurrence=st.session_state.edit_recurrence,
            scheduled_time=st.session_state.edit_scheduled_time.strip() or None,
            due_date=st.session_state.edit_due_date,
        )
    except ValueError as error:
        st.session_state.edit_notice = ("error", str(error))
    else:
        if vars(task) != before:
            st.session_state.pop("plan", None)
            st.session_state.edit_notice = ("success", f"Saved changes to {pet.name}: {task.name}.")
        else:
            st.session_state.edit_notice = ("info", "No changes to save.")
        load_task_editor(pet, task)


def render_task_editor(task_pairs: list[tuple[Pet, Task]]) -> None:
    """Offer every pending task independently of the browse filters."""
    st.markdown("### Edit a pending task")
    notice = st.session_state.pop("edit_notice", None)
    if notice:
        kind, message = notice
        {"error": st.error, "success": st.success, "info": st.info}[kind](message)

    options = {
        f"{number}. {pet.name}: {task.name}": (pet, task)
        for number, (pet, task) in enumerate(task_pairs, start=1)
        if not task.completed
    }
    if not options:
        st.session_state.pop("edit_target", None)
        st.session_state.pop("edit_task", None)
        st.info("No pending tasks to edit. Add a pet and a task above, or add a new task if all are completed.")
        return

    previous_pet, previous_task = st.session_state.get("edit_target", (None, None))
    if st.session_state.get("edit_task") not in options:
        # A saved title changes its label; retain selection by identity.
        st.session_state.edit_task = next(
            (label for label, (pet, task) in options.items()
             if pet is previous_pet and task is previous_task),
            next(iter(options)),
        )
    label = st.selectbox("Pending task", list(options), key="edit_task")
    pet, task = options[label]
    if pet is not previous_pet or task is not previous_task:
        load_task_editor(pet, task)

    st.caption("Changes apply only when saved. Selecting another task discards unsaved edits.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Title", key="edit_title")
    with col2:
        st.number_input("Duration (minutes)", min_value=1, step=1, key="edit_duration")
    with col3:
        st.selectbox("Priority", ["high", "medium", "low"], key="edit_priority")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Scheduled time (optional)", placeholder="HH:MM", key="edit_scheduled_time")
    with col2:
        st.selectbox("Recurrence", ["once", "daily", "weekly"], key="edit_recurrence")
    with col3:
        st.date_input("Due date (optional)", value=None, min_value=date.min,
                      max_value=date.max, key="edit_due_date")
    st.button("Save changes", key="edit_save", on_click=save_task_changes, args=(pet, task))


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=30)
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

owner = st.session_state.owner
scheduler = st.session_state.scheduler

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+. Add your pets and care tasks, then build a daily plan
that fits your available time.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

Your pets and tasks stay available as you use the app in this session.
"""
    )

with st.expander("How to use PawPal+", expanded=True):
    st.markdown(
        """
- Add your pets and select a pet when adding a task.
- Set each task's duration, priority, and recurrence; optionally add a time and due date.
- Browse tasks by time, filter by pet or completion status, and review same-time warnings.
- Mark tasks complete today; daily and weekly tasks create their next occurrence automatically.
- Choose your available time and generate a plan for all your pets.
- Review selected tasks and explanations for anything skipped.
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")
owner_name = st.text_input("Owner name", value=owner.name, key="owner_name")
if owner_name.strip():
    owner.name = owner_name.strip()
else:
    st.warning("Enter an owner name before generating a schedule.")

pet_name = st.text_input("Pet name", value="Mochi", key="pet_name")
species = st.selectbox("Species", ["dog", "cat", "other"], key="species")

if st.button("Add pet", key="add_pet"):
    if not pet_name.strip():
        st.error("Pet name must not be empty.")
    else:
        try:
            owner.add_pet(Pet(name=pet_name.strip(), species=species))
        except ValueError as error:
            st.error(str(error))
        else:
            st.session_state.pop("plan", None)
            st.success(f"Added {pet_name.strip()}.")

if owner.pets:
    st.write("Your pets:")
    st.table([{"Pet": pet.name, "Species": pet.species} for pet in owner.pets])
else:
    st.info("No pets yet. Add a pet above to start adding care tasks.")

st.markdown("### Tasks")
st.caption("Select a pet and add a care task. Leave the time or due date blank when not needed.")
completion_notice = st.session_state.pop("completion_notice", None)
if completion_notice:
    st.success(completion_notice)
if owner.pets and st.session_state.get("selected_pet") is None:
    st.session_state.selected_pet = 0
selected_pet_index = st.selectbox(
    "Task's pet",
    options=list(range(len(owner.pets))),
    format_func=lambda index: f"{index + 1}. {owner.pets[index].name} ({owner.pets[index].species})",
    disabled=not owner.pets,
    key="selected_pet",
)

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk", key="task_title")
with col2:
    duration = st.number_input(
        "Duration (minutes)", min_value=1, max_value=240, value=20, key="duration"
    )
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2, key="priority")

col1, col2, col3 = st.columns(3)
with col1:
    scheduled_time = st.text_input(
        "Scheduled time (optional)", placeholder="HH:MM", key="scheduled_time",
        help="Use 24-hour time, such as 09:05 or 18:30. Leave blank for an untimed task.",
    )
with col2:
    recurrence = st.selectbox("Recurrence", ["once", "daily", "weekly"], key="recurrence")
with col3:
    due_date = st.date_input(
        "Due date (optional)", value=None, key="due_date",
        help="Future tasks are skipped in today's plan. Undated pending tasks are eligible today.",
    )

if st.button("Add task", disabled=selected_pet_index is None, key="add_task"):
    try:
        task = Task(
            name=task_title,
            duration_minutes=int(duration),
            priority=priority,
            scheduled_time=scheduled_time.strip() or None,
            recurrence=recurrence,
            due_date=due_date,
        )
        owner.pets[selected_pet_index].add_task(task)
    except ValueError as error:
        st.error(str(error))
    else:
        st.session_state.pop("plan", None)
        st.success(f"Added {task.name} for {owner.pets[selected_pet_index].name}.")

task_pairs = owner.get_all_tasks()
render_task_editor(task_pairs)
st.markdown("### Browse tasks")
col1, col2 = st.columns(2)
with col1:
    pet_filter = st.text_input(
        "Filter by pet name", key="pet_filter",
        help="Leave blank for all pets. Matches the full name, ignoring case.",
    )
with col2:
    status_filter = st.selectbox(
        "Completion status", ["All", "Pending", "Completed"], key="status_filter",
    )
completed_filter = {"All": None, "Pending": False, "Completed": True}[status_filter]
visible_pairs = scheduler.sort_tasks_by_time(
    scheduler.filter_tasks(owner, pet_name=pet_filter.strip() or None, completed=completed_filter)
)
st.caption("Sorted by scheduled time of day; untimed tasks appear last. Filters only affect this list.")
if task_pairs:
    if visible_pairs:
        st.table([
            {
                "Time": task.scheduled_time or "Untimed",
                "Pet": pet.name,
                "Task": task.name,
                "Minutes": task.duration_minutes,
                "Priority": task.priority,
                "Recurrence": task.recurrence,
                "Due date": str(task.due_date) if task.due_date else "No date",
                "Status": "Completed" if task.completed else "Pending",
            }
            for pet, task in visible_pairs
        ])
        pending_pairs = [(pet, task) for pet, task in visible_pairs if not task.completed]
        if pending_pairs:
            with st.expander("Complete a task"):
                st.caption(
                    "Completion is recorded for today. Daily and weekly tasks create one new "
                    "occurrence due one or seven days after completion."
                )
                for pet, task in pending_pairs:
                    # Object identity keeps each button tied to its task after sorting or filtering.
                    st.button(
                        f"Complete today: {pet.name} - {task.name} "
                        f"({task.scheduled_time or 'Untimed'}, due {task.due_date or 'No date'})",
                        key=f"complete_task_{id(task)}",
                        on_click=complete_task_today,
                        args=(pet, task),
                    )
    else:
        st.info("No tasks match these filters.")
else:
    st.info("No tasks yet. Select a pet and add a task above.")

st.markdown("### Same-time conflicts")
st.caption(
    "Checks all pending tasks across pets and dates, regardless of the filters above. "
    "Tasks without a due date use today. Only identical start times on the same date "
    "are checked; overlapping durations with different start times are not detected."
)
conflicts = scheduler.detect_conflicts(task_pairs, on_date=date.today())
for warning in conflicts:
    st.warning(warning)
if task_pairs and not conflicts:
    st.info("No identical-start-time conflicts found.")

st.divider()

st.subheader("Build Schedule")
st.caption("Plan care across all your pets using one shared time budget.")
available_minutes = st.number_input(
    "Available time (minutes)", min_value=0, value=owner.available_minutes, step=5,
    key="available_minutes",
)
prefer_short_tasks = st.checkbox(
    "Prefer shorter tasks when priorities match", value=owner.prefer_short_tasks,
    key="prefer_short_tasks",
)

settings_valid = True
if (available_minutes, prefer_short_tasks) != (owner.available_minutes, owner.prefer_short_tasks):
    try:
        owner.update_settings(
            available_minutes=int(available_minutes), prefer_short_tasks=prefer_short_tasks
        )
    except ValueError as error:
        settings_valid = False
        st.error(str(error))
    else:
        st.session_state.pop("plan", None)

if st.button(
    "Generate schedule", disabled=not owner_name.strip() or not settings_valid,
    key="generate_schedule",
):
    try:
        st.session_state.plan = scheduler.generate_plan(owner)
    except ValueError as error:
        st.session_state.pop("plan", None)
        st.error(str(error))

plan = st.session_state.get("plan")
if plan is not None:
    st.markdown("### Today's Schedule")
    st.write(f"Planned: {plan['total_minutes']} min | Remaining: {plan['remaining_minutes']} min")
    if plan["selected"]:
        st.table([
            {
                "Order": number,
                "Pet": entry["pet"].name,
                "Task": entry["task"].name,
                "Time": entry["task"].scheduled_time or "Untimed",
                "Minutes": entry["task"].duration_minutes,
                "Priority": entry["task"].priority,
                "Why selected": entry["reason"],
            }
            for number, entry in enumerate(plan["selected"], start=1)
        ])
    elif not task_pairs:
        st.info("Add a pet and care tasks to build your first schedule.")
    else:
        st.info("No tasks could be scheduled. Review the skipped tasks below.")

    if plan["skipped"]:
        st.markdown("### Skipped tasks")
        st.table([
            {"Pet": entry["pet"].name, "Task": entry["task"].name, "Reason": entry["reason"]}
            for entry in plan["skipped"]
        ])
else:
    st.info("Generate a schedule after adding tasks or changing your care settings.")
