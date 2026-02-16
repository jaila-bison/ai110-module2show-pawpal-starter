"""
Demo: Different ways to sort tasks by time using lambda functions
"""

from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, TaskCategory

def demo_basic_time_sorting():
    """Demo 1: Basic time sorting with datetime objects"""
    print("=" * 60)
    print("DEMO 1: Basic Time Sorting (datetime objects)")
    print("=" * 60)

    owner = Owner("Demo Owner", available_time=480)
    dog = Pet("Buddy", "dog")
    owner.add_pet(dog)

    # Create tasks at different times
    tasks = [
        Task("Afternoon walk", 30, 2, datetime.now().replace(hour=14, minute=30), TaskCategory.WALKING),
        Task("Morning feed", 15, 1, datetime.now().replace(hour=8, minute=0), TaskCategory.FEEDING),
        Task("Evening play", 20, 3, datetime.now().replace(hour=18, minute=45), TaskCategory.PLAYTIME),
        Task("Medication", 5, 1, datetime.now().replace(hour=9, minute=15), TaskCategory.MEDICATION),
    ]

    for task in tasks:
        dog.add_task(task)

    # Sort using Owner's method
    sorted_tasks = owner.sort_tasks_by_time(dog.tasks, ascending=True)

    print("\n✅ Tasks sorted by time (earliest → latest):")
    for task in sorted_tasks:
        print(f"  {task.due_time.strftime('%I:%M %p')} - {task.description}")


def demo_string_time_sorting():
    """Demo 2: Sorting "HH:MM" string format"""
    print("\n" + "=" * 60)
    print("DEMO 2: Sorting 'HH:MM' String Times")
    print("=" * 60)

    # Tasks with time as strings
    schedule = [
        {"task": "Lunch break", "time": "12:30"},
        {"task": "Wake up", "time": "07:00"},
        {"task": "Bedtime", "time": "22:00"},
        {"task": "Snack time", "time": "15:45"},
    ]

    # Sort by string time (works because HH:MM is lexicographically sortable)
    sorted_schedule = sorted(schedule, key=lambda item: item["time"])

    print("\n✅ Schedule sorted by time string:")
    for item in sorted_schedule:
        # Convert to 12-hour format for display
        hour, minute = map(int, item["time"].split(":"))
        period = "AM" if hour < 12 else "PM"
        display_hour = hour if hour <= 12 else hour - 12
        display_hour = 12 if display_hour == 0 else display_hour

        print(f"  {display_hour:02d}:{minute:02d} {period} - {item['task']}")


def demo_time_of_day_sorting():
    """Demo 3: Sort by time of day only (ignore date)"""
    print("\n" + "=" * 60)
    print("DEMO 3: Sort by Time of Day (Ignoring Date)")
    print("=" * 60)

    owner = Owner("Demo Owner", available_time=480)
    dog = Pet("Max", "dog")
    owner.add_pet(dog)

    # Tasks on different dates but we only care about time of day
    now = datetime.now()
    tasks = [
        Task("Task A", 30, 1, now + timedelta(days=5, hours=6)),  # 5 days from now, 6am
        Task("Task B", 20, 1, now + timedelta(days=1, hours=12)), # 1 day from now, noon
        Task("Task C", 15, 1, now + timedelta(days=3, hours=8)),  # 3 days from now, 8am
    ]

    for task in tasks:
        dog.add_task(task)

    # Sort by time of day only (hour, minute)
    sorted_by_time_of_day = sorted(
        dog.tasks,
        key=lambda t: (t.due_time.hour, t.due_time.minute)
    )

    print("\n✅ Tasks sorted by time of day (ignoring date):")
    for task in sorted_by_time_of_day:
        print(f"  {task.due_time.strftime('%I:%M %p')} on {task.due_time.strftime('%m/%d/%Y')} - {task.description}")


def demo_multi_key_sorting():
    """Demo 4: Sort by multiple keys (priority, then time)"""
    print("\n" + "=" * 60)
    print("DEMO 4: Multi-Key Sorting (Priority → Time)")
    print("=" * 60)

    owner = Owner("Demo Owner", available_time=480)
    dog = Pet("Charlie", "dog")
    owner.add_pet(dog)

    now = datetime.now()
    tasks = [
        Task("Low priority late", 30, 3, now + timedelta(hours=8), TaskCategory.OTHER),
        Task("High priority early", 15, 1, now + timedelta(hours=2), TaskCategory.FEEDING),
        Task("Medium priority mid", 20, 2, now + timedelta(hours=4), TaskCategory.WALKING),
        Task("High priority late", 25, 1, now + timedelta(hours=6), TaskCategory.MEDICATION),
        Task("Low priority early", 10, 3, now + timedelta(hours=1), TaskCategory.PLAYTIME),
    ]

    for task in tasks:
        dog.add_task(task)

    # Sort by priority first, then by time
    multi_sorted = sorted(
        dog.tasks,
        key=lambda t: (t.priority, t.due_time)
    )

    print("\n✅ Tasks sorted by priority (high→low), then time (early→late):")
    for task in multi_sorted:
        priority_label = "HIGH" if task.priority == 1 else "MED" if task.priority == 2 else "LOW"
        print(f"  [{priority_label}] {task.due_time.strftime('%I:%M %p')} - {task.description}")


def demo_urgency_sorting():
    """Demo 5: Sort by urgency (time until due)"""
    print("\n" + "=" * 60)
    print("DEMO 5: Sort by Urgency (Time Until Due)")
    print("=" * 60)

    owner = Owner("Demo Owner", available_time=480)
    dog = Pet("Luna", "dog")
    owner.add_pet(dog)

    now = datetime.now()
    tasks = [
        Task("Due in 5 hours", 30, 2, now + timedelta(hours=5), TaskCategory.OTHER),
        Task("Due in 30 minutes", 15, 2, now + timedelta(minutes=30), TaskCategory.FEEDING),
        Task("Due in 2 hours", 20, 2, now + timedelta(hours=2), TaskCategory.WALKING),
        Task("Due tomorrow", 25, 2, now + timedelta(days=1), TaskCategory.GROOMING),
    ]

    for task in tasks:
        dog.add_task(task)

    # Sort by time remaining (most urgent first)
    sorted_by_urgency = sorted(
        dog.tasks,
        key=lambda t: (t.due_time - now).total_seconds()
    )

    print("\n✅ Tasks sorted by urgency (most urgent → least urgent):")
    for task in sorted_by_urgency:
        time_remaining = (task.due_time - now).total_seconds()
        hours = time_remaining / 3600

        if hours < 1:
            time_str = f"{int(time_remaining / 60)} minutes"
        elif hours < 24:
            time_str = f"{hours:.1f} hours"
        else:
            time_str = f"{hours / 24:.1f} days"

        print(f"  Due in {time_str} - {task.description}")


def demo_custom_comparisons():
    """Demo 6: Custom lambda comparisons"""
    print("\n" + "=" * 60)
    print("DEMO 6: Custom Lambda Comparisons")
    print("=" * 60)

    owner = Owner("Demo Owner", available_time=480)
    dog = Pet("Rocky", "dog")
    owner.add_pet(dog)

    now = datetime.now()
    tasks = [
        Task("Long task, due soon", 120, 2, now + timedelta(hours=3), TaskCategory.GROOMING),
        Task("Short task, due later", 15, 2, now + timedelta(hours=8), TaskCategory.FEEDING),
        Task("Medium task, due mid", 45, 2, now + timedelta(hours=5), TaskCategory.WALKING),
    ]

    for task in tasks:
        dog.add_task(task)

    # Sort by "slack time" (time until due minus task duration)
    # Tasks with less slack should be done first
    sorted_by_slack = sorted(
        dog.tasks,
        key=lambda t: (t.due_time - now).total_seconds() - (t.duration * 60)
    )

    print("\n✅ Tasks sorted by slack time (least slack → most slack):")
    for task in sorted_by_slack:
        time_until_due = (task.due_time - now).total_seconds() / 3600  # hours
        slack = time_until_due - (task.duration / 60)  # hours

        print(f"  Slack: {slack:.1f}h | {task.description} ({task.duration} min, due in {time_until_due:.1f}h)")


if __name__ == "__main__":
    print("\n🕐 Task Time Sorting Demonstrations 🕐\n")

    demo_basic_time_sorting()
    demo_string_time_sorting()
    demo_time_of_day_sorting()
    demo_multi_key_sorting()
    demo_urgency_sorting()
    demo_custom_comparisons()

    print("\n" + "=" * 60)
    print("✅ All sorting demos complete!")
    print("=" * 60 + "\n")
