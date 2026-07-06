"""Core behavior tests for PawPal+."""

from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    """Calling mark_complete() flips a task from not-done to done."""
    task = Task("Morning walk", 30, "high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet grows its task list by one."""
    pet = Pet("Mochi", species="dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Feeding", 10, "high"))
    assert len(pet.get_tasks()) == 1
