# PawPal+ submission-readiness audit

> Historical audit before the first submission commit. That project state was subsequently committed and pushed as `7013138f8599520c275fd9cf47a59f329e346bfc`. The later bonus features and 150-test results are recorded in [bonus verification](bonus_verification.md). The findings below describe the earlier 116-test, session-only version and are retained as evidence.

Audited October 11, 2026, on `main` in the original `ai110-module2show-pawpal-starter` repository. HEAD remains `98805949bffcb69f5e5299a4deaafe6b8bdb3623`; the completed work is still uncommitted. No packages were installed and nothing was pushed or submitted.

## Required project evidence

This checks the previously supplied 20-point rubric categories without promising a grade or inventing bonus requirements.

| Category / phase | Result | Evidence |
| --- | --- | --- |
| Scenario and initial design | PASS | README scenario and retained `diagrams/uml_draft.mmd` |
| Final UML | PASS for source review | `uml_final.mmd` and the default `uml.mmd` show the four classes, current fields/methods and Owner–Pet–Task relationships; draft retained |
| Core OOP implementation | PASS | `Task`, `Pet`, `Owner`, `Scheduler` remain the only backend classes; `Task.name` provides the task title/description, with due date/time and derived completion state |
| Algorithms | PASS | Priority/time-budget scheduling, chronological sorting, pet/status filtering, daily/weekly recurrence and exact-start-time conflicts; multi-pet behavior exercised |
| CLI demo | PASS | `main.py` creates one owner, two pets and four tasks; generates a real plan with explanations and runs sorting/filtering, recurrence and conflict demos |
| Tests | PASS | 116 cases passed in 20.11s: original 97 plus unchanged 19 frozen editor acceptance cases |
| UI integration | PASS within AppTest coverage | Strategy A editor remains byte-identical to the preserved candidate; existing creation, completion and scheduling workflows pass |
| Documentation and reflection | PASS | README setup, demo, algorithms and actual output; reflection updated to 116 tests and completed editing; agent workflow and comparison documented truthfully |
| Dependencies | PASS in installed environment | Requirements pin installed/tested Streamlit 1.60.0 and pytest 9.1.1; Python 3.13.7 used; packages declare Python >=3.10 |

Both test files, backend, CLI, app and draft/final UML were checked against pre-cleanup hashes and were not modified by cleanup. Reflection section 2b's exact-time conflict tradeoff discussion was preserved. The old placeholder `diagrams/uml.mmd` now mirrors the existing final diagram.

## Repository hygiene and evidence

- Inspected Git's tracked, untracked and ignored inventories, sizes, changes, documentation and submission-file content. At audit entry: 13 tracked files, 138 untracked files, and 11,055 ignored files. The ignored files were virtual-environment dependencies and Python/pytest caches; third-party environment contents were inventoried, not individually source-reviewed.
- Removed `__pycache__/pawpal_system.cpython-314.pyc` from the Git index with `git rm --cached`. It still exists locally. This is the sole staged change; no other files were staged by this audit.
- `.gitignore` now covers `__pycache__/`, `*.py[cod]`, `.venv/`, `.venv_new/`, `venv/`, `.env`, `.env.*`, and `.pytest_cache/`. Ten representative ignore checks passed. Virtual environments were not deleted or changed.
- The evidence archive was under 1 MB; its largest file was under 200 KB. No large binary payloads or credential patterns were found. All grading evidence was retained.
- Before privacy cleanup, the complete raw documentation/evidence tree was backed up outside Git in the local temporary folder `pawpal-submission-original-evidence-20261011`. Personal home paths and machine account identifiers were replaced in 36 submission files with disclosed placeholders. Frozen prompts, original app snapshots, patches, acceptance source and test outcomes remain intact. No evidence was silently deleted.
- [Redaction manifest](prompt_comparison/redaction-manifest.json) records the affected copies and original hashes. [Submission hashes](prompt_comparison/submission-sha256.json) cover the final public evidence. Historical manifests and original results remain labelled as historical; raw copies are retained locally. The external preparation archive and both experiment worktrees remain unchanged.
- Pattern scans of tracked/untracked submission text found no personal absolute home paths, private keys, known API-token patterns or literal credential matches after cleanup. This is a pattern-based audit, not a guarantee that every possible secret format is detectable. No `.env` or credential file is included in the submission inventory.

## Verification and remaining limits

The recorded checks are in [submission-verification.json](submission-verification.json): complete pytest suite, `python main.py`, in-memory syntax compilation for eight Python files, `git diff --check`, and `git diff --cached --check`. All exited 0. Tests used `PYTHONDONTWRITEBYTECODE=1` and disabled the pytest cache provider. Git's LF-to-CRLF advisories do not indicate failed checks.

No code or test failure preventing submission was found. Browser visuals, keyboard accessibility and responsive layout were not manually verified. No installed `mmdc` renderer was found, so Mermaid rendering is NOT VERIFIED; class/method consistency was checked against the Python AST. A fresh dependency installation was not performed because package installation was prohibited. Conflict detection deliberately checks identical starts rather than overlapping durations, and data remains session-only.

The prompt experiment remains a tie with unequal prior context; Strategy A was chosen afterward for its form-based editing experience. Cleanup does not change that conclusion. The files still need the user's review and later authorization to commit/push/submit; those actions were intentionally not taken.
