# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial design was an app that helps a busy owner keep up with pet care. I started with adding pets, managing care tasks, and generating a daily plan based on available time and task priorities. I kept four classes because each one answers a different question about the same problem.

Their responsibilities are:

- **Owner:** Stores the owner's name, time budget, short-task preference, and pets. It collects tasks across pets.
- **Pet:** Stores pet information and manages its task list, including completion and adding the next recurring occurrence.
- **Task:** Stores and validates the details of one care activity, including duration, priority, recurrence, scheduled time, due date, and completion date.
- **Scheduler:** Builds the daily plan, sorts and filters task lists, and reports same-time conflicts.

Owner manages pets, Pet contains tasks, and Scheduler uses their information. None of these classes needs to inherit from another. Keeping the Streamlit interface in app.py also lets me test the care logic without opening the app.

**b. Design changes**

The four-class structure stayed, but the details grew during implementation. Task gained scheduled_time and due_date, and Pet.complete_task() now keeps the completed task and adds a new daily or weekly occurrence. I updated the final UML to reflect these additions instead of leaving it at the original skeleton.

Input validation, pet-task associations, and a consistent plan format are now implemented. Owner.get_all_tasks() returns pairs so a task stays connected to the right pet. The plan dictionary contains selected and skipped tasks, explanations, and time totals. Separate sorting, filtering, and conflict methods let me add features without changing that format.

I kept the scope manageable for a short assignment. The Streamlit app now exposes the scheduling features, but it does not need extra domain classes. Task editing and removal are available in the backend, while the UI focuses on adding, viewing, and completing tasks.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

I put priority and the owner's available minutes first because the main goal is a useful daily care plan. The scheduler considers high-priority tasks first and adds whole tasks that fit. Completed and future-dated tasks are skipped. If a task is too long, it records a reason and continues looking for tasks that fit. The short-task preference only breaks ties within a priority.

This is a straightforward choice-by-choice approach, not a search through every possible combination. It is easy to explain, but it does not guarantee the fullest possible use of the budget. Chronological sorting is a separate view: it orders HH:MM times and puts untimed tasks last. Pet and completion filters help browse the list without changing the plan across all pets.

For recurrence, completing a daily task creates one pending occurrence due the next day; a weekly task creates one due seven days later. The dates are based on completion, so finishing late shifts the next occurrence instead of maintaining a fixed calendar schedule. Keeping the original completed task makes the history clear, and repeating completion does not add another copy.

**b. Tradeoffs**

I chose to keep conflict detection simple. The scheduler groups pending tasks by their date and exact starting time, including tasks for different pets, and returns a warning when a group has more than one task. It uses each task's due date when available, otherwise the planning date, which defaults to today. It ignores completed tasks and tasks without a scheduled time. It only reports conflicts; it does not change tasks or the generated plan.

The tradeoff is that it detects identical starting times on the same date but does not detect overlapping intervals with different starting times. For example, tasks scheduled for 09:00–09:30 and 09:15–09:45 would not trigger a warning. I chose this approach for a short assignment because the dictionary grouping is easy to understand and test, while full overlap detection would need more logic and edge cases. I kept the explicit dictionary version because a shorter version would not improve what it detects.

Later, I could combine each task's date and starting time, add its duration to calculate an ending time, and check whether two intervals overlap. I would add tests for partial overlaps, one task inside another, and tasks that cross midnight. Tasks that start exactly when another ends would not count as overlapping.

---

## 3. AI Collaboration

**a. How you used AI**

I used Codex to brainstorm the four classes, draft the UML and Python skeleton, and implement features in small phases. My prompts named the files to read, the behavior to add, the files to leave alone, and the checks to run. This made each change easier to review. For testing, I asked for a coverage plan before adding tests so we could build on the existing suite instead of starting over.

The most useful capabilities were codebase inspection, focused changes, test generation, and explanations of algorithm choices. Inspecting the actual methods helped keep the UI aligned with the backend. Generating tests helped cover less obvious cases, such as two different Task objects with identical details and completing a recurring task more than once. The explanations helped me judge whether a shorter implementation was actually better.

I mostly used the same Codex chat throughout the project. Keeping the earlier context helped maintain continuity because we could refer back to the design, decisions, and completed work. I kept things organized by giving focused prompts for each phase, from planning and algorithms to testing and final documentation. That helped make the next task clear without having to explain the whole project again.

**b. Judgment and verification**

One alternative we considered was replacing the explicit dictionary used for conflict grouping with defaultdict(list). That would remove the check for a missing group, but both approaches have expected O(n) time for n tasks. I kept the explicit dictionary because it was easier for me to follow and there was no meaningful improvement in behavior. This was a considered alternative, not a code change that had to be undone.

I made scope decisions throughout the work: keep the four classes, preserve working APIs and tests, limit conflicts to exact starting times, and separate documentation changes from code changes. I asked Codex to inspect existing behavior before adding requirements and to report actual test output. That gave me specific results to review rather than just accepting a claim that a feature worked.

I personally ran terminal commands, including python main.py and pytest, and shared the successful output. The CLI demo stayed within 40 minutes and explained why Grooming was skipped, and the test suite reached 97 passing cases. Running the commands myself gave me a way to check the results alongside Codex's reports.

Codex also ran and reported automated tests, syntax checks, and Streamlit AppTest smoke checks. AppTest checked task entry, sorting and filtering, conflict warnings, recurring completion, and state across reruns. These were automated UI checks, so I would not describe them as a full manual browser review that I completed myself.

---

## 4. Testing and Verification

**a. What you tested**

The automated suite checks priority and time-budget scheduling, chronological sorting, pet and completion filters, daily and weekly recurrence, and same-start-time conflict warnings. It also checks empty inputs, invalid times and settings, duplicate object additions, repeated completion, leap days, and year changes. Tests verify that rejected updates do not partly change an object and that detecting conflicts leaves tasks and the plan unchanged.

Phase 4 ended with 87 passing cases. Phase 5 added focused cases for duplicate prevention, strict owner settings, and recurrence chains, and extended a sorting test to check 09:05 before 09:45. The latest recorded pytest run passed all 97 cases. These tests exercise the real classes and methods; only two replace the task accessor to check that Scheduler calls it. Most tests use the real accessor too.

These checks matter because a plausible-looking schedule can still hide errors, such as assigning a task to the wrong pet or creating duplicate recurring tasks. Streamlit AppTest smoke checks also verified that ordinary reruns do not add tasks and that completing a task clears the saved plan. Those UI checks were separate from the 97-case backend suite.

**b. Confidence**

My confidence is 4 out of 5. The 97 passing tests and UI smoke checks support the behaviors that are implemented, but they are not proof that every possible interaction works. Conflict detection still does not check duration overlaps, and the Streamlit UI is not comprehensively covered by automated tests or a recorded visual browser review.

With more time, I would turn the UI smoke checks into repeatable tests and cover longer user flows, such as completing tasks while changing filters. If I added interval-overlap detection, I would test tasks inside other tasks, intervals crossing midnight, and tasks that meet at an endpoint without overlapping.

---

## 5. Reflection

**a. What went well**

The separation between the backend and UI worked well. Sorting, filtering, recurring-task creation, and conflict warnings could be added to the same four-class design and then exposed in Streamlit. Returning pet-task pairs kept the results understandable even with multiple pets. Working in small phases also made it possible to identify specific gaps and grow the suite from 87 to 97 cases without replacing working tests.

**b. What you would improve**

I would first make the UI checks part of the saved test suite and add storage so pets and tasks survive beyond a Streamlit session. I would also consider full duration-overlap detection and UI controls for editing tasks. Before adding those features, I would define their behavior and edge cases so the implementation stays understandable instead of growing only because AI can generate more code.

**c. Key takeaway**

My main takeaway is that using AI does not remove my role as the lead architect. Codex can generate code quickly, but I am responsible for the requirements, class responsibilities, scope decisions, validation, and understanding the final product. A passing test suite is useful evidence, and I still need to know what it covers and what it leaves out. The best result comes from giving focused instructions, reviewing the changes and evidence, and choosing solutions I can explain.
