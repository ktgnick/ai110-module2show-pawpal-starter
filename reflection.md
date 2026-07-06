# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

A PawPal+ user should be able to:

1. **Add a pet and its care tasks** — enter owner and pet info, then add care tasks (walks, feeding, meds, enrichment, grooming) with a duration and a priority for each.
2. **Generate a daily plan** — tell PawPal+ how much time is available today and have it produce a schedule that fits the tasks into that time by priority.
3. **View today's plan and why** — see the ordered daily schedule clearly, with an explanation of why tasks were included, dropped, or ordered the way they were.

**a. Initial design**

My initial UML had five classes, each with one clear responsibility:

- **Owner** — the pet owner. Holds their pets, preferences (e.g. no meds after 8pm), and the daily time budget. Responsible for owning-side data, not scheduling logic.
- **Pet** — one animal. Holds its own list of care tasks and can add/remove/return them.
- **Task** — one unit of care work (walk, feeding, meds…). Holds name, duration, priority, category, recurrence, and preferred time. This is the object the scheduler sorts and filters.
- **Scheduler** — the planning engine. Sorts tasks by priority, filters them to fit the time budget, resolves time conflicts, and builds a Plan. Kept separate from Owner/Pet so the logic is testable on its own.
- **Plan** — the scheduler's output. Holds the ordered scheduled tasks, the skipped tasks (with reasons), total time, and a reasoning string for the UI.

Relationships: Owner *has* many Pets, each Pet *has* many Tasks; Scheduler *reads* Tasks and *produces* a Plan that *references* the chosen Tasks.

**b. Design changes**

After the skeleton, I asked my AI assistant to review it for missing relationships and logic bottlenecks. Three issues led to changes:

1. **Missing Pet→Scheduler bridge.** Tasks lived on each `Pet`, but the `Scheduler` expected one flat list of tasks. Nothing collected all of an owner's tasks. I added `Owner.all_tasks()` to gather every pet's tasks into a single list the scheduler can consume.
2. **Duplicated time budget.** Both `Owner.available_minutes` and `Scheduler.time_budget` stored the day's budget — ambiguous which was authoritative. I removed `Scheduler.time_budget` and made the Scheduler stateless; the budget now lives only on `Owner` and is passed into `build_plan(tasks, budget)`.
3. **Priority couldn't be sorted.** Priority was a free string (`"low"/"medium"/"high"`), which the scheduler can't order directly. I added a `PRIORITY_ORDER` rank map and a `Task.priority_rank()` method so sorting is deterministic.

I did *not* act on one suggestion — converting `preferred_time` from a string to a real time object. For a draft skeleton that adds parsing complexity before it's needed, so I left it as a string and noted it as a bottleneck to revisit if conflict-resolution logic needs real time math.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints, applied in this order:

1. **Completion status** — already-completed tasks are dropped before planning.
2. **Priority** — tasks sort high → medium → low (via `PRIORITY_ORDER` / `Task.priority_rank()`), with shortest-duration first as a tiebreak so more tasks fit.
3. **Time budget** — `Owner.available_minutes` caps the day; `filter_tasks()` greedily keeps tasks until the budget runs out.

Time conflicts (two tasks wanting the same `preferred_time`) are resolved on top of this. Priority mattered most because the scenario is a *busy* owner: when time is short, the important tasks (meds, walks) must survive over nice-to-haves (enrichment).

**b. Tradeoffs**

My conflict detection only checks for **exact `preferred_time` matches**, not overlapping durations. Two tasks both at `08:00` are flagged, but a 30-minute task at `08:00` and another at `08:15` are *not* — even though they truly overlap.

This is a reasonable tradeoff for the scenario: comparing exact start-time strings is simple, fast, and easy to reason about, and most owners enter round times ("08:00", "09:00") anyway. Full interval-overlap detection would need real time math (parse start, add duration, compare ranges) for a small accuracy gain. I noted it as the first thing to improve if the app graduated from a daily planner to a minute-accurate calendar.

A second tradeoff: within one priority level, `sort_tasks` favors **shorter** tasks so more fit under a tight budget. The cost is that a long high-priority anchor (e.g. a 30-min walk) can lose its slot to a shorter same-priority task — visible in the demo where "Breakfast" claimed 08:00 over "Morning walk".

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant across every phase but in different modes:

- **Design brainstorming** — listing candidate classes and their attributes/methods, then reviewing the skeleton for missing relationships and bottlenecks.
- **Implementation** — agent/edit mode to flesh out the class bodies and generate the Streamlit wiring.
- **Algorithm help** — targeted chat questions like "how do I sort 'HH:MM' strings with a lambda key?" and "how do I use timedelta for the next occurrence?".
- **Testing** — drafting the pytest cases and enumerating edge cases (empty pet, duplicate times).

The most helpful prompts were **specific and scoped** — naming the method and the exact behavior ("sort Task objects by their time attribute") — rather than broad ones ("write my scheduler"). Narrow questions gave answers I could actually verify.

**b. Judgment and verification**

I rejected the suggestion to convert `preferred_time` from a string to a `datetime.time` object during the skeleton phase. It was technically cleaner but added parsing complexity before any logic needed it; I kept the zero-padded "HH:MM" string, which sorts chronologically as-is. I also kept my readable `detect_conflicts` loop instead of a denser one-liner the assistant offered, because clarity mattered more than compactness for a method I'd have to defend.

I verified AI output three ways: running `main.py` to watch real behavior, running `pytest` after every change, and reading the generated code line by line before saving — which is how I caught that the exact-time conflict check misses overlapping durations.

---

## 4. Testing and Verification

**a. What you tested**

The suite (`tests/test_pawpal.py`, 14 tests) covers: task completion, adding tasks to a pet, chronological sorting (incl. empty list), status/pet filtering (incl. unknown pet), conflict detection (present and absent), recurrence (daily +1, weekly +7, non-recurring → None), owner-level task aggregation, and planning edge cases (empty pet, over-budget, completed skipped).

These mattered because they are the behaviors a user actually depends on — the schedule is only trustworthy if sorting, budget filtering, and recurrence are correct, and the edge cases are exactly where a naive implementation crashes or silently drops data.

**b. Confidence**

I'm confident (★★★★☆) the core scheduler works: all 14 tests pass and cover the happy paths plus the obvious edge cases. My remaining doubt is the parts *not* yet unit-tested — the clock-time placement in `build_plan` and overlapping-duration conflicts. Next I'd test: tasks whose `preferred_time` has already passed, back-to-back durations that overlap, and a budget of exactly zero.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the clean separation of concerns: `Owner`/`Pet`/`Task` hold data, `Scheduler` holds the logic, and `Plan` holds the result. That split made the logic easy to unit-test in isolation and easy to wire into Streamlit without tangling UI code with scheduling rules.

**b. What you would improve**

I'd replace exact-time conflict detection with real interval-overlap logic and give `build_plan` smarter time placement (respecting `preferred_time` windows instead of a single sequential clock). I'd also add persistence so pets and tasks survive a full app restart, not just reruns.

**c. Key takeaway — AI strategy and being lead architect**

- **Most effective AI features:** scoped chat questions for algorithms (sorting keys, `timedelta`) and agent/edit mode for mechanical fan-out (fleshing out stubs, wiring the UI). Inline review of the skeleton caught design gaps early.
- **A suggestion I modified:** I declined the `datetime.time` conversion for `preferred_time` and kept the simpler "HH:MM" string, and I kept my readable conflict loop over a denser one-liner — small choices that kept the design clean.
- **Separate chat sessions per phase** kept the context focused: a planning chat didn't drag along implementation details, and a testing chat stayed on edge cases. Less noise meant more relevant answers and fewer accidental rewrites of working code.
- **Lead architect takeaway:** the AI is fast at producing plausible code, but *plausible isn't correct*. My job was to own the design decisions, keep the constraints straight (priority > budget > conflict), verify every suggestion by running it, and reject anything that added complexity without earning it. The most important skill wasn't prompting — it was judgment about what to keep.
