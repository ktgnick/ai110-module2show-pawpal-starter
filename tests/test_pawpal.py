"""Core behavior tests for PawPal+."""

from datetime import date, timedelta

from pawpal_system import Task, Pet, Owner, Scheduler


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


def test_sort_by_time_orders_chronologically():
    """sort_by_time puts earlier times first and untimed tasks last."""
    tasks = [
        Task("Evening", 30, "low", preferred_time="18:00"),
        Task("Anytime", 10, "low"),
        Task("Morning", 30, "high", preferred_time="08:00"),
    ]
    ordered = [t.name for t in Scheduler().sort_by_time(tasks)]
    assert ordered == ["Morning", "Evening", "Anytime"]


def test_filter_by_status_returns_only_matching():
    """filter_by_status splits pending from completed tasks."""
    done = Task("Fed", 10, "high", completed=True)
    pending = Task("Walk", 30, "high")
    result = Scheduler().filter_by_status([done, pending], completed=False)
    assert result == [pending]


def test_detect_conflicts_flags_same_time():
    """detect_conflicts returns a warning when two tasks share a time slot."""
    tasks = [
        Task("Walk", 30, "high", preferred_time="08:00"),
        Task("Breakfast", 10, "high", preferred_time="08:00"),
    ]
    warnings = Scheduler().detect_conflicts(tasks)
    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_completing_daily_task_creates_next_occurrence():
    """Marking a daily task complete auto-adds a copy due one day later."""
    pet = Pet("Mochi")
    walk = Task("Walk", 30, "high", recurrence="daily", due_date=date.today())
    pet.add_task(walk)
    upcoming = pet.mark_task_complete(walk)
    assert walk.completed is True
    assert len(pet.get_tasks()) == 2
    assert upcoming.completed is False
    assert upcoming.due_date == date.today() + timedelta(days=1)
