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

Smarter Scheduling

PawPal+ now includes advanced scheduling features that make pet care planning more intelligent and flexible:

Recurring Tasks
- **Auto-generation**: Daily, weekly, and monthly recurring tasks automatically create the next occurrence when marked complete
- **End dates**: Optional recurrence end dates to stop generating future tasks
- **Algorithm**: Uses Python's `timedelta` for accurate date calculations

Flexible Filtering
- **Multi-criteria**: Filter tasks by pet name, completion status, category, or overdue status
- **Combine filters**: Get specific results like "Buddy's pending feeding tasks" in a single call
- **O(n) complexity**: Fast filtering even with many tasks

 Conflict Detection
PawPal+ validates your schedule and warns about potential issues:
- **Circular dependencies**: Detects impossible dependency chains using DFS (O(V+E))
- **Impossible deadlines**: Finds tasks that can't finish before their due time (O(n))
- **Time overlaps**: Identifies tasks scheduled at the same time (distinguishes same-pet vs different-pet conflicts)
- **Lightweight approach**: Returns warnings instead of crashing, so your schedule still generates

Smart Sorting
Sort tasks by multiple criteria:
- **By time**: Chronological order (earliest or latest first)
- **By priority**: High to low priority (1 = highest)
- **By duration**: Shortest or longest tasks first
- **By category**: Grouped by task type (feeding, walking, grooming, etc.)

Efficient Algorithm
- **Greedy scheduling**: O(n log n) performance trades perfect optimization for speed and simplicity
- **Good-enough results**: Finds a practical schedule quickly without solving NP-hard optimization problems
- **Predictable**: Users can understand why tasks are ordered (priority first, then due time)



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
