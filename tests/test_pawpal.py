import pytest
from datetime import datetime, timedelta
from pawpal_system import Task, Pet, TaskCategory


class TestTaskCompletion:
    """Test suite for Task completion functionality."""

    def test_mark_complete_changes_status(self):
        """Verify that calling mark_complete() changes the task's status."""
        # Arrange: Create a task that is not completed
        task = Task(
            description="Feed the dog",
            duration=15,
            priority=1,
            due_time=datetime.now() + timedelta(hours=2),
            category=TaskCategory.FEEDING
        )

        # Verify initial state
        assert task.is_completed is False
        assert task.completed_at is None

        # Act: Mark the task as complete
        task.mark_complete()

        # Assert: Verify the status changed
        assert task.is_completed is True
        assert task.completed_at is not None
        assert isinstance(task.completed_at, datetime)

    def test_mark_complete_sets_timestamp(self):
        """Verify that mark_complete() sets a valid timestamp."""
        # Arrange
        task = Task(
            description="Walk the dog",
            duration=30,
            priority=2,
            due_time=datetime.now() + timedelta(hours=1)
        )
        before_completion = datetime.now()

        # Act
        task.mark_complete()
        after_completion = datetime.now()

        # Assert: The completion time should be between before and after
        assert before_completion <= task.completed_at <= after_completion

    def test_mark_complete_multiple_times(self):
        """Verify that calling mark_complete() multiple times doesn't cause errors."""
        # Arrange
        task = Task(
            description="Grooming session",
            duration=45,
            priority=3,
            due_time=datetime.now() + timedelta(hours=3),
            category=TaskCategory.GROOMING
        )

        # Act: Mark complete multiple times
        task.mark_complete()
        first_completion_time = task.completed_at

        # Wait a tiny bit and mark complete again
        task.mark_complete()
        second_completion_time = task.completed_at

        # Assert: Should still be completed and timestamp should be updated
        assert task.is_completed is True
        assert second_completion_time >= first_completion_time


class TestTaskAddition:
    """Test suite for adding tasks to pets."""

    def test_add_task_increases_task_count(self):
        """Verify that adding a task to a Pet increases that pet's task count."""
        # Arrange: Create a pet with no tasks
        pet = Pet(name="Buddy", species="Dog")
        initial_task_count = len(pet.tasks)

        task = Task(
            description="Feed Buddy",
            duration=10,
            priority=1,
            due_time=datetime.now() + timedelta(hours=1),
            category=TaskCategory.FEEDING
        )

        # Act: Add the task to the pet
        pet.add_task(task)

        # Assert: Task count should increase by 1
        assert len(pet.tasks) == initial_task_count + 1
        assert len(pet.tasks) == 1

    def test_add_multiple_tasks(self):
        """Verify that adding multiple tasks increases the count correctly."""
        # Arrange
        pet = Pet(name="Whiskers", species="Cat")

        task1 = Task(
            description="Feed Whiskers",
            duration=10,
            priority=1,
            due_time=datetime.now() + timedelta(hours=1)
        )
        task2 = Task(
            description="Clean litter box",
            duration=15,
            priority=2,
            due_time=datetime.now() + timedelta(hours=2)
        )
        task3 = Task(
            description="Playtime with Whiskers",
            duration=20,
            priority=3,
            due_time=datetime.now() + timedelta(hours=3),
            category=TaskCategory.PLAYTIME
        )

        # Act: Add multiple tasks
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)

        # Assert: Task count should be 3
        assert len(pet.tasks) == 3

    def test_add_task_sets_pet_name(self):
        """Verify that adding a task sets the back-reference to the pet's name."""
        # Arrange
        pet = Pet(name="Max", species="Dog")
        task = Task(
            description="Walk Max",
            duration=30,
            priority=1,
            due_time=datetime.now() + timedelta(hours=1),
            category=TaskCategory.WALKING
        )

        # Verify task initially has no pet_name
        assert task.pet_name == ""

        # Act
        pet.add_task(task)

        # Assert: The task should now have the pet's name
        assert task.pet_name == "Max"

    def test_add_task_actually_in_list(self):
        """Verify that the added task is actually in the pet's task list."""
        # Arrange
        pet = Pet(name="Luna", species="Cat")
        task = Task(
            description="Give Luna medication",
            duration=5,
            priority=1,
            due_time=datetime.now() + timedelta(hours=1),
            category=TaskCategory.MEDICATION
        )

        # Act
        pet.add_task(task)

        # Assert: The task should be in the pet's task list
        assert task in pet.tasks
        assert pet.tasks[0] == task
        assert pet.tasks[0].description == "Give Luna medication"
