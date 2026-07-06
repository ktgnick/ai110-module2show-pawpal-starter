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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
