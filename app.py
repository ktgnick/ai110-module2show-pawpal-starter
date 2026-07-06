import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care tasks for the day, ordered by priority and time.")

# --- Session memory ------------------------------------------------------
# Streamlit reruns this script top-to-bottom on every interaction. Storing the
# Owner in st.session_state keeps our pets and tasks alive across those reruns
# instead of rebuilding an empty Owner each time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=120)

owner = st.session_state.owner

# --- Owner settings ------------------------------------------------------
st.subheader("Owner")
col_a, col_b = st.columns(2)
with col_a:
    owner.name = st.text_input("Owner name", value=owner.name)
with col_b:
    owner.set_available_time(
        st.number_input(
            "Time available today (minutes)",
            min_value=0,
            max_value=1440,
            value=owner.available_minutes,
            step=15,
        )
    )

st.divider()

# --- Add a pet -----------------------------------------------------------
st.subheader("Add a pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed (optional)", value="")
    if st.form_submit_button("Add pet") and pet_name.strip():
        owner.add_pet(Pet(pet_name.strip(), species=species, breed=breed.strip() or None))
        st.success(f"Added {pet_name.strip()}.")

if not owner.pets:
    st.info("No pets yet. Add one above to get started.")
    st.stop()

# --- Add a task to a pet -------------------------------------------------
st.subheader("Add a task")
pet_names = [pet.name for pet in owner.pets]
with st.form("add_task_form", clear_on_submit=True):
    target_name = st.selectbox("For which pet?", pet_names)
    task_title = st.text_input("Task title", value="Morning walk")
    c1, c2, c3 = st.columns(3)
    with c1:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with c2:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with c3:
        preferred_time = st.text_input("Time (HH:MM, optional)", value="")
    category = st.text_input("Category (optional)", value="")
    if st.form_submit_button("Add task") and task_title.strip():
        pet = owner.pets[pet_names.index(target_name)]
        pet.add_task(
            Task(
                task_title.strip(),
                int(duration),
                priority,
                category=category.strip() or None,
                preferred_time=preferred_time.strip() or None,
            )
        )
        st.success(f"Added '{task_title.strip()}' to {target_name}.")

# --- Current pets & tasks ------------------------------------------------
scheduler = Scheduler()

st.subheader("Pets & tasks")

# Surface time conflicts across ALL pets up front, so the owner sees them
# before they try to build a schedule.
conflicts = scheduler.detect_conflicts(owner.all_tasks())
for warning in conflicts:
    st.warning(warning)

status_filter = st.radio(
    "Show", ["All", "Pending", "Completed"], horizontal=True, index=0
)

for pet in owner.pets:
    tasks = pet.get_tasks()
    if status_filter == "Pending":
        tasks = scheduler.filter_by_status(tasks, completed=False)
    elif status_filter == "Completed":
        tasks = scheduler.filter_by_status(tasks, completed=True)
    tasks = scheduler.sort_by_time(tasks)  # chronological order

    with st.expander(f"{pet.name} ({pet.species}) — {len(tasks)} task(s)", expanded=True):
        if not tasks:
            st.caption("No tasks to show.")
        for i, task in enumerate(tasks):
            recur = f" · 🔁 {task.recurrence}" if task.recurrence else ""
            when = task.preferred_time or "--:--"
            row, action = st.columns([5, 1])
            with row:
                mark = "✅" if task.completed else "⬜️"
                st.write(f"{mark} **{when}** · {task.name} — {task.duration} min [{task.priority}]{recur}")
            with action:
                if not task.completed and st.button("Done", key=f"done_{pet.name}_{i}"):
                    upcoming = pet.mark_task_complete(task)
                    if upcoming is not None:
                        st.toast(f"Next '{task.name}' scheduled for {upcoming.due_date}.")
                    st.rerun()

st.divider()

# --- Build the schedule --------------------------------------------------
st.subheader("Today's Schedule")
if st.button("Generate schedule", type="primary"):
    if conflicts:
        st.warning(
            f"{len(conflicts)} time conflict(s) detected — lower-priority clashes "
            "will be left out of the plan below."
        )

    plan = scheduler.schedule_owner(owner)
    rows = plan.to_display()
    if rows:
        st.success(f"Planned {len(rows)} task(s).")
        st.table(rows)
        st.caption(f"Total scheduled: {plan.total_time} min of {owner.available_minutes} available.")
    else:
        st.warning("Nothing could be scheduled. Add tasks or increase available time.")

    if plan.skipped:
        st.markdown("**Not scheduled:**")
        for task, reason in plan.skipped:
            st.write(f"- {task.name}: {reason}")

    with st.expander("Why this plan?"):
        st.text(plan.explain())
