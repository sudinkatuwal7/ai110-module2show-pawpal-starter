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
