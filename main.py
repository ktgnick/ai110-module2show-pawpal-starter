"""Manual testing ground for PawPal+.

Builds an owner with two pets and several tasks, then prints the day's plan.
Run: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def build_demo_owner():
    """Create a sample owner with two pets and a mix of tasks."""
    owner = Owner("Jordan", available_minutes=120)

    mochi = Pet("Mochi", species="dog", breed="Shiba Inu")
    mochi.add_task(Task("Morning walk", 30, "high", category="walk", preferred_time="08:00"))
    mochi.add_task(Task("Breakfast", 10, "high", category="feeding", preferred_time="08:45"))
    mochi.add_task(Task("Evening walk", 30, "medium", category="walk", preferred_time="18:00"))

    biscuit = Pet("Biscuit", species="cat", breed="Tabby")
    biscuit.add_task(Task("Feeding", 10, "high", category="feeding", preferred_time="09:00"))
    biscuit.add_task(Task("Litter cleanup", 15, "medium", category="grooming", preferred_time="09:30"))
    biscuit.add_task(Task("Play session", 20, "low", category="enrichment"))

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


def main():
    owner = build_demo_owner()
    plan = Scheduler().schedule_owner(owner)
    print_schedule(owner, plan)


if __name__ == "__main__":
    main()
