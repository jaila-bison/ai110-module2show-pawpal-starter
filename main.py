from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler, TaskCategory


def main():
    # Create an Owner
    owner = Owner(name="Sarah", available_time=360)  # 6 hours available today

    # Create Pets
    buddy = Pet(name="Buddy", species="Golden Retriever")
    mittens = Pet(name="Mittens", species="Cat")

    # Add pets to owner
    owner.add_pet(buddy)
    owner.add_pet(mittens)

    # Create Tasks INTENTIONALLY OUT OF ORDER to demonstrate scheduler's sorting
    now = datetime.now()

    print("\n🔀 ADDING TASKS OUT OF CHRONOLOGICAL ORDER...\n")

    # Task 1: Due in 4 hours (added first, but not soonest!)
    buddy_play = Task(
        description="Playtime with Buddy",
        duration=30,
        priority=2,
        due_time=now + timedelta(hours=4),
        category=TaskCategory.PLAYTIME
    )
    buddy.add_task(buddy_play)
    print(f"✓ Added: {buddy_play.description} (Due: {buddy_play.due_time.strftime('%I:%M %p')})")

    # Task 2: Due in 3 hours
    mittens_groom = Task(
        description="Brush Mittens",
        duration=20,
        priority=2,
        due_time=now + timedelta(hours=3),
        category=TaskCategory.GROOMING
    )
    mittens.add_task(mittens_groom)
    print(f"✓ Added: {mittens_groom.description} (Due: {mittens_groom.due_time.strftime('%I:%M %p')})")

    # Task 3: Due in 1 hour (should be FIRST, but added third!)
    buddy_feed = Task(
        description="Feed Buddy breakfast",
        duration=15,
        priority=1,  # High priority
        due_time=now + timedelta(hours=1),
        category=TaskCategory.FEEDING
    )
    buddy.add_task(buddy_feed)
    print(f"✓ Added: {buddy_feed.description} (Due: {buddy_feed.due_time.strftime('%I:%M %p')})")

    # Task 4: Due in 5 hours (added fourth)
    mittens_play = Task(
        description="Interactive play with Mittens",
        duration=25,
        priority=3,
        due_time=now + timedelta(hours=5),
        category=TaskCategory.PLAYTIME
    )
    mittens.add_task(mittens_play)
    print(f"✓ Added: {mittens_play.description} (Due: {mittens_play.due_time.strftime('%I:%M %p')})")

    # Task 5: Due in 1.5 hours (should be second, but added fifth!)
    mittens_feed = Task(
        description="Feed Mittens",
        duration=10,
        priority=1,
        due_time=now + timedelta(hours=1, minutes=30),
        category=TaskCategory.FEEDING
    )
    mittens.add_task(mittens_feed)
    print(f"✓ Added: {mittens_feed.description} (Due: {mittens_feed.due_time.strftime('%I:%M %p')})")

    # Task 6: Due in 2 hours with dependency
    buddy_walk = Task(
        description="Morning walk with Buddy",
        duration=45,
        priority=1,
        due_time=now + timedelta(hours=2),
        category=TaskCategory.WALKING,
        dependencies=["Feed Buddy breakfast"]  # Must feed before walk
    )
    buddy.add_task(buddy_walk)
    print(f"✓ Added: {buddy_walk.description} (Due: {buddy_walk.due_time.strftime('%I:%M %p')}) [DEPENDS ON: Feed Buddy breakfast]")

    # Task 7 & 8: INTENTIONALLY SCHEDULED AT SAME TIME to test conflict detection
    print("\n⚠️  ADDING CONFLICTING TASKS (same time)...")

    # Task 7: Training for Buddy at 3pm
    buddy_training = Task(
        description="Training session with Buddy",
        duration=30,
        priority=2,
        due_time=now + timedelta(hours=6),  # 6 hours from now
        category=TaskCategory.TRAINING
    )
    buddy.add_task(buddy_training)
    print(f"✓ Added: {buddy_training.description} (Due: {buddy_training.due_time.strftime('%I:%M %p')})")

    # Task 8: Medication for Mittens at EXACTLY THE SAME TIME (3pm)
    mittens_medication = Task(
        description="Give Mittens medication",
        duration=5,
        priority=1,  # Higher priority
        due_time=now + timedelta(hours=6),  # SAME TIME AS BUDDY'S TRAINING!
        category=TaskCategory.MEDICATION
    )
    mittens.add_task(mittens_medication)
    print(f"✓ Added: {mittens_medication.description} (Due: {mittens_medication.due_time.strftime('%I:%M %p')}) ⚠️ CONFLICTS WITH TRAINING!")

    # Demonstrate sorting capabilities
    print("\n" + "=" * 60)
    print("📊 DEMONSTRATING SORTING (Before Scheduling)")
    print("=" * 60)

    all_tasks = owner.get_all_pending_tasks()

    print("\n1️⃣  Tasks as added (out of order):")
    for i, task in enumerate(all_tasks, 1):
        print(f"   {i}. {task.description} (Due: {task.due_time.strftime('%I:%M %p')})")

    print("\n2️⃣  Tasks sorted by time (chronological):")
    sorted_by_time = owner.sort_tasks_by_time(all_tasks, ascending=True)
    for i, task in enumerate(sorted_by_time, 1):
        print(f"   {i}. {task.description} (Due: {task.due_time.strftime('%I:%M %p')})")

    print("\n3️⃣  Tasks sorted by priority (high → low):")
    sorted_by_priority = owner.sort_tasks_by_priority(all_tasks, ascending=True)
    for i, task in enumerate(sorted_by_priority, 1):
        priority_label = "HIGH" if task.priority == 1 else "MED" if task.priority == 2 else "LOW"
        print(f"   {i}. [{priority_label}] {task.description}")

    print("\n4️⃣  Filtered: Only high-priority tasks:")
    high_priority = [t for t in all_tasks if t.priority == 1]
    for i, task in enumerate(high_priority, 1):
        print(f"   {i}. {task.description} ({task.pet_name})")

    print("\n")

    # Create Scheduler and generate daily plan
    scheduler = Scheduler(owner)
    daily_plan = scheduler.generate_daily_plan(start_time=now)

    # Print Today's Schedule
    print("=" * 60)
    print(f"🐾 TODAY'S OPTIMIZED SCHEDULE FOR {owner.name.upper()} 🐾")
    print("=" * 60)
    print("✨ Scheduler automatically sorted and organized out-of-order tasks!")
    print("=" * 60)
    print(f"Available Time: {owner.available_time} minutes ({owner.available_time // 60} hours)")
    print(f"Total Pets: {len(owner.pets)}")
    print(f"Total Tasks: {len(daily_plan.scheduled_tasks)}")
    print(f"Total Duration: {daily_plan.total_duration} minutes")
    print(f"Conflicts Detected: {len(scheduler.conflicts)}")

    # Display conflicts if any (lightweight warning approach)
    if scheduler.conflicts:
        scheduler.print_conflicts()
    else:
        print("\n✅ No scheduling conflicts detected!\n")

    # Display scheduled tasks
    print("SCHEDULED TASKS:")
    print("-" * 60)

    for i, scheduled_task in enumerate(daily_plan.scheduled_tasks, 1):
        task = scheduled_task.task
        start = scheduled_task.scheduled_time.strftime("%I:%M %p")
        end = scheduled_task.end_time.strftime("%I:%M %p")

        # Priority indicator
        priority_icon = "🔴" if task.priority == 1 else "🟡" if task.priority == 2 else "🟢"

        print(f"{i}. [{start} - {end}] {priority_icon}")
        print(f"   Pet: {task.pet_name} | {task.description}")
        print(f"   Duration: {task.duration} min | Category: {task.category.value.title()}")

        if task.dependencies:
            print(f"   Dependencies: {', '.join(task.dependencies)}")
        print()

    # Display skipped tasks if any
    if daily_plan.skipped_tasks:
        print("\n⚠️  SKIPPED TASKS (Not enough time):")
        print("-" * 60)
        for task in daily_plan.skipped_tasks:
            print(f"   • {task.description} ({task.pet_name}) - {task.duration} min")
        print()

    # Summary by pet
    print("\nSUMMARY BY PET:")
    print("-" * 60)
    for pet in owner.pets:
        pet_tasks = daily_plan.get_tasks_by_pet(pet.name)
        total_time = sum(st.task.duration for st in pet_tasks)
        print(f"🐾 {pet.name} ({pet.species}): {len(pet_tasks)} tasks, {total_time} minutes")

    print("\n" + "=" * 60)
    print("✨ Schedule generated successfully! ✨")
    print("=" * 60)
    print("\n💡 KEY FEATURES DEMONSTRATED:")
    print("   ✓ Sorted tasks by priority and time (even when added out of order)")
    print("   ✓ Respected task dependencies")
    print("   ✓ Optimized the final schedule")
    print("   ✓ Detected scheduling conflicts (LIGHTWEIGHT - warns, doesn't crash!)")
    print("   ✓ Identified same-time conflicts for different pets")
    print("\n🎯 The order you add tasks doesn't matter - the scheduler")
    print("   will always create an optimal schedule!")
    print("\n⚠️  CONFLICT DETECTION:")
    if scheduler.conflicts:
        print(f"   Found {len(scheduler.conflicts)} conflict(s) - see warnings above")
        print("   The program continues running despite conflicts (lightweight approach)")
    else:
        print("   No conflicts detected - perfect schedule!")
    print("=" * 60)


if __name__ == "__main__":
    main()
