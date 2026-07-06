"""Scheduler: the planning engine. Turns tasks + a time budget into a Plan."""


class Scheduler:
    """Sorts, filters, and orders tasks into a daily Plan given a time budget."""

    def __init__(self, time_budget=0):
        """time_budget: int, minutes available for the day."""
        self.time_budget = time_budget

    def sort_tasks(self, tasks):
        """Return tasks ordered by priority, then duration. STUB."""
        raise NotImplementedError

    def filter_tasks(self, tasks, budget):
        """Return tasks that fit within budget; drop the rest. STUB."""
        raise NotImplementedError

    def resolve_conflicts(self, tasks):
        """Handle overlapping preferred time slots. STUB."""
        raise NotImplementedError

    def build_plan(self, tasks, budget):
        """Produce a Plan from tasks and a time budget. STUB."""
        raise NotImplementedError
