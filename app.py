import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=30)
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

owner = st.session_state.owner

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
- Set each task's duration and priority.
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
st.caption("Select a pet and add a care task with its duration and priority.")
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

if st.button("Add task", disabled=selected_pet_index is None, key="add_task"):
    try:
        task = Task(name=task_title, duration_minutes=int(duration), priority=priority)
        owner.pets[selected_pet_index].add_task(task)
    except ValueError as error:
        st.error(str(error))
    else:
        st.session_state.pop("plan", None)
        st.success(f"Added {task.name} for {owner.pets[selected_pet_index].name}.")

task_pairs = owner.get_all_tasks()
if task_pairs:
    st.write("Current tasks:")
    st.table([
        {"Pet": pet.name, "Task": task.name, "Minutes": task.duration_minutes, "Priority": task.priority}
        for pet, task in task_pairs
    ])
else:
    st.info("No tasks yet. Select a pet and add a task above.")

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
        st.session_state.plan = st.session_state.scheduler.generate_plan(owner)
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
