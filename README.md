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

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-8.3.4, pluggy-1.5.0
rootdir: .../ai110-module2show-pawpal-starter
collected 6 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 16%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 33%]
tests/test_pawpal.py::test_sort_by_time_orders_chronologically PASSED    [ 50%]
tests/test_pawpal.py::test_filter_by_status_returns_only_matching PASSED [ 66%]
tests/test_pawpal.py::test_detect_conflicts_flags_same_time PASSED       [ 83%]
tests/test_pawpal.py::test_completing_daily_task_creates_next_occurrence PASSED [100%]

============================== 6 passed in 0.01s ===============================
```

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
