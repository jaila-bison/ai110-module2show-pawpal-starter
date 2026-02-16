"""
Test script for new scheduling features:
- Task sorting by time, priority, duration, category
- Filtering by pet, status, category
- Recurring task support
- Conflict detection
"""

from datetime import datetime, timedelta
from pawpal_system import (
    Owner, Pet, Task, TaskCategory, Scheduler, RecurrenceType
)


def test_sorting_and_filtering():
    """Test sorting and filtering functionality."""
    print("=" * 60)
    print("TEST 1: Sorting and Filtering")
    print("=" * 60)

    # Setup
    owner = Owner(name="Test Owner", available_time=480)
    dog = Pet(name="Buddy", species="dog")
    cat = Pet(name="Whiskers", species="cat")
    owner.add_pet(dog)
    owner.add_pet(cat)

    # Add various tasks
    task1 = Task(
        description="Feed Buddy",
        duration=15,
        priority=1,
        due_time=datetime.now() + timedelta(hours=2),
        category=TaskCategory.FEEDING
    )
    task2 = Task(
        description="Walk Buddy",
        duration=30,
        priority=2,
        due_time=datetime.now() + timedelta(hours=1),
        category=TaskCategory.WALKING
    )
    task3 = Task(
        description="Feed Whiskers",
        duration=10,
        priority=1,
        due_time=datetime.now() + timedelta(hours=3),
        category=TaskCategory.FEEDING
    )

    dog.add_task(task1)
    dog.add_task(task2)
    cat.add_task(task3)

    # Test sorting by time
    all_tasks = owner.get_all_pending_tasks()
    sorted_by_time = owner.sort_tasks_by_time(all_tasks)
    print("\n✅ Tasks sorted by time:")
    for task in sorted_by_time:
        print(f"  - {task.description} (Due: {task.due_time.strftime('%I:%M %p')})")

    # Test sorting by priority
    sorted_by_priority = owner.sort_tasks_by_priority(all_tasks)
    print("\n✅ Tasks sorted by priority:")
    for task in sorted_by_priority:
        print(f"  - {task.description} (Priority: {task.priority})")

    # Test filtering by pet
    buddy_tasks = owner.get_tasks_by_pet("Buddy")
    print(f"\n✅ Buddy's tasks: {len(buddy_tasks)} tasks")
    for task in buddy_tasks:
        print(f"  - {task.description}")

    # Test filtering by category
    feeding_tasks = owner.get_tasks_by_category(TaskCategory.FEEDING)
    print(f"\n✅ Feeding tasks: {len(feeding_tasks)} tasks")
    for task in feeding_tasks:
        print(f"  - {task.description} ({task.pet_name})")


def test_recurring_tasks():
    """Test recurring task functionality."""
    print("\n" + "=" * 60)
    print("TEST 2: Recurring Tasks")
    print("=" * 60)

    owner = Owner(name="Test Owner", available_time=480)
    dog = Pet(name="Max", species="dog")
    owner.add_pet(dog)

    # Create a daily recurring task
    recurring_task = Task(
        description="Daily Walk",
        duration=30,
        priority=1,
        due_time=datetime.now() + timedelta(hours=1),
        category=TaskCategory.WALKING,
        recurrence=RecurrenceType.DAILY,
        recurrence_end_date=datetime.now() + timedelta(days=7)
    )

    dog.add_task(recurring_task)

    print(f"\n✅ Created recurring task: {recurring_task.description}")
    print(f"   Recurrence: {recurring_task.recurrence.value}")
    print(f"   Due: {recurring_task.due_time.strftime('%m/%d/%Y %I:%M %p')}")

    # Mark complete and generate next occurrence
    next_occurrence = dog.mark_task_complete(recurring_task)

    if next_occurrence:
        print(f"\n✅ Task marked complete - Next occurrence generated:")
        print(f"   Due: {next_occurrence.due_time.strftime('%m/%d/%Y %I:%M %p')}")
        print(f"   Time difference: {(next_occurrence.due_time - recurring_task.due_time).days} day(s)")
    else:
        print("\n❌ No next occurrence generated")


def test_conflict_detection():
    """Test conflict detection functionality."""
    print("\n" + "=" * 60)
    print("TEST 3: Conflict Detection")
    print("=" * 60)

    owner = Owner(name="Test Owner", available_time=60)  # Only 1 hour available
    dog = Pet(name="Charlie", species="dog")
    owner.add_pet(dog)

    # Create tasks that will cause conflicts

    # 1. Circular dependency
    task1 = Task(
        description="Task A",
        duration=20,
        priority=1,
        due_time=datetime.now() + timedelta(hours=2),
        category=TaskCategory.OTHER,
        dependencies=["Task B"]
    )
    task2 = Task(
        description="Task B",
        duration=20,
        priority=1,
        due_time=datetime.now() + timedelta(hours=2),
        category=TaskCategory.OTHER,
        dependencies=["Task A"]  # Circular dependency!
    )

    # 2. Impossible deadline (task due before it can be completed)
    task3 = Task(
        description="Urgent Task",
        duration=120,  # 2 hours
        priority=1,
        due_time=datetime.now() + timedelta(minutes=30),  # Due in 30 minutes!
        category=TaskCategory.OTHER
    )

    # 3. Duplicate task
    task4 = Task(
        description="Feed Dog",
        duration=15,
        priority=1,
        due_time=datetime.now() + timedelta(hours=1),
        category=TaskCategory.FEEDING
    )
    task5 = Task(
        description="Feed Dog",  # Duplicate!
        duration=15,
        priority=1,
        due_time=datetime.now() + timedelta(hours=2),
        category=TaskCategory.FEEDING
    )

    dog.add_task(task1)
    dog.add_task(task2)
    dog.add_task(task3)
    dog.add_task(task4)
    dog.add_task(task5)

    # Run conflict detection
    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts(
        owner.get_all_pending_tasks(),
        datetime.now()
    )

    print(f"\n✅ Detected {len(conflicts)} conflict(s):")
    for i, conflict in enumerate(conflicts, 1):
        print(f"\n{i}. {conflict.conflict_type.upper()} ({conflict.severity})")
        print(f"   Description: {conflict.description}")
        if conflict.affected_tasks:
            print(f"   Affected tasks: {', '.join([t.description for t in conflict.affected_tasks])}")


def test_full_workflow():
    """Test complete workflow with all features."""
    print("\n" + "=" * 60)
    print("TEST 4: Full Workflow Integration")
    print("=" * 60)

    owner = Owner(name="Pet Owner", available_time=300)  # 5 hours
    dog = Pet(name="Rover", species="dog")
    cat = Pet(name="Mittens", species="cat")
    owner.add_pet(dog)
    owner.add_pet(cat)

    # Add mix of regular and recurring tasks
    tasks = [
        Task("Morning Walk", 30, 1, datetime.now() + timedelta(hours=1),
             TaskCategory.WALKING, recurrence=RecurrenceType.DAILY),
        Task("Feed Rover", 15, 1, datetime.now() + timedelta(minutes=30),
             TaskCategory.FEEDING, recurrence=RecurrenceType.DAILY),
        Task("Feed Mittens", 10, 1, datetime.now() + timedelta(minutes=30),
             TaskCategory.FEEDING, recurrence=RecurrenceType.DAILY),
        Task("Grooming", 45, 2, datetime.now() + timedelta(hours=3),
             TaskCategory.GROOMING),
        Task("Playtime", 20, 2, datetime.now() + timedelta(hours=2),
             TaskCategory.PLAYTIME),
    ]

    for i, task in enumerate(tasks[:3]):
        dog.add_task(task)
    for task in tasks[3:]:
        cat.add_task(task)

    print(f"\n✅ Created {len(tasks)} tasks")
    print(f"   Recurring: {len([t for t in tasks if t.is_recurring()])}")
    print(f"   Regular: {len([t for t in tasks if not t.is_recurring()])}")

    # Generate schedule with conflict detection
    scheduler = Scheduler(owner)
    daily_plan = scheduler.generate_daily_plan(
        start_time=datetime.now(),
        check_conflicts=True
    )

    print(f"\n✅ Schedule generated:")
    print(f"   Scheduled: {len(daily_plan.scheduled_tasks)} tasks")
    print(f"   Skipped: {len(daily_plan.skipped_tasks)} tasks")
    print(f"   Total duration: {daily_plan.total_duration} minutes")
    print(f"   Conflicts detected: {len(scheduler.conflicts)}")

    if scheduler.conflicts:
        print("\n⚠️  Conflicts:")
        for conflict in scheduler.conflicts:
            print(f"   - {conflict.conflict_type}: {conflict.description}")


if __name__ == "__main__":
    print("\n🐾 PawPal+ New Features Test Suite 🐾\n")

    test_sorting_and_filtering()
    test_recurring_tasks()
    test_conflict_detection()
    test_full_workflow()

    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60 + "\n")
