"""Task: one unit of pet care work. Core object the scheduler sorts and filters."""


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
    ):
        """
        name: str, e.g. "Morning walk"
        duration: int, minutes the task takes
        priority: str, one of "low" | "medium" | "high"
        category: str or None, e.g. "walk" | "feeding" | "meds"
        recurrence: str or None, e.g. "daily" | "weekly"
        preferred_time: str or None, e.g. "08:00"
        """
        self.name = name
        self.duration = duration
        self.priority = priority
        self.category = category
        self.recurrence = recurrence
        self.preferred_time = preferred_time

    def is_high_priority(self):
        """Return True if this task is high priority. STUB."""
        raise NotImplementedError

    def __repr__(self):
        return f"Task(name={self.name!r}, duration={self.duration}, priority={self.priority!r})"
