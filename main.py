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

    # Create Tasks for Buddy (dog)
    now = datetime.now()

    buddy_feed = Task(
        description="Feed Buddy breakfast",
        duration=15,
        priority=1,  # High priority
        due_time=now + timedelta(hours=1),
        category=TaskCategory.FEEDING
    )

    buddy_walk = Task(
        description="Morning walk with Buddy",
        duration=45,
        priority=1,
        due_time=now + timedelta(hours=2),
        category=TaskCategory.WALKING,
        dependencies=["Feed Buddy breakfast"]  # Must feed before walk
    )

    buddy_play = Task(
        description="Playtime with Buddy",
        duration=30,
        priority=2,
        due_time=now + timedelta(hours=4),
        category=TaskCategory.PLAYTIME
    )

    # Create Tasks for Mittens (cat)
    mittens_feed = Task(
        description="Feed Mittens",
        duration=10,
        priority=1,
        due_time=now + timedelta(hours=1, minutes=30),
        category=TaskCategory.FEEDING
    )

    mittens_groom = Task(
        description="Brush Mittens",
        duration=20,
        priority=2,
        due_time=now + timedelta(hours=3),
        category=TaskCategory.GROOMING
    )

    mittens_play = Task(
        description="Interactive play with Mittens",
        duration=25,
        priority=3,
        due_time=now + timedelta(hours=5),
        category=TaskCategory.PLAYTIME
    )

    # Add tasks to pets
    buddy.add_task(buddy_feed)
    buddy.add_task(buddy_walk)
    buddy.add_task(buddy_play)

    mittens.add_task(mittens_feed)
    mittens.add_task(mittens_groom)
    mittens.add_task(mittens_play)

    # Create Scheduler and generate daily plan
    scheduler = Scheduler(owner)
    daily_plan = scheduler.generate_daily_plan(start_time=now)

    # Print Today's Schedule
    print("=" * 60)
    print(f"🐾 TODAY'S SCHEDULE FOR {owner.name.upper()} 🐾")
    print("=" * 60)
    print(f"Available Time: {owner.available_time} minutes ({owner.available_time // 60} hours)")
    print(f"Total Pets: {len(owner.pets)}")
    print(f"Total Tasks: {len(daily_plan.scheduled_tasks)}")
    print(f"Total Duration: {daily_plan.total_duration} minutes\n")

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


if __name__ == "__main__":
    main()
