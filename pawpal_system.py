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


class RecurrenceType(Enum):
    """Types of task recurrence patterns."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


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
    recurrence: RecurrenceType = RecurrenceType.NONE
    recurrence_end_date: Optional[datetime] = None  # When to stop recurring

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

    def generate_next_occurrence(self) -> Optional['Task']:
        """
        Generate the next occurrence of a recurring task.

        Creates a deep copy of the current task and calculates the next due time
        based on the recurrence type using Python's timedelta.

        Algorithm:
        - DAILY: adds 1 day to current due_time
        - WEEKLY: adds 7 days (1 week) to current due_time
        - MONTHLY: adds 30 days (approximation) to current due_time

        Returns:
            Optional[Task]: New task instance with updated due_time, or None if:
                - Task is not recurring (RecurrenceType.NONE)
                - Next occurrence would exceed recurrence_end_date
                - Recurrence type is invalid

        Example:
            >>> task = Task("Feed Buddy", 15, 1, datetime.now(),
            ...             TaskCategory.FEEDING, recurrence=RecurrenceType.DAILY)
            >>> next_task = task.generate_next_occurrence()
            >>> next_task.due_time == task.due_time + timedelta(days=1)
            True
        """
        if self.recurrence == RecurrenceType.NONE:
            return None

        # Calculate next due time based on recurrence type
        if self.recurrence == RecurrenceType.DAILY:
            next_due = self.due_time + timedelta(days=1)
        elif self.recurrence == RecurrenceType.WEEKLY:
            next_due = self.due_time + timedelta(weeks=1)
        elif self.recurrence == RecurrenceType.MONTHLY:
            # Approximate monthly as 30 days
            next_due = self.due_time + timedelta(days=30)
        else:
            return None

        # Check if we've exceeded the recurrence end date
        if self.recurrence_end_date and next_due > self.recurrence_end_date:
            return None

        # Create new task instance with same properties
        from copy import deepcopy
        next_task = deepcopy(self)
        next_task.due_time = next_due
        next_task.is_completed = False
        next_task.completed_at = None

        return next_task

    def is_recurring(self) -> bool:
        """Check if this task is recurring."""
        return self.recurrence != RecurrenceType.NONE


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

    def get_tasks_by_category(self, category: TaskCategory) -> List[Task]:
        """Get all tasks in a specific category."""
        return [task for task in self.tasks if task.category == category]

    def get_tasks_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Task]:
        """Get tasks within a specific date range."""
        return [task for task in self.tasks if start_date <= task.due_time <= end_date]

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """
        Mark a task as complete and generate next occurrence if recurring.
        Returns the next occurrence task if created, None otherwise.
        """
        task.mark_complete()

        # Generate next occurrence for recurring tasks
        if task.is_recurring():
            next_task = task.generate_next_occurrence()
            if next_task:
                self.add_task(next_task)
                return next_task

        return None

    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        category: Optional[TaskCategory] = None,
        overdue_only: bool = False
    ) -> List[Task]:
        """
        Filter this pet's tasks by various criteria.

        Args:
            completed: Filter by completion status (None = all, True = completed, False = pending)
            category: Filter by task category (None = all categories)
            overdue_only: If True, only return overdue tasks

        Returns:
            List of tasks matching the criteria

        Examples:
            # Get all pending tasks
            tasks = pet.filter_tasks(completed=False)

            # Get completed feeding tasks
            tasks = pet.filter_tasks(completed=True, category=TaskCategory.FEEDING)

            # Get overdue tasks
            tasks = pet.filter_tasks(overdue_only=True)
        """
        filtered = self.tasks

        # Filter by completion status
        if completed is not None:
            filtered = [t for t in filtered if t.is_completed == completed]

        # Filter by category
        if category is not None:
            filtered = [t for t in filtered if t.category == category]

        # Filter by overdue status
        if overdue_only:
            filtered = [t for t in filtered if not t.is_completed and t.is_overdue()]

        return filtered


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

    def get_tasks_by_pet(self, pet_name: str) -> List[Task]:
        """Get all tasks for a specific pet by name."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet.tasks
        return []

    def get_tasks_by_status(self, completed: bool = False) -> List[Task]:
        """Get tasks filtered by completion status."""
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks if task.is_completed == completed]

    def get_tasks_by_category(self, category: TaskCategory) -> List[Task]:
        """Get all tasks across all pets in a specific category."""
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks if task.category == category]

    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks across all pets."""
        all_tasks = self.get_all_pending_tasks()
        return [task for task in all_tasks if task.is_overdue()]

    def get_recurring_tasks(self) -> List[Task]:
        """Get all recurring tasks across all pets."""
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks if task.is_recurring()]

    # Sorting methods
    def sort_tasks_by_time(self, tasks: List[Task], ascending: bool = True) -> List[Task]:
        """
        Sort tasks by their due_time (chronologically).

        Args:
            tasks: List of tasks to sort
            ascending: If True, sort earliest first; if False, sort latest first

        Returns:
            New sorted list (original list unchanged)

        Time Complexity: O(n log n)

        Example:
            >>> tasks = owner.get_all_pending_tasks()
            >>> earliest_first = owner.sort_tasks_by_time(tasks, ascending=True)
            >>> latest_first = owner.sort_tasks_by_time(tasks, ascending=False)
        """
        return sorted(tasks, key=lambda t: t.due_time, reverse=not ascending)

    def sort_tasks_by_priority(self, tasks: List[Task], ascending: bool = True) -> List[Task]:
        """
        Sort tasks by priority level (1 = highest priority).

        Args:
            tasks: List of tasks to sort
            ascending: If True, sort highest priority (1) first; if False, lowest first

        Returns:
            New sorted list (original list unchanged)

        Time Complexity: O(n log n)

        Example:
            >>> tasks = owner.get_all_pending_tasks()
            >>> high_priority_first = owner.sort_tasks_by_priority(tasks, ascending=True)
            >>> # Returns tasks with priority 1, then 2, then 3
        """
        return sorted(tasks, key=lambda t: t.priority, reverse=not ascending)

    def sort_tasks_by_duration(self, tasks: List[Task], ascending: bool = True) -> List[Task]:
        """Sort tasks by duration."""
        return sorted(tasks, key=lambda t: t.duration, reverse=not ascending)

    def sort_tasks_by_category(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by category name."""
        return sorted(tasks, key=lambda t: t.category.value)

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
        category: Optional[TaskCategory] = None,
        overdue_only: bool = False
    ) -> List[Task]:
        """
        Flexible task filtering method that can filter by multiple criteria.

        Args:
            pet_name: Filter by specific pet name (None = all pets)
            completed: Filter by completion status (None = all statuses, True = completed, False = pending)
            category: Filter by task category (None = all categories)
            overdue_only: If True, only return overdue tasks (only applies to pending tasks)

        Returns:
            List of tasks matching all specified criteria

        Examples:
            # Get all pending tasks for "Buddy"
            tasks = owner.filter_tasks(pet_name="Buddy", completed=False)

            # Get all completed feeding tasks
            tasks = owner.filter_tasks(completed=True, category=TaskCategory.FEEDING)

            # Get all overdue tasks for "Whiskers"
            tasks = owner.filter_tasks(pet_name="Whiskers", overdue_only=True)

            # Get all tasks (no filters)
            tasks = owner.filter_tasks()
        """
        # Start with all tasks
        filtered_tasks = self.get_all_tasks()

        # Filter by pet name
        if pet_name is not None:
            filtered_tasks = [t for t in filtered_tasks if t.pet_name == pet_name]

        # Filter by completion status
        if completed is not None:
            filtered_tasks = [t for t in filtered_tasks if t.is_completed == completed]

        # Filter by category
        if category is not None:
            filtered_tasks = [t for t in filtered_tasks if t.category == category]

        # Filter by overdue status (only for pending tasks)
        if overdue_only:
            filtered_tasks = [t for t in filtered_tasks if not t.is_completed and t.is_overdue()]

        return filtered_tasks


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


@dataclass
class SchedulingConflict:
    """Represents a scheduling conflict or issue."""
    conflict_type: str  # e.g., "circular_dependency", "time_overlap", "impossible_deadline"
    description: str
    affected_tasks: List[Task] = field(default_factory=list)
    severity: str = "warning"  # "warning", "error"


class Scheduler:
    """The brain of PawPal+ that generates optimized daily care plans."""

    def __init__(self, owner: Owner):
        """Initialize the scheduler with an owner."""
        self.owner: Owner = owner
        self.conflicts: List[SchedulingConflict] = []

    def generate_daily_plan(self, start_time: Optional[datetime] = None, check_conflicts: bool = True) -> DailyPlan:
        """
        Generate an optimized daily plan based on priority and available time.

        Algorithm:
        1. Get all pending tasks
        2. Detect conflicts (optional)
        3. Sort by priority (1 highest), then by due_time
        4. Resolve dependencies
        5. Fit tasks within available_time
        6. Assign time slots
        7. Check for time overlap conflicts
        """
        if start_time is None:
            start_time = datetime.now()

        # Get and sort tasks
        pending_tasks = self.owner.get_all_pending_tasks()

        # Detect conflicts before scheduling
        if check_conflicts:
            conflicts = self.detect_conflicts(pending_tasks, start_time)
            # Store conflicts for UI to display
            self.conflicts = conflicts

        sorted_tasks = self.optimize_by_priority(pending_tasks)

        # Filter by available time
        fitted_tasks, skipped_tasks = self._fit_tasks_to_time(sorted_tasks)

        # Resolve dependencies and assign time slots
        scheduled_tasks = self._assign_time_slots(fitted_tasks, start_time)

        # Check for time overlaps in the generated schedule (lightweight detection)
        if check_conflicts:
            overlap_conflicts = self.detect_schedule_conflicts(scheduled_tasks)
            self.conflicts.extend(overlap_conflicts)

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

    def detect_conflicts(self, tasks: List[Task], start_time: datetime) -> List[SchedulingConflict]:
        """
        Detect various scheduling conflicts before generating the daily plan.

        Performs multiple validation checks to identify potential issues:
        1. Circular dependencies (Task A depends on B, B depends on A)
        2. Impossible deadlines (task duration > time until due)
        3. Insufficient total time (sum of durations > available time)
        4. Duplicate task descriptions (potential user error)

        Args:
            tasks: List of tasks to check for conflicts
            start_time: Scheduled start time for the day

        Returns:
            List[SchedulingConflict]: All detected conflicts with:
                - conflict_type: category of conflict
                - description: human-readable explanation
                - affected_tasks: tasks involved in the conflict
                - severity: "error" (critical) or "warning" (informational)

        Side Effects:
            Sets self.conflicts to the detected conflicts list

        Example:
            >>> scheduler = Scheduler(owner)
            >>> conflicts = scheduler.detect_conflicts(tasks, datetime.now())
            >>> for conflict in conflicts:
            ...     print(f"{conflict.severity}: {conflict.description}")
        """
        conflicts = []

        # Check for circular dependencies
        circular_deps = self._detect_circular_dependencies(tasks)
        if circular_deps:
            conflicts.append(SchedulingConflict(
                conflict_type="circular_dependency",
                description=f"Circular dependency detected: {' -> '.join(circular_deps)}",
                affected_tasks=[t for t in tasks if t.description in circular_deps],
                severity="error"
            ))

        # Check for impossible deadlines
        impossible_deadlines = self._detect_impossible_deadlines(tasks, start_time)
        for task in impossible_deadlines:
            conflicts.append(SchedulingConflict(
                conflict_type="impossible_deadline",
                description=f"Task '{task.description}' cannot be completed before its due time",
                affected_tasks=[task],
                severity="warning"
            ))

        # Check for total time exceeding available time
        total_duration = sum(t.duration for t in tasks)
        if total_duration > self.owner.available_time:
            conflicts.append(SchedulingConflict(
                conflict_type="insufficient_time",
                description=f"Total task duration ({total_duration} min) exceeds available time ({self.owner.available_time} min)",
                affected_tasks=tasks,
                severity="warning"
            ))

        # Check for duplicate task descriptions (potential mistakes)
        duplicates = self._detect_duplicate_tasks(tasks)
        if duplicates:
            conflicts.append(SchedulingConflict(
                conflict_type="duplicate_tasks",
                description=f"Duplicate task descriptions found: {', '.join(duplicates)}",
                affected_tasks=[t for t in tasks if t.description in duplicates],
                severity="warning"
            ))

        self.conflicts = conflicts
        return conflicts

    def _detect_circular_dependencies(self, tasks: List[Task]) -> List[str]:
        """
        Detect circular dependencies in task dependency graph using Depth-First Search.

        A circular dependency occurs when Task A depends on Task B, and Task B
        (directly or indirectly) depends on Task A, creating an unresolvable cycle.

        Algorithm:
        - Build directed graph from task dependencies
        - Perform DFS traversal with recursion stack tracking
        - Detect back edges (revisiting nodes in current path)
        - Return the cycle path when found

        Time Complexity: O(V + E) where V = tasks, E = dependencies
        Space Complexity: O(V) for visited set and recursion stack

        Args:
            tasks: List of tasks to check

        Returns:
            List[str]: Task descriptions forming the cycle (e.g., ["A", "B", "C", "A"])
                       Empty list if no circular dependencies found

        Example:
            >>> # Task A depends on B, B depends on C, C depends on A
            >>> cycle = scheduler._detect_circular_dependencies(tasks)
            >>> cycle  # ['A', 'B', 'C', 'A']
        """
        # Build dependency graph
        graph = {task.description: task.dependencies for task in tasks}

        def has_cycle(node: str, visited: set, rec_stack: set, path: List[str]) -> Optional[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            # Check all dependencies
            if node in graph:
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        cycle = has_cycle(neighbor, visited, rec_stack, path[:])
                        if cycle:
                            return cycle
                    elif neighbor in rec_stack:
                        # Found a cycle
                        cycle_start = path.index(neighbor)
                        return path[cycle_start:] + [neighbor]

            rec_stack.remove(node)
            return None

        visited = set()
        for task in tasks:
            if task.description not in visited:
                cycle = has_cycle(task.description, visited, set(), [])
                if cycle:
                    return cycle

        return []

    def _detect_impossible_deadlines(self, tasks: List[Task], start_time: datetime) -> List[Task]:
        """
        Detect tasks with impossible deadlines (duration exceeds available time).

        Simple validation: for each task, checks if the task duration is greater
        than the time remaining until the deadline.

        Algorithm:
        - For each task: calculate time_until_due = (due_time - start_time) in minutes
        - If task.duration > time_until_due, the deadline is impossible
        - Return list of all tasks with impossible deadlines

        Time Complexity: O(n) where n = number of tasks
        Space Complexity: O(k) where k = number of impossible tasks

        Args:
            tasks: List of tasks to validate
            start_time: Scheduled start time for the day

        Returns:
            List[Task]: Tasks that cannot be completed before their due_time

        Example:
            >>> # Task due in 30 minutes but takes 60 minutes
            >>> task = Task("Long task", 60, 1, datetime.now() + timedelta(minutes=30))
            >>> impossible = scheduler._detect_impossible_deadlines([task], datetime.now())
            >>> len(impossible)  # 1
        """
        impossible = []

        for task in tasks:
            # Calculate time available until deadline (in minutes)
            time_until_due = (task.due_time - start_time).total_seconds() / 60

            # If task duration exceeds available time, it's impossible
            if task.duration > time_until_due:
                impossible.append(task)

        return impossible

    def _detect_duplicate_tasks(self, tasks: List[Task]) -> List[str]:
        """
        Detect tasks with duplicate descriptions (potential user error).

        Finds task descriptions that appear multiple times in the task list,
        which may indicate accidental duplicates or data entry errors.

        Algorithm:
        - Track seen descriptions in a dictionary
        - When a duplicate is found, add to duplicates list (once per description)
        - Return all duplicate descriptions

        Time Complexity: O(n) where n = number of tasks
        Space Complexity: O(n) for seen dictionary

        Args:
            tasks: List of tasks to check

        Returns:
            List[str]: Task descriptions that appear more than once

        Example:
            >>> task1 = Task("Feed Buddy", 15, 1, datetime.now())
            >>> task2 = Task("Feed Buddy", 15, 1, datetime.now())  # Duplicate!
            >>> duplicates = scheduler._detect_duplicate_tasks([task1, task2])
            >>> duplicates  # ['Feed Buddy']
        """
        seen = {}
        duplicates = []

        for task in tasks:
            if task.description in seen:
                if task.description not in duplicates:
                    duplicates.append(task.description)
            else:
                seen[task.description] = task

        return duplicates

    def detect_schedule_conflicts(self, scheduled_tasks: List[ScheduledTask]) -> List[SchedulingConflict]:
        """
        Detect time overlaps between scheduled tasks (lightweight approach).

        Checks all pairs of scheduled tasks to find time conflicts. Returns
        warnings instead of raising exceptions (non-blocking validation).

        Conflict Types:
        - SAME-TIME: Tasks start at exactly the same time
        - TIME OVERLAP: Tasks have overlapping time ranges

        Additional Context:
        - Distinguishes between same-pet conflicts and different-pet conflicts
        - Formats human-readable time ranges for debugging

        Algorithm:
        - Compare all pairs of scheduled tasks (O(n²))
        - For each pair, check if time ranges overlap
        - Time overlap: (start1 < end2) AND (start2 < end1)
        - Create detailed conflict descriptions

        Time Complexity: O(n²) where n = number of scheduled tasks
        Space Complexity: O(k) where k = number of conflicts

        Args:
            scheduled_tasks: List of tasks with assigned time slots

        Returns:
            List[SchedulingConflict]: All detected time conflicts with severity "warning"

        Example:
            >>> # Two tasks scheduled at 9:00 AM
            >>> conflicts = scheduler.detect_schedule_conflicts(daily_plan.scheduled_tasks)
            >>> for c in conflicts:
            ...     print(c.description)  # "⚠️ SAME-TIME CONFLICT: ..."
        """
        conflicts = []

        for i, task1 in enumerate(scheduled_tasks):
            for task2 in scheduled_tasks[i + 1:]:
                # Check if time ranges overlap
                if (task1.scheduled_time < task2.end_time and
                    task2.scheduled_time < task1.end_time):

                    # Determine conflict details
                    same_pet = task1.task.pet_name == task2.task.pet_name
                    pet_info = f"same pet ({task1.task.pet_name})" if same_pet else f"different pets ({task1.task.pet_name} and {task2.task.pet_name})"

                    # Check if they start at exactly the same time
                    exact_overlap = task1.scheduled_time == task2.scheduled_time

                    if exact_overlap:
                        description = (
                            f"⚠️ SAME-TIME CONFLICT: '{task1.task.description}' and '{task2.task.description}' "
                            f"are scheduled at exactly the same time ({task1.scheduled_time.strftime('%I:%M %p')}) "
                            f"for {pet_info}"
                        )
                    else:
                        description = (
                            f"⚠️ TIME OVERLAP: '{task1.task.description}' ({task1.scheduled_time.strftime('%I:%M %p')} - {task1.end_time.strftime('%I:%M %p')}) "
                            f"overlaps with '{task2.task.description}' ({task2.scheduled_time.strftime('%I:%M %p')} - {task2.end_time.strftime('%I:%M %p')}) "
                            f"for {pet_info}"
                        )

                    conflicts.append(SchedulingConflict(
                        conflict_type="time_overlap",
                        description=description,
                        affected_tasks=[task1.task, task2.task],
                        severity="warning"  # Warning, not error - lightweight approach
                    ))

        return conflicts

    def print_conflicts(self, prefix: str = ""):
        """
        Display all detected conflicts in a formatted, user-friendly way.

        Prints warnings to stdout without raising exceptions (lightweight approach).
        Each conflict shows:
        - Severity icon (🔴 for error, 🟡 for warning)
        - Conflict type (e.g., CIRCULAR_DEPENDENCY, TIME_OVERLAP)
        - Human-readable description
        - List of affected tasks

        Args:
            prefix: String to prepend to each output line (useful for indentation)

        Side Effects:
            Prints to stdout if conflicts exist; does nothing if self.conflicts is empty

        Example:
            >>> scheduler.detect_conflicts(tasks, datetime.now())
            >>> scheduler.print_conflicts(prefix="  ")
            # Output:
            #   ⚠️  SCHEDULING CONFLICTS DETECTED ⚠️
            #   ==========================================================
            #   1. 🟡 IMPOSSIBLE_DEADLINE
            #      Task 'Feed Buddy' cannot be completed before its due time
            #      Affected tasks: Feed Buddy
        """
        if not self.conflicts:
            return

        print(f"\n{prefix}⚠️  SCHEDULING CONFLICTS DETECTED ⚠️")
        print(f"{prefix}{'=' * 60}")

        for i, conflict in enumerate(self.conflicts, 1):
            severity_icon = "🔴" if conflict.severity == "error" else "🟡"
            print(f"{prefix}{i}. {severity_icon} {conflict.conflict_type.upper()}")
            print(f"{prefix}   {conflict.description}")
            if conflict.affected_tasks:
                print(f"{prefix}   Affected tasks: {', '.join([t.description for t in conflict.affected_tasks])}")
            print()

        print(f"{prefix}{'=' * 60}\n")
