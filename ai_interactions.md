# AI Interactions Log

This log records the agent workflow and prompt-comparison work completed for PawPal+.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked Codex to implement a pending-task editor while preserving the four-class backend, the original 97 tests, task identity, atomic validation, and existing scheduling behavior. I used two isolated candidates with frozen prompts and 19 shared acceptance tests, then authorized evaluation and integration separately.

**What did the agent do?**

Codex inspected the existing code, implemented each candidate in app.py, and ran the baseline, acceptance, and combined pytest suites, the CLI demo, syntax checks, and Git diff checks. It preserved the prompts, patches, actual available transcripts and results, independently reran the checks, and documented a tie. After my approval, it integrated Strategy A's form editor and the frozen acceptance tests, updated the documentation, and reran all 116 tests. The backend and original test file stayed unchanged.

**What did you have to verify or fix manually?**

I reviewed the comparison and chose Strategy A because I preferred editing fields together in a form. No manual candidate code repair was required by the frozen tests. I also requested a final cleanup of tracked bytecode, outdated documentation and personal paths in the submission evidence. The experiment's unequal prior context remains a limitation. I have not claimed a full manual browser review; the reported UI checks are automated AppTest runs.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Codex CLI 0.155.1; session metadata records `gpt-6-astra`, high reasoning effort. Exact served model build unavailable. | Same recorded configuration; exact served model build unavailable. |
| **Prompt** | [Frozen Strategy A: direct implementation](docs/prompt_comparison/preparation/prompt_a.txt) | [Frozen Strategy B: staged inspection, plan, implementation and review](docs/prompt_comparison/preparation/prompt_b.txt) |
| **Response summary** | Added a pending-task editor using a form, identity-safe selection and atomic backend saves. Only `app.py` changed: +116 / -0 lines. | Added a pending-task editor with a separate rendering helper, identity-safe selection and atomic backend saves. Only `app.py` changed: +98 / -0 lines. |
| **What was useful** | Form batches drafts until Save; explicit field help and validation mapping. Original and evaluator runs each passed 97 baseline, 19 acceptance and 116 combined tests. | Smaller diff and grouped rendering logic; explicit Pet/Task target and broad date bounds. Original and evaluator runs each passed 97 baseline, 19 acceptance and 116 combined tests. |
| **Problems noticed** | More top-level UI code and selection-label state; default date bounds. This run retained preparation context, so conditions were not fully controlled. No browser review. | Every widget event reruns the app; fewer field hints and change detection using `vars(task)`. Separate first-task session verified from logs; launch-directory/permission conditions differed. No browser review. |
| **Decision** | Experimental tie; subsequently selected for integration because the form batches edits until Save. No candidate repair needed or made. | Experimental tie; retained as evidence and not integrated. No candidate repair needed or made. |

I compared the actual patches and kept the original prompts, visible Codex transcripts, tool results and environment records separate from fresh evaluator checks. Both implementations preserved task identity, rejected the tested invalid edits atomically and avoided duplicate tasks. A's form and B's rendering helper are different strengths; the evidence did not establish an overall winner. The unequal prior context means I cannot attribute the differences only to prompt strategy. This was one run per strategy, not a general model-performance finding.

See [the full comparison and acceptance review](docs/prompt_comparison.md) and [evidence index](docs/prompt_comparison/README.md). The evaluator reran all eight frozen commands for each candidate on October 11, 2026; all exited successfully. Additional AppTest observations are labeled separately and are not browser verification. Neither candidate received a human repair.

**Which approach did you use in your final implementation and why?**

I selected Strategy A for integration because I prefer its form-based editing experience: users change task fields together and submit them with **Save changes**. Both candidates passed the same checks, so this choice does not turn the experimental tie into a claim that Strategy A or direct prompting is generally better. After my approval, the preserved A implementation and the unchanged 19 frozen acceptance tests were copied into main's working tree. The backend, original 97 tests, evidence archive and both candidate worktrees were preserved. The integration remains uncommitted for review, and no manual browser verification is claimed.
