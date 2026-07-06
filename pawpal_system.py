"""PawPal+ core system: pet care task modeling and scheduling.

Single-module version of the UML design. Classes:
    Task      - one unit of pet care work
    Pet       - one animal and its tasks
    Owner     - the owner, their pets, preferences, and daily time budget
    Plan      - the scheduler's output (what the UI displays)
    Scheduler - the planning engine that turns tasks + budget into a Plan
"""

# Rank map so the scheduler can order tasks by priority deterministically.
# Higher number = more important.
PRIORITY_ORDER = {"low": 0, "medium": 1, "high": 2}

# Default clock the scheduler starts placing tasks at when none is preferred.
DAY_START = "08:00"


def _parse_time(hhmm):
    """'HH:MM' -> minutes since midnight (int)."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def _format_time(total_minutes):
    """minutes since midnight (int) -> 'HH:MM'."""
    total_minutes %= 24 * 60
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


class Task:
    """A single pet care task (walk, feeding, meds, enrichment, grooming...)."""

    def __init__(
        self,
        name,
        duration,
        priority,
        category=None,
        recurrence=None,
        preferred_time=None,
        completed=False,
    ):
        """
        name: str, description of the activity, e.g. "Morning walk"
        duration: int, minutes the task takes
        priority: str, one of "low" | "medium" | "high"
        category: str or None, e.g. "walk" | "feeding" | "meds"
        recurrence: str or None, frequency e.g. "daily" | "weekly"
        preferred_time: str or None, 'HH:MM' the owner wants it at
        completed: bool, whether the task is already done today
        """
        self.name = name
        self.duration = duration
        self.priority = priority
        self.category = category
        self.recurrence = recurrence
        self.preferred_time = preferred_time
        self.completed = completed

    def is_high_priority(self):
        """Return True if this task is high priority."""
        return self.priority == "high"

    def priority_rank(self):
        """Return int rank for sorting; unknown priorities rank lowest."""
        return PRIORITY_ORDER.get(self.priority, 0)

    def mark_complete(self):
        """Mark this task complete."""
        self.completed = True

    # Alias kept for readability at call sites.
    mark_done = mark_complete

    def reset(self):
        """Mark this task not complete (e.g. new day)."""
        self.completed = False

    def __repr__(self):
        return (
            f"Task(name={self.name!r}, duration={self.duration}, "
            f"priority={self.priority!r}, completed={self.completed})"
        )


class Pet:
    """A pet owned by an Owner. Holds its own list of Tasks."""

    def __init__(self, name, species=None, breed=None):
        """
        name: str
        species: str or None, e.g. "dog" | "cat"
        breed: str or None
        """
        self.name = name
        self.species = species
        self.breed = breed
        self.tasks = []  # list[Task]

    def add_task(self, task):
        """Attach a Task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task):
        """Detach a Task from this pet. No error if it isn't present."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self):
        """Return this pet's tasks."""
        return self.tasks


class Owner:
    """A pet owner. Holds pets, preferences, and available time for the day."""

    def __init__(self, name, available_minutes=0, preferences=None):
        """
        name: str
        available_minutes: int, total time budget for today's plan
        preferences: dict or None, e.g. {"no_meds_after": "20:00"}
        """
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences if preferences is not None else {}
        self.pets = []  # list[Pet]

    def add_pet(self, pet):
        """Attach a Pet to this owner."""
        self.pets.append(pet)

    def set_available_time(self, minutes):
        """Set the daily time budget in minutes."""
        self.available_minutes = minutes

    def set_preference(self, key, value):
        """Set a single preference."""
        self.preferences[key] = value

    def all_tasks(self):
        """Return every task across all pets as one flat list for the Scheduler."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks


class Plan:
    """A generated daily plan: scheduled tasks, skipped tasks, and reasoning."""

    def __init__(self):
        self.scheduled = []  # list[tuple[str time, Task]]
        self.skipped = []    # list[tuple[Task, str reason]]
        self.total_time = 0  # int, minutes of scheduled work

    def add_entry(self, time, task):
        """Add a scheduled (time, task) entry and accrue its duration."""
        self.scheduled.append((time, task))
        self.total_time += task.duration

    def add_skipped(self, task, reason):
        """Record a task that was left out and why."""
        self.skipped.append((task, reason))

    def explain(self):
        """Return text explaining the plan's choices."""
        lines = []
        if self.scheduled:
            lines.append(
                f"Scheduled {len(self.scheduled)} task(s) using {self.total_time} min, "
                "ordered by priority then shortest duration."
            )
            for time, task in self.scheduled:
                lines.append(f"  {time} — {task.name} ({task.duration} min) [{task.priority}]")
        else:
            lines.append("No tasks scheduled.")
        if self.skipped:
            lines.append(f"Skipped {len(self.skipped)} task(s):")
            for task, reason in self.skipped:
                lines.append(f"  {task.name} — {reason}")
        return "\n".join(lines)

    def to_display(self):
        """Return a list of row dicts for the Streamlit UI table."""
        return [
            {
                "time": time,
                "task": task.name,
                "duration_minutes": task.duration,
                "priority": task.priority,
            }
            for time, task in self.scheduled
        ]


class Scheduler:
    """Sorts, filters, and orders tasks into a daily Plan given a time budget.

    Stateless: the time budget lives on the Owner and is passed into build_plan,
    so the Scheduler holds no duplicate copy of it.
    """

    def sort_tasks(self, tasks):
        """Return tasks ordered by priority (high first), then shortest duration.

        Shortest-first within a priority lets more tasks fit under a tight budget.
        """
        return sorted(tasks, key=lambda t: (-t.priority_rank(), t.duration))

    def filter_tasks(self, tasks, budget):
        """Greedily keep tasks (in given order) whose running total fits budget.

        Returns (kept, dropped). Later tasks that don't fit are dropped even if
        an earlier long task was skipped — order is assumed pre-sorted by caller.
        """
        kept, dropped = [], []
        used = 0
        for task in tasks:
            if used + task.duration <= budget:
                kept.append(task)
                used += task.duration
            else:
                dropped.append(task)
        return kept, dropped

    def resolve_conflicts(self, tasks):
        """Drop lower-priority tasks that want a preferred_time already claimed.

        Assumes `tasks` is already sorted best-first, so the first task to claim
        a slot wins. Returns (kept, dropped).
        """
        kept, dropped = [], []
        claimed = set()
        for task in tasks:
            slot = task.preferred_time
            if slot is not None and slot in claimed:
                dropped.append(task)
            else:
                if slot is not None:
                    claimed.add(slot)
                kept.append(task)
        return kept, dropped

    def build_plan(self, tasks, budget):
        """Produce a Plan from tasks and a time budget.

        Pipeline: drop completed -> sort -> resolve time conflicts ->
        filter to budget -> assign clock times.
        """
        plan = Plan()

        active = []
        for task in tasks:
            if task.completed:
                plan.add_skipped(task, "already completed")
            else:
                active.append(task)

        ordered = self.sort_tasks(active)

        deconflicted, conflicts = self.resolve_conflicts(ordered)
        for task in conflicts:
            plan.add_skipped(task, f"time conflict at {task.preferred_time}")

        kept, over_budget = self.filter_tasks(deconflicted, budget)
        for task in over_budget:
            plan.add_skipped(task, "not enough time in the day")

        clock = _parse_time(DAY_START)
        for task in kept:
            if task.preferred_time is not None:
                start = _parse_time(task.preferred_time)
                if start < clock:
                    start = clock  # preferred slot already passed; place next free
            else:
                start = clock
            plan.add_entry(_format_time(start), task)
            clock = start + task.duration

        return plan

    def schedule_owner(self, owner):
        """Bridge: pull every task across the owner's pets and plan the day.

        Uses the owner's available_minutes as the budget.
        """
        return self.build_plan(owner.all_tasks(), owner.available_minutes)
