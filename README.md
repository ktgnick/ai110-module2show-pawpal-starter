# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

- **Multi-pet management** — one owner, many pets, each with its own task list (`Owner.add_pet`, `Pet.add_task`).
- **Priority scheduling** — tasks planned high → medium → low, shortest-first as tiebreak (`Scheduler.sort_tasks`).
- **Sort by time** — view tasks in chronological order of their preferred time (`Scheduler.sort_by_time`).
- **Filtering** — by completion status or by pet (`Scheduler.filter_by_status`, `Scheduler.filter_by_pet`).
- **Time-budget planning** — fits tasks into the owner's available minutes and reports what didn't fit (`Scheduler.filter_tasks`, `Scheduler.build_plan`).
- **Conflict warnings** — flags tasks competing for the same time slot without crashing (`Scheduler.detect_conflicts`).
- **Daily / weekly recurrence** — completing a recurring task auto-creates its next occurrence via `timedelta` (`Task.next_occurrence`, `Pet.mark_task_complete`).
- **Explainable plans** — every plan reports why tasks were scheduled or skipped (`Plan.explain`).

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output from running `python main.py`:

```
============================================
  Today's Schedule for Jordan
  Time budget: 120 min
============================================
  08:00  Breakfast         10 min  [high]
  09:00  Feeding           10 min  [high]
  09:10  Vet visit         60 min  [high]
  10:10  Litter cleanup    15 min  [medium]
--------------------------------------------
  Total scheduled: 95 min

  Not scheduled:
    - Morning walk: time conflict at 08:00
    - Evening walk: not enough time in the day
============================================

--- Tasks sorted by time ---
  08:00  Morning walk
  08:00  Breakfast
  09:00  Feeding
  09:30  Litter cleanup
  18:00  Evening walk
    --    Vet visit

--- Filter: pending (not completed) ---
  Evening walk
  Morning walk
  Breakfast
  Litter cleanup
  Feeding
  Vet visit

--- Filter: only Mochi's tasks ---
  Evening walk
  Morning walk
  Breakfast

--- Conflict detection ---
  ⚠️ Conflict at 08:00: Morning walk, Breakfast

--- Recurring tasks ---
  Completed 'Morning walk' (daily).
  Task count 3 -> 4; next occurrence due 2026-07-07.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

**What the tests cover:**

- **Task basics** — completion status flips; adding a task grows the pet's list.
- **Sorting** — `sort_by_time` returns chronological order; untimed tasks last; empty list is safe.
- **Filtering** — by completion status; by pet name (incl. unknown pet → empty).
- **Recurrence** — daily task regenerates +1 day, weekly +7 days; one-off tasks don't regenerate.
- **Conflict detection** — flags duplicate times; silent when all times differ.
- **Planning edge cases** — aggregation across pets; a pet with no tasks yields an empty plan; completed and over-budget tasks are skipped with reasons.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-8.3.4, pluggy-1.5.0
rootdir: .../ai110-module2show-pawpal-starter
collected 14 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  7%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 14%]
tests/test_pawpal.py::test_sort_by_time_orders_chronologically PASSED    [ 21%]
tests/test_pawpal.py::test_filter_by_status_returns_only_matching PASSED [ 28%]
tests/test_pawpal.py::test_detect_conflicts_flags_same_time PASSED       [ 35%]
tests/test_pawpal.py::test_completing_daily_task_creates_next_occurrence PASSED [ 42%]
tests/test_pawpal.py::test_completing_weekly_task_advances_seven_days PASSED [ 50%]
tests/test_pawpal.py::test_non_recurring_task_does_not_regenerate PASSED [ 57%]
tests/test_pawpal.py::test_owner_all_tasks_aggregates_across_pets PASSED [ 64%]
tests/test_pawpal.py::test_pet_with_no_tasks_produces_empty_plan PASSED  [ 71%]
tests/test_pawpal.py::test_sort_by_time_on_empty_list PASSED             [ 78%]
tests/test_pawpal.py::test_detect_conflicts_none_when_all_times_differ PASSED [ 85%]
tests/test_pawpal.py::test_filter_by_pet_unknown_name_returns_empty PASSED [ 92%]
tests/test_pawpal.py::test_build_plan_skips_completed_and_over_budget PASSED [100%]

============================== 14 passed in 0.02s ===============================
```

**Confidence level: ★★★★☆ (4/5)**

All 14 tests pass and cover every core behavior plus the main edge cases (empty pets, duplicate times, recurrence intervals, budget overflow). Dropping one star because conflict detection only catches exact time matches — not overlapping durations — and time-of-day placement isn't yet unit-tested. Those are the next tests to add.

## 📐 Smarter Scheduling

All scheduling logic lives in `pawpal_system.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by priority | `Scheduler.sort_tasks()` | High → medium → low (`Task.priority_rank()`), shortest duration as tiebreak |
| Sort by time | `Scheduler.sort_by_time()` | Chronological by `preferred_time` ("HH:MM"); untimed tasks last |
| Filter by status | `Scheduler.filter_by_status()` | Keep only completed / pending tasks |
| Filter by pet | `Scheduler.filter_by_pet()` | Return one named pet's tasks |
| Filter by time budget | `Scheduler.filter_tasks()` | Greedily keep tasks until `available_minutes` runs out |
| Conflict detection | `Scheduler.detect_conflicts()` | Warns on exact same-time clashes; returns messages, never raises |
| Recurring tasks | `Task.next_occurrence()`, `Pet.mark_task_complete()` | Completing a daily/weekly task auto-creates the next occurrence (`timedelta`) |
| Plan assembly | `Scheduler.build_plan()`, `Scheduler.schedule_owner()` | Drop completed → sort → resolve conflicts → filter to budget → assign clock times |

## 📸 Demo Walkthrough

### Main UI features (`app.py`)

- **Owner panel** — set your name and how many minutes you have today.
- **Add a pet** — name, species, breed. Pets persist across reruns via `st.session_state`.
- **Add a task** — pick the pet, then set title, duration, priority, optional time, and category.
- **Pets & tasks view** — tasks shown per pet, sorted by time, with a status filter (All / Pending / Completed) and a **Done** button that completes a task (and auto-creates the next one if it recurs).
- **Conflict banner** — any two tasks at the same time raise a `st.warning` at the top.
- **Today's Schedule** — one button builds the plan, shows it as a table, lists skipped tasks with reasons, and offers a "Why this plan?" explanation.

### Example workflow

1. Enter owner **Jordan**, 120 minutes available.
2. Add pet **Mochi** (dog), then add tasks: *Morning walk* 08:00 (daily), *Breakfast* 08:00, *Evening walk* 18:00.
3. Add pet **Biscuit** (cat) with *Feeding* 09:00 and a weekly *Vet visit*.
4. A conflict warning appears: *Morning walk* and *Breakfast* both want 08:00.
5. Click **Generate schedule** — the planner sorts by priority, drops the lower-priority 08:00 clash, fits the rest into 120 minutes, and explains the result.
6. Click **Done** on *Morning walk* — it's marked complete and tomorrow's occurrence is created automatically.

### Key Scheduler behaviors shown

- Sorting by time and by priority
- Conflict detection with a plain-language warning
- Budget-aware filtering (tasks that don't fit are reported, not dropped silently)
- Daily/weekly recurrence on completion

### Sample CLI output (`python main.py`)

```
============================================
  Today's Schedule for Jordan
  Time budget: 120 min
============================================
  08:00  Breakfast         10 min  [high]
  09:00  Feeding           10 min  [high]
  09:10  Vet visit         60 min  [high]
  10:10  Litter cleanup    15 min  [medium]
--------------------------------------------
  Total scheduled: 95 min

  Not scheduled:
    - Morning walk: time conflict at 08:00
    - Evening walk: not enough time in the day
============================================

--- Tasks sorted by time ---
  08:00  Morning walk
  08:00  Breakfast
  09:00  Feeding
  09:30  Litter cleanup
  18:00  Evening walk
    --    Vet visit

--- Conflict detection ---
  ⚠️ Conflict at 08:00: Morning walk, Breakfast

--- Recurring tasks ---
  Completed 'Morning walk' (daily).
  Task count 3 -> 4; next occurrence due 2026-07-07.
```
