"""Plan: the scheduler's output. What the UI displays."""


class Plan:
    """A generated daily plan: scheduled tasks, skipped tasks, and reasoning."""

    def __init__(self):
        self.scheduled = []  # list[tuple[str time, Task]]
        self.skipped = []    # list[tuple[Task, str reason]]
        self.total_time = 0  # int, minutes of scheduled work
        self.reasoning = ""  # str, human-readable explanation

    def add_entry(self, time, task):
        """Add a scheduled (time, task) entry. STUB."""
        raise NotImplementedError

    def add_skipped(self, task, reason):
        """Record a task that was left out and why. STUB."""
        raise NotImplementedError

    def explain(self):
        """Return text explaining the plan's choices. STUB."""
        raise NotImplementedError

    def to_display(self):
        """Return a formatted view for the Streamlit UI. STUB."""
        raise NotImplementedError
