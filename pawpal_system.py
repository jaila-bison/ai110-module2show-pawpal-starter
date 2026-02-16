from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum


class TaskCategory(Enum):
    """Categories for different types of pet care tasks."""
    FEEDING = "feeding"
    WALKING = "walking"
    MEDICATION = "medication"
    GROOMING = "grooming"
    PLAYTIME = "playtime"
    TRAINING = "training"
    OTHER = "other"


@dataclass
class Task:
    """Represents a pet care task with priority and scheduling information."""
    description: str
    duration: int  # in minutes
    priority: int  # 1-3, where 1 is highest priority
    due_time: datetime
    category: TaskCategory = TaskCategory.OTHER
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    pet_name: str = ""  # Back-reference to identify which pet this task belongs to
    dependencies: List[str] = field(default_factory=list)  # List of task descriptions that must be done first

    def __post_init__(self):
        """Validate task data after initialization."""
        if not 1 <= self.priority <= 3:
            raise ValueError("Priority must be between 1 and 3")
        if self.duration <= 0:
            raise ValueError("Duration must be positive")

    def mark_complete(self) -> None:
        """Mark this task as completed with timestamp."""
        self.is_completed = True
        self.completed_at = datetime.now()

    def is_overdue(self) -> bool:
        """Check if the task is overdue."""
        return not self.is_completed and datetime.now() > self.due_time

    def has_dependencies_met(self, completed_tasks: List['Task']) -> bool:
        """Check if all dependency tasks have been completed."""
        if not self.dependencies:
            return True
        completed_descriptions = {task.description for task in completed_tasks}
        return all(dep in completed_descriptions for dep in self.dependencies)


@dataclass
class ScheduledTask:
    """A task with an assigned time slot in the daily plan."""
    task: Task
    scheduled_time: datetime
    end_time: datetime

    def __post_init__(self):
        """Calculate end time based on task duration."""
        if self.end_time is None:
            self.end_time = self.scheduled_time + timedelta(minutes=self.task.duration)


class Pet:
    """Represents a pet with associated care tasks."""

    def __init__(self, name: str, species: str):
        """Initialize a new pet with a name and species."""
        self.name: str = name
        self.species: str = species
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        task.pet_name = self.name  # Set back-reference
        self.tasks.append(task)

    def get_pending_tasks(self) -> List[Task]:
        """Get all tasks that are not yet completed."""
        return [task for task in self.tasks if not task.is_completed]

    def get_completed_tasks(self) -> List[Task]:
        """Get all tasks that have been completed."""
        return [task for task in self.tasks if task.is_completed]

    def get_overdue_tasks(self) -> List[Task]:
        """Get all tasks that are overdue."""
        return [task for task in self.tasks if task.is_overdue()]


class Owner:
    """Represents a pet owner who manages multiple pets."""

    def __init__(self, name: str, available_time: int = 480):
        """Initialize a new owner with a name and available time in minutes."""
        self.name: str = name
        self.pets: List[Pet] = []
        self.available_time: int = available_time  # in minutes (default 8 hours)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's care."""
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's care."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_all_pending_tasks(self) -> List[Task]:
        """Get all pending tasks across all pets."""
        pending_tasks = []
        for pet in self.pets:
            pending_tasks.extend(pet.get_pending_tasks())
        return pending_tasks

    def set_available_time(self, minutes: int) -> None:
        """Set the available time constraint for the day."""
        if minutes <= 0:
            raise ValueError("Available time must be positive")
        self.available_time = minutes


@dataclass
class DailyPlan:
    """Represents a complete daily schedule with time slots."""
    scheduled_tasks: List[ScheduledTask]
    total_duration: int
    skipped_tasks: List[Task] = field(default_factory=list)  # Tasks that couldn't fit

    def get_tasks_by_pet(self, pet_name: str) -> List[ScheduledTask]:
        """Get all scheduled tasks for a specific pet."""
        return [st for st in self.scheduled_tasks if st.task.pet_name == pet_name]

    def get_tasks_by_category(self, category: TaskCategory) -> List[ScheduledTask]:
        """Get all scheduled tasks in a specific category."""
        return [st for st in self.scheduled_tasks if st.task.category == category]


class Scheduler:
    """The brain of PawPal+ that generates optimized daily care plans."""

    def __init__(self, owner: Owner):
        """Initialize the scheduler with an owner."""
        self.owner: Owner = owner

    def generate_daily_plan(self, start_time: Optional[datetime] = None) -> DailyPlan:
        """
        Generate an optimized daily plan based on priority and available time.

        Algorithm:
        1. Get all pending tasks
        2. Sort by priority (1 highest), then by due_time
        3. Resolve dependencies
        4. Fit tasks within available_time
        5. Assign time slots
        """
        if start_time is None:
            start_time = datetime.now()

        # Get and sort tasks
        pending_tasks = self.owner.get_all_pending_tasks()
        sorted_tasks = self.optimize_by_priority(pending_tasks)

        # Filter by available time
        fitted_tasks, skipped_tasks = self._fit_tasks_to_time(sorted_tasks)

        # Resolve dependencies and assign time slots
        scheduled_tasks = self._assign_time_slots(fitted_tasks, start_time)

        total_duration = sum(st.task.duration for st in scheduled_tasks)

        return DailyPlan(
            scheduled_tasks=scheduled_tasks,
            total_duration=total_duration,
            skipped_tasks=skipped_tasks
        )

    def optimize_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (1 = highest, 3 = lowest), then by due_time."""
        return sorted(tasks, key=lambda t: (t.priority, t.due_time))

    def calculate_total_duration(self, tasks: List[Task]) -> int:
        """Calculate total duration of given tasks."""
        return sum(task.duration for task in tasks)

    def _fit_tasks_to_time(self, tasks: List[Task]) -> tuple[List[Task], List[Task]]:
        """
        Filter tasks to fit within owner's available time.
        Returns (fitted_tasks, skipped_tasks).
        """
        fitted = []
        skipped = []
        cumulative_time = 0

        for task in tasks:
            if cumulative_time + task.duration <= self.owner.available_time:
                fitted.append(task)
                cumulative_time += task.duration
            else:
                skipped.append(task)

        return fitted, skipped

    def _assign_time_slots(self, tasks: List[Task], start_time: datetime) -> List[ScheduledTask]:
        """
        Assign specific time slots to tasks, respecting dependencies.
        """
        scheduled = []
        completed_tasks = []
        current_time = start_time

        # Create a working list of tasks to schedule
        remaining_tasks = tasks.copy()

        while remaining_tasks:
            # Find next task with met dependencies
            next_task = None
            for task in remaining_tasks:
                if task.has_dependencies_met(completed_tasks):
                    next_task = task
                    break

            # If no task has met dependencies, break to avoid infinite loop
            if next_task is None:
                # Schedule remaining tasks anyway (dependency issue)
                next_task = remaining_tasks[0]

            # Schedule the task
            end_time = current_time + timedelta(minutes=next_task.duration)
            scheduled_task = ScheduledTask(
                task=next_task,
                scheduled_time=current_time,
                end_time=end_time
            )
            scheduled.append(scheduled_task)
            completed_tasks.append(next_task)
            remaining_tasks.remove(next_task)

            # Move to next time slot
            current_time = end_time

        return scheduled

    def get_tasks_by_pet(self, pet: Pet) -> List[Task]:
        """Get all pending tasks for a specific pet."""
        return pet.get_pending_tasks()

    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks across all pets."""
        overdue = []
        for pet in self.owner.pets:
            overdue.extend(pet.get_overdue_tasks())
        return overdue
