# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
     This UML class diagram shows a pet management and scheduling system. At the start is the Owner, who manages multiple Pets and has a specific amount of available time. Each Pet is associated with a list of Tasks, which are defined as data classes containing details like description, duration, priority, and completion status. . A Scheduler class acts as a coordinator, holding a reference to an Owner to "schedule for" them; it also has a dependency on Tasks, as it "optimizes" them by calculating total durations and filtering activities based on the owner's available time and task priority.
- What classes did you include, and what 
responsibilities did you assign to each?
    For the initial design, I chose four main classes: Pet, Task, Owner, and Scheduler. The Pet and Task classes (using Python Dataclasses) act as the primary data models, storing essential information like care requirements, priorities, and durations. The Owner class serves as the central hub that manages multiple pet profiles, while the Scheduler acts as the logic engine that processes the owner's available time and task priorities to generate an optimized daily plan


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Added TaskCategory enum and ScheduledTask/DailyPlan classes to structure the scheduler output with actual time slots. Enhanced Task with pet back-references (pet_name), dependencies, completion timestamps, and validation. Implemented complete Scheduler algorithm that sorts by priority, respects dependencies, fits tasks within available time, and returns a structured plan with skipped tasks. Added helper methods across all classes for filtering overdue/pending tasks and preventing data integrity issues.

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
