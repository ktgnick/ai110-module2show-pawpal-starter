"""Manual testing ground for PawPal+.

Builds an owner with two pets and several tasks, then exercises the
scheduling, sorting, filtering, recurring, and conflict-detection logic.
Run: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def build_demo_owner():
    """Create a sample owner with two pets and tasks added out of time order."""
    owner = Owner("Jordan", available_minutes=120)

    mochi = Pet("Mochi", species="dog", breed="Shiba Inu")
    # Deliberately out of chronological order to exercise sort_by_time().
    mochi.add_task(Task("Evening walk", 30, "medium", category="walk", preferred_time="18:00"))
    mochi.add_task(Task("Morning walk", 30, "high", category="walk", preferred_time="08:00", recurrence="daily"))
    mochi.add_task(Task("Breakfast", 10, "high", category="feeding", preferred_time="08:00"))  # conflict w/ walk

    biscuit = Pet("Biscuit", species="cat", breed="Tabby")
    biscuit.add_task(Task("Litter cleanup", 15, "medium", category="grooming", preferred_time="09:30"))
    biscuit.add_task(Task("Feeding", 10, "high", category="feeding", preferred_time="09:00"))
    biscuit.add_task(Task("Vet visit", 60, "high", category="meds", recurrence="weekly"))

    owner.add_pet(mochi)
    owner.add_pet(biscuit)
    return owner


def print_schedule(owner, plan):
    """Pretty-print the plan as a readable terminal schedule."""
    print("=" * 44)
    print(f"  Today's Schedule for {owner.name}")
    print(f"  Time budget: {owner.available_minutes} min")
    print("=" * 44)
    if plan.scheduled:
        for time, task in plan.scheduled:
            print(f"  {time}  {task.name:<16} {task.duration:>3} min  [{task.priority}]")
    else:
        print("  (nothing scheduled)")
    print("-" * 44)
    print(f"  Total scheduled: {plan.total_time} min")
    if plan.skipped:
        print("\n  Not scheduled:")
        for task, reason in plan.skipped:
            print(f"    - {task.name}: {reason}")
    print("=" * 44)


def demo_sorting_and_filtering(owner, scheduler):
    """Show sort_by_time plus status/pet filtering in the terminal."""
    all_tasks = owner.all_tasks()

    print("\n--- Tasks sorted by time ---")
    for task in scheduler.sort_by_time(all_tasks):
        when = task.preferred_time or "  --  "
        print(f"  {when}  {task.name}")

    print("\n--- Filter: pending (not completed) ---")
    for task in scheduler.filter_by_status(all_tasks, completed=False):
        print(f"  {task.name}")

    print("\n--- Filter: only Mochi's tasks ---")
    for task in scheduler.filter_by_pet(owner, "Mochi"):
        print(f"  {task.name}")


def demo_conflicts(owner, scheduler):
    """Show lightweight conflict detection."""
    print("\n--- Conflict detection ---")
    warnings = scheduler.detect_conflicts(owner.all_tasks())
    if warnings:
        for w in warnings:
            print(f"  {w}")
    else:
        print("  No time conflicts.")


def demo_recurring(owner):
    """Complete a recurring task and show the next occurrence auto-appears."""
    print("\n--- Recurring tasks ---")
    mochi = owner.pets[0]
    walk = next(t for t in mochi.get_tasks() if t.name == "Morning walk")
    before = len(mochi.get_tasks())
    upcoming = mochi.mark_task_complete(walk)
    after = len(mochi.get_tasks())
    print(f"  Completed '{walk.name}' ({walk.recurrence}).")
    print(f"  Task count {before} -> {after}; next occurrence due {upcoming.due_date}.")


def main():
    owner = build_demo_owner()
    scheduler = Scheduler()

    plan = scheduler.schedule_owner(owner)
    print_schedule(owner, plan)

    demo_sorting_and_filtering(owner, scheduler)
    demo_conflicts(owner, scheduler)
    demo_recurring(owner)


if __name__ == "__main__":
    main()
