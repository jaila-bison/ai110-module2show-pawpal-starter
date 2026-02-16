"""
Test and demonstrate task filtering methods
- Filter by completion status
- Filter by pet name
- Filter by category
- Filter by multiple criteria
- Filter overdue tasks
"""

from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, TaskCategory

def setup_test_data():
    """Create test data with multiple pets and various tasks"""
    owner = Owner("Test Owner", available_time=480)

    # Create pets
    dog = Pet("Buddy", "dog")
    cat = Pet("Whiskers", "cat")
    bird = Pet("Tweety", "bird")

    owner.add_pet(dog)
    owner.add_pet(cat)
    owner.add_pet(bird)

    # Current time for reference
    now = datetime.now()

    # Add tasks for dog (mix of pending and completed)
    dog_tasks = [
        Task("Morning walk", 30, 1, now + timedelta(hours=1), TaskCategory.WALKING),
        Task("Feed Buddy", 15, 1, now + timedelta(hours=2), TaskCategory.FEEDING),
        Task("Play fetch", 20, 2, now - timedelta(hours=1), TaskCategory.PLAYTIME),  # Overdue!
        Task("Groom Buddy", 45, 3, now + timedelta(days=1), TaskCategory.GROOMING),
    ]
    for task in dog_tasks:
        dog.add_task(task)

    # Mark some dog tasks as completed
    dog.tasks[1].mark_complete()  # Feed Buddy - completed

    # Add tasks for cat (mix of pending and completed)
    cat_tasks = [
        Task("Feed Whiskers", 10, 1, now + timedelta(hours=1), TaskCategory.FEEDING),
        Task("Clean litter box", 15, 1, now - timedelta(hours=2), TaskCategory.OTHER),  # Overdue!
        Task("Cat medication", 5, 1, now + timedelta(hours=3), TaskCategory.MEDICATION),
        Task("Brush cat", 20, 2, now + timedelta(days=2), TaskCategory.GROOMING),
    ]
    for task in cat_tasks:
        cat.add_task(task)

    # Mark some cat tasks as completed
    cat.tasks[0].mark_complete()  # Feed Whiskers - completed
    cat.tasks[2].mark_complete()  # Cat medication - completed

    # Add tasks for bird
    bird_tasks = [
        Task("Clean cage", 25, 1, now + timedelta(hours=4), TaskCategory.OTHER),
        Task("Feed Tweety", 5, 1, now + timedelta(hours=1), TaskCategory.FEEDING),
    ]
    for task in bird_tasks:
        bird.add_task(task)

    return owner


def test_filter_by_completion_status():
    """Test filtering by completion status"""
    print("=" * 70)
    print("TEST 1: Filter by Completion Status")
    print("=" * 70)

    owner = setup_test_data()

    # Get all completed tasks
    completed_tasks = owner.filter_tasks(completed=True)
    print(f"\n✅ Completed tasks ({len(completed_tasks)} total):")
    for task in completed_tasks:
        print(f"  - {task.description} ({task.pet_name})")

    # Get all pending tasks
    pending_tasks = owner.filter_tasks(completed=False)
    print(f"\n⏳ Pending tasks ({len(pending_tasks)} total):")
    for task in pending_tasks:
        print(f"  - {task.description} ({task.pet_name})")


def test_filter_by_pet_name():
    """Test filtering by pet name"""
    print("\n" + "=" * 70)
    print("TEST 2: Filter by Pet Name")
    print("=" * 70)

    owner = setup_test_data()

    # Get all tasks for Buddy
    buddy_tasks = owner.filter_tasks(pet_name="Buddy")
    print(f"\n🐕 Buddy's tasks ({len(buddy_tasks)} total):")
    for task in buddy_tasks:
        status = "✅" if task.is_completed else "⏳"
        print(f"  {status} {task.description} - {task.category.value}")

    # Get all tasks for Whiskers
    whiskers_tasks = owner.filter_tasks(pet_name="Whiskers")
    print(f"\n🐈 Whiskers' tasks ({len(whiskers_tasks)} total):")
    for task in whiskers_tasks:
        status = "✅" if task.is_completed else "⏳"
        print(f"  {status} {task.description} - {task.category.value}")


def test_filter_by_category():
    """Test filtering by task category"""
    print("\n" + "=" * 70)
    print("TEST 3: Filter by Category")
    print("=" * 70)

    owner = setup_test_data()

    # Get all feeding tasks
    feeding_tasks = owner.filter_tasks(category=TaskCategory.FEEDING)
    print(f"\n🍽️  Feeding tasks ({len(feeding_tasks)} total):")
    for task in feeding_tasks:
        status = "✅" if task.is_completed else "⏳"
        print(f"  {status} {task.description} ({task.pet_name})")

    # Get all grooming tasks
    grooming_tasks = owner.filter_tasks(category=TaskCategory.GROOMING)
    print(f"\n✂️  Grooming tasks ({len(grooming_tasks)} total):")
    for task in grooming_tasks:
        status = "✅" if task.is_completed else "⏳"
        print(f"  {status} {task.description} ({task.pet_name})")


def test_filter_by_multiple_criteria():
    """Test filtering by multiple criteria at once"""
    print("\n" + "=" * 70)
    print("TEST 4: Filter by Multiple Criteria")
    print("=" * 70)

    owner = setup_test_data()

    # Get pending tasks for Buddy
    buddy_pending = owner.filter_tasks(pet_name="Buddy", completed=False)
    print(f"\n🐕 Buddy's pending tasks ({len(buddy_pending)} total):")
    for task in buddy_pending:
        print(f"  ⏳ {task.description} - {task.category.value}")

    # Get completed feeding tasks across all pets
    completed_feeding = owner.filter_tasks(
        completed=True,
        category=TaskCategory.FEEDING
    )
    print(f"\n🍽️  Completed feeding tasks ({len(completed_feeding)} total):")
    for task in completed_feeding:
        print(f"  ✅ {task.description} ({task.pet_name})")

    # Get pending grooming tasks for Whiskers
    whiskers_pending_grooming = owner.filter_tasks(
        pet_name="Whiskers",
        completed=False,
        category=TaskCategory.GROOMING
    )
    print(f"\n✂️  Whiskers' pending grooming tasks ({len(whiskers_pending_grooming)} total):")
    for task in whiskers_pending_grooming:
        print(f"  ⏳ {task.description}")


def test_filter_overdue_tasks():
    """Test filtering overdue tasks"""
    print("\n" + "=" * 70)
    print("TEST 5: Filter Overdue Tasks")
    print("=" * 70)

    owner = setup_test_data()

    # Get all overdue tasks
    overdue_tasks = owner.filter_tasks(overdue_only=True)
    print(f"\n⚠️  Overdue tasks ({len(overdue_tasks)} total):")
    for task in overdue_tasks:
        hours_overdue = (datetime.now() - task.due_time).total_seconds() / 3600
        print(f"  🔴 {task.description} ({task.pet_name}) - {hours_overdue:.1f} hours overdue")

    # Get overdue tasks for specific pet
    buddy_overdue = owner.filter_tasks(pet_name="Buddy", overdue_only=True)
    print(f"\n⚠️  Buddy's overdue tasks ({len(buddy_overdue)} total):")
    for task in buddy_overdue:
        hours_overdue = (datetime.now() - task.due_time).total_seconds() / 3600
        print(f"  🔴 {task.description} - {hours_overdue:.1f} hours overdue")


def test_pet_level_filtering():
    """Test filtering at the Pet level"""
    print("\n" + "=" * 70)
    print("TEST 6: Pet-Level Filtering")
    print("=" * 70)

    owner = setup_test_data()
    buddy = owner.pets[0]  # Buddy the dog

    # Get Buddy's pending tasks
    buddy_pending = buddy.filter_tasks(completed=False)
    print(f"\n🐕 Buddy's pending tasks ({len(buddy_pending)} total):")
    for task in buddy_pending:
        print(f"  ⏳ {task.description} - {task.category.value}")

    # Get Buddy's completed tasks
    buddy_completed = buddy.filter_tasks(completed=True)
    print(f"\n🐕 Buddy's completed tasks ({len(buddy_completed)} total):")
    for task in buddy_completed:
        print(f"  ✅ {task.description} - {task.category.value}")

    # Get Buddy's feeding tasks
    buddy_feeding = buddy.filter_tasks(category=TaskCategory.FEEDING)
    print(f"\n🐕 Buddy's feeding tasks ({len(buddy_feeding)} total):")
    for task in buddy_feeding:
        status = "✅" if task.is_completed else "⏳"
        print(f"  {status} {task.description}")


def test_comparison_old_vs_new_methods():
    """Compare old filtering methods vs new flexible method"""
    print("\n" + "=" * 70)
    print("TEST 7: Old Methods vs New filter_tasks() Method")
    print("=" * 70)

    owner = setup_test_data()

    print("\n📊 Comparison of filtering approaches:")

    # Old way - using existing methods
    print("\n1️⃣  OLD WAY (using separate methods):")
    print("   owner.get_tasks_by_pet('Buddy')")
    old_buddy = owner.get_tasks_by_pet("Buddy")
    print(f"   Result: {len(old_buddy)} tasks")

    print("\n   owner.get_tasks_by_status(completed=False)")
    old_pending = owner.get_tasks_by_status(completed=False)
    print(f"   Result: {len(old_pending)} tasks")

    # New way - using flexible filter_tasks
    print("\n2️⃣  NEW WAY (using filter_tasks):")
    print("   owner.filter_tasks(pet_name='Buddy')")
    new_buddy = owner.filter_tasks(pet_name="Buddy")
    print(f"   Result: {len(new_buddy)} tasks")

    print("\n   owner.filter_tasks(completed=False)")
    new_pending = owner.filter_tasks(completed=False)
    print(f"   Result: {len(new_pending)} tasks")

    # New capability - combine filters
    print("\n3️⃣  NEW CAPABILITY (combined filters):")
    print("   owner.filter_tasks(pet_name='Buddy', completed=False)")
    buddy_pending = owner.filter_tasks(pet_name="Buddy", completed=False)
    print(f"   Result: {len(buddy_pending)} tasks")
    for task in buddy_pending:
        print(f"     - {task.description}")


def test_practical_use_cases():
    """Demonstrate practical use cases"""
    print("\n" + "=" * 70)
    print("TEST 8: Practical Use Cases")
    print("=" * 70)

    owner = setup_test_data()

    # Use case 1: What needs to be done for Buddy today?
    print("\n📋 Use Case 1: What needs to be done for Buddy today?")
    buddy_pending = owner.filter_tasks(pet_name="Buddy", completed=False)
    print(f"   {len(buddy_pending)} pending tasks:")
    for task in buddy_pending:
        overdue = "⚠️ OVERDUE" if task.is_overdue() else ""
        print(f"     - {task.description} {overdue}")

    # Use case 2: Which tasks are overdue and need immediate attention?
    print("\n⚠️  Use Case 2: Which tasks are overdue and need immediate attention?")
    overdue = owner.filter_tasks(overdue_only=True)
    print(f"   {len(overdue)} overdue tasks:")
    for task in overdue:
        hours = (datetime.now() - task.due_time).total_seconds() / 3600
        print(f"     - {task.description} ({task.pet_name}) - {hours:.1f}h overdue")

    # Use case 3: What feeding tasks have been completed today?
    print("\n✅ Use Case 3: What feeding tasks have been completed?")
    completed_feeding = owner.filter_tasks(
        completed=True,
        category=TaskCategory.FEEDING
    )
    print(f"   {len(completed_feeding)} completed feeding tasks:")
    for task in completed_feeding:
        print(f"     - {task.description} ({task.pet_name})")

    # Use case 4: What grooming tasks are pending for all pets?
    print("\n✂️  Use Case 4: What grooming tasks are pending for all pets?")
    pending_grooming = owner.filter_tasks(
        completed=False,
        category=TaskCategory.GROOMING
    )
    print(f"   {len(pending_grooming)} pending grooming tasks:")
    for task in pending_grooming:
        print(f"     - {task.description} ({task.pet_name})")


if __name__ == "__main__":
    print("\n🔍 Task Filtering Methods Test Suite 🔍\n")

    test_filter_by_completion_status()
    test_filter_by_pet_name()
    test_filter_by_category()
    test_filter_by_multiple_criteria()
    test_filter_overdue_tasks()
    test_pet_level_filtering()
    test_comparison_old_vs_new_methods()
    test_practical_use_cases()

    print("\n" + "=" * 70)
    print("✅ All filtering tests completed!")
    print("=" * 70 + "\n")
