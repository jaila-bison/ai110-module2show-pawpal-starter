import streamlit as st
from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, TaskCategory, Scheduler, DailyPlan, RecurrenceType

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+**, your intelligent pet care planning assistant!
Manage your pets, schedule tasks, and optimize your daily pet care routine.
"""
)

# ============================================================================
# STEP 1: Initialize Owner in session_state (persists across reruns)
# ============================================================================
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_time=480)

owner = st.session_state.owner

# ============================================================================
# OWNER SETTINGS
# ============================================================================
st.subheader("👤 Owner Settings")
col1, col2 = st.columns(2)
with col1:
    new_owner_name = st.text_input("Owner name", value=owner.name)
    if new_owner_name != owner.name:
        owner.name = new_owner_name

with col2:
    available_hours = st.number_input(
        "Available hours per day",
        min_value=1,
        max_value=24,
        value=owner.available_time // 60
    )
    owner.set_available_time(available_hours * 60)

st.divider()

# ============================================================================
# STEP 2: Add Pet functionality - Uses Owner.add_pet() method
# ============================================================================
st.subheader("🐾 Manage Pets")

with st.expander("➕ Add a New Pet", expanded=len(owner.pets) == 0):
    col1, col2 = st.columns(2)
    with col1:
        new_pet_name = st.text_input("Pet name", value="", key="new_pet_name")
    with col2:
        new_pet_species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"], key="new_pet_species")

    if st.button("Add Pet", type="primary"):
        if new_pet_name:
            new_pet = Pet(name=new_pet_name, species=new_pet_species)
            owner.add_pet(new_pet)  # 🎯 PHASE 2 METHOD: Owner.add_pet()
            st.success(f"✅ Added {new_pet_name} the {new_pet_species}!")
            st.rerun()
        else:
            st.error("Please enter a pet name.")

# Display current pets
if owner.pets:
    st.markdown("**Your Pets:**")
    for i, pet in enumerate(owner.pets):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"🐾 **{pet.name}**")
        with col2:
            st.write(f"_{pet.species}_")
        with col3:
            st.write(f"{len(pet.tasks)} tasks")
else:
    st.info("No pets yet. Add one above to get started!")

st.divider()

# ============================================================================
# STEP 3: Add Task functionality - Uses Pet.add_task() method
# ============================================================================
st.subheader("📋 Add Tasks")

if owner.pets:
    with st.expander("➕ Add a New Task", expanded=True):
        # Select which pet this task is for
        selected_pet_name = st.selectbox(
            "Select Pet",
            options=[pet.name for pet in owner.pets],
            key="task_pet_selector"
        )
        selected_pet = next(pet for pet in owner.pets if pet.name == selected_pet_name)

        # Task details
        col1, col2 = st.columns(2)
        with col1:
            task_description = st.text_input("Task description", value="", key="task_desc")
            task_category = st.selectbox(
                "Category",
                options=[cat.value for cat in TaskCategory],
                key="task_category"
            )

        with col2:
            task_duration = st.number_input("Duration (minutes)", min_value=5, max_value=240, value=30, key="task_dur")
            task_priority = st.selectbox(
                "Priority",
                options=[1, 2, 3],
                format_func=lambda x: f"{x} - {'High' if x == 1 else 'Medium' if x == 2 else 'Low'}",
                key="task_priority"
            )

        # Due time
        col1, col2 = st.columns(2)
        with col1:
            due_date = st.date_input("Due date", value=datetime.now().date(), key="task_date")
        with col2:
            due_time = st.time_input("Due time", value=datetime.now().time(), key="task_time")

        # Recurring task options
        st.markdown("**Recurring Task (Optional)**")
        col1, col2 = st.columns(2)
        with col1:
            recurrence_type = st.selectbox(
                "Recurrence",
                options=[r.value for r in RecurrenceType],
                format_func=lambda x: x.capitalize(),
                key="task_recurrence"
            )
        with col2:
            if recurrence_type != "none":
                recurrence_end = st.date_input(
                    "Recurrence end date (optional)",
                    value=None,
                    key="task_recurrence_end"
                )
            else:
                recurrence_end = None

        if st.button("Add Task", type="primary"):
            if task_description:
                # Combine date and time
                due_datetime = datetime.combine(due_date, due_time)

                # Handle recurrence end date
                recurrence_end_datetime = None
                if recurrence_end:
                    recurrence_end_datetime = datetime.combine(recurrence_end, due_time)

                # Create Task object
                new_task = Task(
                    description=task_description,
                    duration=task_duration,
                    priority=task_priority,
                    due_time=due_datetime,
                    category=TaskCategory(task_category),
                    recurrence=RecurrenceType(recurrence_type),
                    recurrence_end_date=recurrence_end_datetime
                )

                # 🎯 PHASE 2 METHOD: Pet.add_task()
                selected_pet.add_task(new_task)

                recurring_msg = f" (Recurring: {recurrence_type})" if recurrence_type != "none" else ""
                st.success(f"✅ Added task '{task_description}' for {selected_pet.name}!{recurring_msg}")
                st.rerun()
            else:
                st.error("Please enter a task description.")

    # Display all tasks with filtering and sorting
    st.markdown("**Current Tasks:**")

    # Add filtering and sorting controls
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_pet = st.selectbox(
            "Filter by Pet",
            options=["All"] + [pet.name for pet in owner.pets],
            key="filter_pet"
        )
    with col2:
        filter_status = st.selectbox(
            "Filter by Status",
            options=["Pending", "Completed", "All"],
            key="filter_status"
        )
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            options=["Priority", "Due Time", "Duration", "Category"],
            key="sort_by"
        )

    # Get tasks based on filters
    if filter_pet == "All":
        if filter_status == "Pending":
            display_tasks = owner.get_all_pending_tasks()
        elif filter_status == "Completed":
            display_tasks = owner.get_tasks_by_status(completed=True)
        else:
            display_tasks = owner.get_all_tasks()
    else:
        pet_tasks = owner.get_tasks_by_pet(filter_pet)
        if filter_status == "Pending":
            display_tasks = [t for t in pet_tasks if not t.is_completed]
        elif filter_status == "Completed":
            display_tasks = [t for t in pet_tasks if t.is_completed]
        else:
            display_tasks = pet_tasks

    # Apply sorting
    if sort_by == "Priority":
        display_tasks = owner.sort_tasks_by_priority(display_tasks, ascending=True)
    elif sort_by == "Due Time":
        display_tasks = owner.sort_tasks_by_time(display_tasks, ascending=True)
    elif sort_by == "Duration":
        display_tasks = owner.sort_tasks_by_duration(display_tasks, ascending=False)
    elif sort_by == "Category":
        display_tasks = owner.sort_tasks_by_category(display_tasks)

    # Display tasks
    if display_tasks:
        for task in display_tasks:
            priority_icon = "🔴" if task.priority == 1 else "🟡" if task.priority == 2 else "🟢"
            status_icon = "✅" if task.is_completed else "⏳"
            recurring_icon = "🔄" if task.is_recurring() else ""
            overdue_icon = "⚠️" if task.is_overdue() else ""

            st.write(
                f"{status_icon} {priority_icon} {recurring_icon} {overdue_icon} "
                f"**{task.description}** ({task.pet_name}) - {task.duration} min - "
                f"{task.category.value} - Due: {task.due_time.strftime('%m/%d %I:%M %p')}"
            )
    else:
        st.info(f"No {filter_status.lower()} tasks found.")
else:
    st.info("Add a pet first before creating tasks.")

st.divider()

# ============================================================================
# STEP 4: Generate Schedule - Uses Scheduler.generate_daily_plan() method
# ============================================================================
st.subheader("📅 Generate Daily Schedule")

if owner.pets and any(pet.get_pending_tasks() for pet in owner.pets):
    col1, col2 = st.columns([1, 3])
    with col1:
        start_time = st.time_input("Start time", value=datetime.now().time())
    with col2:
        st.write("")  # Spacing

    if st.button("🚀 Generate Optimized Schedule", type="primary", use_container_width=True):
        # 🎯 PHASE 2 METHOD: Scheduler.generate_daily_plan()
        scheduler = Scheduler(owner)
        start_datetime = datetime.combine(datetime.now().date(), start_time)
        daily_plan = scheduler.generate_daily_plan(start_time=start_datetime, check_conflicts=True)

        # Store in session state for display
        st.session_state.daily_plan = daily_plan
        st.session_state.scheduler = scheduler  # Store scheduler to access conflicts

        if scheduler.conflicts:
            st.warning(f"⚠️ {len(scheduler.conflicts)} conflict(s) detected - see details below")
        else:
            st.success("✅ Schedule generated successfully with no conflicts!")
        st.rerun()

    # Display conflicts if any
    if "scheduler" in st.session_state and st.session_state.scheduler.conflicts:
        st.markdown("### ⚠️ Scheduling Conflicts Detected")
        for conflict in st.session_state.scheduler.conflicts:
            severity_color = "🔴" if conflict.severity == "error" else "🟡"
            with st.expander(f"{severity_color} {conflict.conflict_type.replace('_', ' ').title()}", expanded=False):
                st.write(f"**Description:** {conflict.description}")
                if conflict.affected_tasks:
                    st.write("**Affected Tasks:**")
                    for task in conflict.affected_tasks:
                        st.write(f"  - {task.description} ({task.pet_name})")
        st.divider()

    # Display generated schedule
    if "daily_plan" in st.session_state:
        daily_plan = st.session_state.daily_plan

        st.markdown("### 📋 Today's Schedule")

        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tasks", len(daily_plan.scheduled_tasks))
        with col2:
            st.metric("Total Time", f"{daily_plan.total_duration} min")
        with col3:
            st.metric("Skipped Tasks", len(daily_plan.skipped_tasks))

        # Display scheduled tasks
        if daily_plan.scheduled_tasks:
            st.markdown("#### ✅ Scheduled Tasks")
            for i, scheduled_task in enumerate(daily_plan.scheduled_tasks, 1):
                task = scheduled_task.task
                start = scheduled_task.scheduled_time.strftime("%I:%M %p")
                end = scheduled_task.end_time.strftime("%I:%M %p")
                priority_icon = "🔴" if task.priority == 1 else "🟡" if task.priority == 2 else "🟢"

                with st.container():
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.write(f"**{start} - {end}**")
                    with col2:
                        st.write(f"{priority_icon} **{task.description}** ({task.pet_name})")
                        st.caption(f"{task.duration} min • {task.category.value.title()}")

        # Display skipped tasks
        if daily_plan.skipped_tasks:
            st.markdown("#### ⚠️ Skipped Tasks (Not Enough Time)")
            for task in daily_plan.skipped_tasks:
                priority_icon = "🔴" if task.priority == 1 else "🟡" if task.priority == 2 else "🟢"
                st.write(f"{priority_icon} {task.description} ({task.pet_name}) - {task.duration} min")

        # Summary by pet
        st.markdown("#### 🐾 Summary by Pet")
        for pet in owner.pets:
            pet_tasks = daily_plan.get_tasks_by_pet(pet.name)
            total_time = sum(st.task.duration for st in pet_tasks)
            st.write(f"**{pet.name}**: {len(pet_tasks)} tasks, {total_time} minutes")

        # Task completion section
        st.markdown("#### ✅ Mark Tasks as Complete")
        incomplete_scheduled = [st for st in daily_plan.scheduled_tasks if not st.task.is_completed]
        if incomplete_scheduled:
            task_to_complete = st.selectbox(
                "Select a task to mark as complete",
                options=[f"{st.task.description} ({st.task.pet_name})" for st in incomplete_scheduled],
                key="complete_task_selector"
            )

            if st.button("Mark Complete"):
                # Find the task and pet
                selected_task_desc = task_to_complete.split(" (")[0]
                for pet in owner.pets:
                    for task in pet.tasks:
                        if task.description == selected_task_desc and not task.is_completed:
                            next_occurrence = pet.mark_task_complete(task)
                            if next_occurrence:
                                st.success(f"✅ Task completed! Next occurrence scheduled for {next_occurrence.due_time.strftime('%m/%d/%Y %I:%M %p')}")
                            else:
                                st.success(f"✅ Task '{task.description}' marked as complete!")
                            st.rerun()
                            break
        else:
            st.info("All scheduled tasks are complete!")

        # Clear schedule button
        if st.button("Clear Schedule"):
            del st.session_state.daily_plan
            if "scheduler" in st.session_state:
                del st.session_state.scheduler
            st.rerun()

else:
    st.info("Add some pets and tasks to generate a schedule!")

st.divider()

# ============================================================================
# TASK INSIGHTS & SUMMARY
# ============================================================================
if owner.pets and owner.get_all_tasks():
    st.subheader("📊 Task Insights")

    col1, col2, col3 = st.columns(3)

    with col1:
        overdue = owner.get_overdue_tasks()
        st.metric("Overdue Tasks", len(overdue), delta=None if len(overdue) == 0 else f"-{len(overdue)}")

    with col2:
        recurring = owner.get_recurring_tasks()
        st.metric("Recurring Tasks", len(recurring))

    with col3:
        completed = owner.get_tasks_by_status(completed=True)
        st.metric("Completed Tasks", len(completed))

    # Show overdue tasks if any
    if overdue:
        with st.expander("⚠️ View Overdue Tasks", expanded=False):
            for task in overdue:
                hours_overdue = (datetime.now() - task.due_time).total_seconds() / 3600
                st.write(f"🔴 **{task.description}** ({task.pet_name}) - {hours_overdue:.1f} hours overdue")

    # Show recurring tasks if any
    if recurring:
        with st.expander("🔄 View Recurring Tasks", expanded=False):
            for task in recurring:
                end_info = f" until {task.recurrence_end_date.strftime('%m/%d/%Y')}" if task.recurrence_end_date else ""
                st.write(f"**{task.description}** ({task.pet_name}) - {task.recurrence.value}{end_info}")

st.divider()
st.caption("Built with ❤️ using PawPal+ scheduling system")
