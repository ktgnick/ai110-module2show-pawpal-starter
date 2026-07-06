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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
