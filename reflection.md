# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial design is for an app that helps a busy owner keep up with pet care. The three main actions are adding a pet, adding or editing care tasks with a duration and priority, and generating a daily plan based on the owner's available time and task priorities.

I would use four classes:

- **Owner:** Stores basic owner information, available time, and care preferences. An owner has pets.
- **Pet:** Stores basic pet information and keeps track of that pet's care tasks. Each pet belongs to an owner.
- **Task:** Represents a care activity, like feeding or walking, with a name, duration in minutes, and priority. Each task is for a pet.
- **Scheduler:** Uses the owner's available time and the pet's tasks to make a daily plan. It considers higher-priority tasks first, chooses tasks that fit in the time available, and explains its choices.

In my UML design, Owner would connect to Pet, and Pet would connect to Task. Scheduler would use information from these classes to build the plan.

**b. Design changes**

After reviewing the design with AI, I decided to keep the original four classes: Owner, Pet, Task, and Scheduler. Each class has a clear responsibility, so I kept the UML and Python skeleton unchanged.

The review helped me identify a few improvements to make during implementation. I plan to validate task inputs, keep each task associated with its pet, define a consistent format for the scheduler output, and set clear rules for task priorities and time limits. These are planned improvements and have not been implemented yet.

I chose not to add extra classes or complex appointment scheduling because I want to keep the project manageable within the four-hour time frame.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

I chose to keep conflict detection simple. The scheduler groups pending tasks by their date and exact starting time, including tasks for different pets, and returns a warning when a group has more than one task. It uses each task's due date when available, otherwise the planning date, which defaults to today. It ignores completed tasks and tasks without a scheduled time. It only reports conflicts; it does not change tasks or the generated plan.

The tradeoff is that it detects identical starting times on the same date but does not detect overlapping intervals with different starting times. For example, tasks scheduled for 09:00–09:30 and 09:15–09:45 would not trigger a warning. I chose this approach for a short assignment because the dictionary grouping is easy to understand and test, while full overlap detection would need more logic and edge cases. I kept the explicit dictionary version because a shorter version would not improve what it detects.

Later, I could combine each task's date and starting time, add its duration to calculate an ending time, and check whether two intervals overlap. I would add tests for partial overlaps, one task inside another, and tasks that cross midnight. Tasks that start exactly when another ends would not count as overlapping.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI to brainstorm the four classes, draft the UML, create the Python skeleton, and help implement the logic. AI suggested validating task inputs, keeping tasks connected to their pets, and using a consistent format for the daily plan. I accepted these ideas. Asking how the Scheduler should get tasks from all of the owner's pets was especially helpful. The implementation now uses Owner.get_all_tasks() to return pet and task pairs.

**b. Judgment and verification**

After the AI review, I chose to keep the four-class design and leave out extra classes and complex appointment scheduling. I wanted the project to stay manageable. I also refined the original idea of returning only tasks: returning each task with its pet makes the schedule easier to understand when multiple pets have similar tasks.

To verify the result, the AI assistant ran python main.py and python -m pytest. The demo printed tasks for two pets, stayed within a 40-minute budget, and explained why grooming was skipped. All 19 tests passed, including task completion, adding a task, and a check that Scheduler gets tasks through Owner.get_all_tasks(). These results support the logic we tested, but the Streamlit UI still needs to be connected.

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
