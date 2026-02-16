from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Task:
    """Represents a pet care task with priority and scheduling information."""
    description: str
    duration: int  # in minutes
    priority: int  # 1-3, where 1 is highest priority
    due_time: datetime
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def is_overdue(self) -> bool:
        """Check if the task is overdue."""
        pass


class Pet:
    """Represents a pet with associated care tasks."""

    def __init__(self, name: str, species: str):
        self.name: str = name
        self.species: str = species
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        pass

    def get_pending_tasks(self) -> List[Task]:
        """Get all tasks that are not yet completed."""
        pass

    def get_completed_tasks(self) -> List[Task]:
        """Get all tasks that have been completed."""
        pass


class Owner:
    """Represents a pet owner who manages multiple pets."""

    def __init__(self, name: str, available_time: int = 480):
        self.name: str = name
        self.pets: List[Pet] = []
        self.available_time: int = available_time  # in minutes (default 8 hours)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's care."""
        pass

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's care."""
        pass

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks across all pets."""
        pass

    def set_available_time(self, minutes: int) -> None:
        """Set the available time constraint for the day."""
        pass


class Scheduler:
    """The brain of PawPal+ that generates optimized daily care plans."""

    def __init__(self, owner: Owner):
        self.owner: Owner = owner

    def generate_daily_plan(self) -> List[Task]:
        """Generate an optimized daily plan based on priority and available time."""
        pass

    def optimize_by_priority(self) -> List[Task]:
        """Sort tasks by priority (1 = highest, 3 = lowest)."""
        pass

    def calculate_total_duration(self) -> int:
        """Calculate total duration of all pending tasks."""
        pass

    def filter_by_available_time(self) -> List[Task]:
        """Filter tasks to fit within owner's available time."""
        pass
