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


def test_completing_weekly_task_advances_seven_days():
    """A weekly task's next occurrence is due seven days later."""
    pet = Pet("Biscuit")
    vet = Task("Vet visit", 60, "high", recurrence="weekly", due_date=date.today())
    pet.add_task(vet)
    upcoming = pet.mark_task_complete(vet)
    assert upcoming.due_date == date.today() + timedelta(days=7)


def test_non_recurring_task_does_not_regenerate():
    """Completing a one-off task adds no new task and returns None."""
    pet = Pet("Mochi")
    task = Task("Nail trim", 15, "low")  # no recurrence
    pet.add_task(task)
    upcoming = pet.mark_task_complete(task)
    assert upcoming is None
    assert len(pet.get_tasks()) == 1


# --- Edge cases ----------------------------------------------------------

def test_owner_all_tasks_aggregates_across_pets():
    """all_tasks() flattens every pet's tasks into one list."""
    owner = Owner("Jordan")
    dog = Pet("Mochi")
    cat = Pet("Biscuit")
    dog.add_task(Task("Walk", 30, "high"))
    cat.add_task(Task("Feeding", 10, "high"))
    cat.add_task(Task("Play", 20, "low"))
    owner.add_pet(dog)
    owner.add_pet(cat)
    assert len(owner.all_tasks()) == 3


def test_pet_with_no_tasks_produces_empty_plan():
    """An owner whose pets have no tasks yields an empty, non-crashing plan."""
    owner = Owner("Jordan", available_minutes=60)
    owner.add_pet(Pet("Mochi"))
    plan = Scheduler().schedule_owner(owner)
    assert plan.scheduled == []
    assert plan.skipped == []
    assert plan.total_time == 0


def test_sort_by_time_on_empty_list():
    """Sorting an empty task list returns an empty list, not an error."""
    assert Scheduler().sort_by_time([]) == []


def test_detect_conflicts_none_when_all_times_differ():
    """No warnings when every task has a distinct time (or no time)."""
    tasks = [
        Task("Walk", 30, "high", preferred_time="08:00"),
        Task("Feeding", 10, "high", preferred_time="09:00"),
        Task("Play", 20, "low"),  # no time -> never conflicts
    ]
    assert Scheduler().detect_conflicts(tasks) == []


def test_filter_by_pet_unknown_name_returns_empty():
    """Filtering by a pet that doesn't exist returns an empty list."""
    owner = Owner("Jordan")
    owner.add_pet(Pet("Mochi"))
    assert Scheduler().filter_by_pet(owner, "Ghost") == []


def test_build_plan_skips_completed_and_over_budget():
    """Completed tasks and tasks past the time budget land in skipped."""
    tasks = [
        Task("Walk", 30, "high"),
        Task("Long training", 45, "medium"),  # 30+45 > 60 budget
        Task("Grooming", 20, "medium", completed=True),
    ]
    plan = Scheduler().build_plan(tasks, budget=60)
    scheduled_names = [t.name for _, t in plan.scheduled]
    skipped = {t.name: reason for t, reason in plan.skipped}
    assert scheduled_names == ["Walk"]
    assert skipped["Grooming"] == "already completed"
    assert "not enough time" in skipped["Long training"]
