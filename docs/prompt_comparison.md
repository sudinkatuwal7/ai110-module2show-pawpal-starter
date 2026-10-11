# PawPal+ pending-task editor: prompt comparison

> Historical experiment and integration report. The integrated project was later committed and pushed as `7013138f8599520c275fd9cf47a59f329e346bfc`. Subsequent bonus work extends main with persistence and free-slot search; see [bonus verification](bonus_verification.md). Frozen candidates, original evidence and the experimental tie remain unchanged.

Evaluation date: **2026-10-11**, America/Chicago. Experimental result: **tie**. Integration decision: **Strategy A selected by the user for its form-based editing experience and copied into main's working tree; not committed**.

Both unchanged implementations pass the same 97 baseline tests and 19 frozen acceptance tests. The evaluator independently reproduced all 116 passes for each. Review found different strengths, but no demonstrated correctness or overall quality advantage large enough to select a winner. This is one case study with unequal prior context, not evidence that either prompting strategy is generally better.

Submission cleanup subsequently redacted personal home paths and machine account identifiers from public evidence copies. The complete raw archive was backed up outside the repository first; no results were removed or invented. Frozen prompts, candidate source and acceptance-test bytes are unchanged. See the [privacy disclosure and hash manifests](prompt_comparison/README.md#submission-privacy-cleanup). References below to original capture or integrity checks describe their historical pre-redaction state.

## Evidence and preservation

The starting commit was `98805949bffcb69f5e5299a4deaafe6b8bdb3623`. Candidates remain in the original temporary worktrees on `experiment/prompt-a` and `experiment/prompt-b`. Before rerunning their checks or comparing code, the evaluator copied both `app.py` files, captured their Git patches, status and hashes, copied the preparation archive, and extracted available original tool outputs from local Codex session records. No candidate repair was made.

- Exact frozen prompts: [A](prompt_comparison/preparation/prompt_a.txt), [B](prompt_comparison/preparation/prompt_b.txt). Their entire prefix before `## Strategy instruction` is byte-identical.
- Original artifacts: [A patch](prompt_comparison/original/a/app.patch), [B patch](prompt_comparison/original/b/app.patch), [A source](prompt_comparison/original/a/app.py), [B source](prompt_comparison/original/b/app.py).
- Actual visible transcript excerpts: [A](prompt_comparison/original/a/transcript.visible.jsonl), [B](prompt_comparison/original/b/transcript.visible.jsonl). These preserve actual JSONL records with disclosed privacy substitutions, not reconstructed dialogue. Internal reasoning and system/developer messages are excluded. Source locations, original line numbers and session metadata are in each candidate's `provenance.json`.
- Original tool results: [A](prompt_comparison/original/a/tool-results.json), [B](prompt_comparison/original/b/tool-results.json). Original final reports: [A](prompt_comparison/original/a/final-response.md), [B](prompt_comparison/original/b/final-response.md).
- [Evidence hashes](prompt_comparison/evidence-sha256.json), [environment](prompt_comparison/environment.json), [review metrics](prompt_comparison/review-metrics.json), and [evidence index](prompt_comparison/README.md).

The original extraction initially omitted assistant prose because this log format uses `phase`, not `channel`; the extractor was corrected to preserve the actual commentary and final records. Existing source snapshots and patches were unchanged. Original tool results were already preserved before evaluation. This was an evidence-processing correction, not a candidate repair.

All 13 protected files in each candidate matched their preparation hashes, including the 97-test suite and the frozen acceptance file. Only `app.py` differed from the baseline, apart from the supplied untracked acceptance file. All copied frozen artifacts matched their recorded hashes before submission privacy redaction. The archived acceptance source is named `test_pending_task_editing.py.txt` to preserve its bytes without adding a test to main's pytest discovery; the original archive and both candidate test files retain their original names and bytes.

## Comparison

| Measure | Strategy A: direct | Strategy B: staged |
| --- | --- | --- |
| Original candidate tests | 97 baseline / 19 acceptance / 116 combined passed | 97 baseline / 19 acceptance / 116 combined passed |
| Independent evaluator tests | 97 / 19 / 116 passed; 0 failures | 97 / 19 / 116 passed; 0 failures |
| Frozen AC1–AC12 | All PASS within frozen coverage | All PASS within frozen coverage |
| Scope | Only `app.py`; +116 / −0 lines | Only `app.py`; +98 / −0 lines |
| New functions | `load_task_editor`, `save_pending_task` | `load_task_editor`, `save_task_changes`, `render_task_editor` |
| Existing functions modified | None | None |
| UI organization | 66 added lines in the existing top-level task section; editor form | Dedicated rendering function, called once from the existing task section |
| Main strengths | Batched form submission; explicit field guidance; readable validation mapping | Smaller diff; separated rendering; Pet/Task identity pair; explicit full date range |
| Main weaknesses | More top-level code; extra selection-label state; implicit date limits | Every widget event reruns the app; fewer field hints; change detection depends on `vars(task)` |
| State management | Loaded Task plus previous label; callback captures Pet/Task | Loaded Pet/Task tuple; callback captures Pet/Task |
| Human corrections to candidates | None observed or applied; none required by frozen checks | None observed or applied; none required by frozen checks |
| Remaining verification | Browser interaction, accessibility, responsiveness, numeric-entry UX | Same |
| Experimental decision | Tie | Tie |
| Subsequent integration choice | Selected by the user for form-based editing | Preserved as comparison evidence; not integrated |

Line count is descriptive. B's 18-line reduction does not establish better correctness, and A's form is a structural usability advantage whose perceived benefit was not browser-tested.

## Original results versus evaluator reruns

The original test output is available in the preserved tool records and corroborates the original final reports. Preparation-only test passes inside README text or preparation logs are **not** counted as implementation results.

| Suite | Original A | Original B | Evaluator A | Evaluator B |
| --- | --- | --- | --- | --- |
| Baseline | 97 passed, 0.24s | 97 passed, 0.21s | 97 passed, 0.18s | 97 passed, 0.18s |
| Frozen acceptance | 19 passed, 20.49s | 19 passed, 21.12s | 19 passed, 10.28s | 19 passed, 10.28s |
| Combined | 116 passed, 15.40s | 116 passed, 18.36s | 116 passed, 10.66s | 116 passed, 10.40s |

These are pytest-reported durations, not comparable performance benchmarks. Original A ran its baseline and acceptance commands concurrently; original B ran them sequentially. The evaluator ran every check sequentially, A then B, using the recorded interpreter:

`<USER_HOME>\AppData\Local\Programs\Python\Python313\python.exe`

Each candidate's working directory was its own worktree. The evaluator ran all eight frozen commands with `PYTHONDONTWRITEBYTECODE=1`:

```powershell
python -m pytest tests/test_pawpal.py -p no:cacheprovider
python -m pytest tests/test_pending_task_editing.py -p no:cacheprovider
python -m pytest -p no:cacheprovider
python main.py
python -c "from pathlib import Path; compile(Path('app.py').read_text(encoding='utf-8'), 'app.py', 'exec'); print('app.py syntax OK')"
git diff --check
git diff --stat
git status --short
```

`python` above denotes that absolute recorded executable. Git used a command-local `-c safe.directory=<candidate path>` override because the sandbox account differs from the worktree owner; no global Git setting changed. All 16 evaluator commands exited 0. Both demos completed, both syntax checks printed `app.py syntax OK`, and both diff checks passed. Git emitted an LF-to-CRLF advisory. Status showed only modified `app.py` and the supplied untracked acceptance test.

Full per-command stdout, stderr, argv, directories, exit codes, wall durations and timestamps are in [evaluator-reruns/commands.json](prompt_comparison/evaluator-reruns/commands.json) and the linked files. Both reruns used local date **2026-10-11** without crossing midnight. Their hashes were checked before and after verification.

At the end of evaluation, before integration, main's own `python -m pytest -p no:cacheprovider` still collected exactly its original 97 cases and passed all 97 in 0.20s. The documentation diff check passed. [Evaluation integrity evidence](prompt_comparison/final-integrity.json) records that earlier state: both candidates were unchanged and `ai_interactions.md` was the only changed pre-existing main file. This historical evidence has not been rewritten to describe the later integration.

## Implementation review

**Correctness.** Both use numbered string labels in the Owner collection order, keep completion and browse filters separate from editor selection, and load all six editable attributes. Both capture the rendered Pet and Task in callback arguments, verify that the task remains owned and pending, and use the real atomic backend update method. Neither replaces or appends tasks. Backend completion alone creates recurring occurrences. Save callbacks execute before the app redraws the chronological list and warnings.

**Validation and cached plans.** A constructs a normalized `changes` dictionary and compares its six proposed attributes with saved values; it clears the plan only after validation succeeds. It explicitly guards a `None` duration, since the backend interprets that argument as unspecified. B compares a shallow copy of `vars(task)` before and after the update, so normalized no-ops retain the plan. This works for the present dataclass, but couples UI change detection to all instance attributes. A's comparison is more explicit about the editor contract; B's comparison directly measures the saved result. Both show errors without changing fields on the frozen invalid inputs.

**Widget state.** A places the six fields in a form, with selection outside it. Draft editing is batched until Save; switching selection loads the next task and discards the prior draft. Its extra `edit_previous_label` state distinguishes navigation from relabeling. B uses ordinary widgets, a Pet/Task tuple and a smaller label-recovery path. It explicitly preserves both identities, but sends each field event through a full app rerun. Both keep a nonfirst task selected after repeated renaming in supplemental AppTest checks. Neither uses mutable dataclass equality to locate a task.

**Readability and maintainability.** A's explicit conditionals and field mapping are easy to trace alongside the existing app style. Its larger top-level UI block makes the main script longer. B's `render_task_editor()` makes the main flow easier to scan and groups editor responsibilities, although it still accesses global Streamlit session state. B's message-dispatch dictionary is compact; A's `if`/`elif` is more conventional for beginners. These are modest tradeoffs, not evidence of unnecessary architectural complexity.

**Duplication and scope.** Both repeat the existing creation controls for an independently keyed editor and explicitly list the six fields when loading and saving. That is reasonable for this limited feature; neither duplicates backend validation or recurrence logic. B scans `owner.get_all_tasks()` to verify ownership; A checks pets and the selected pet's tasks directly. Neither approach is a practical scalability concern at this app's size. No existing function body, backend, dependency, test or candidate documentation was changed.

## Acceptance review and coverage boundaries

PASS below means the frozen tests and relevant code review support the criterion; it does not mean every possible input or browser interaction was verified. The exact test mapping is preserved in [acceptance_coverage.md](prompt_comparison/preparation/acceptance_coverage.md).

| Criterion | A | B | Evidence / boundary |
| --- | --- | --- | --- |
| AC1: select a specific pending task | PASS | PASS | Identical tasks/pet names and browse-filter independence exercised |
| AC2: prepopulate; discard draft on switch | PASS | PASS | All six values checked across selections and ordinary reruns |
| AC3: edit attributes; clear optional fields | PASS | PASS | All attributes saved; time/date clearing exercised; numeric-entry UX and date navigation limits remain separate |
| AC4: mutate only on Save | PASS | PASS | Unsaved drafts and navigation preserve task fields and plan |
| AC5: atomic backend save and readable errors | PASS | PASS | Real `update_details()` delegation; blank/whitespace title and invalid HH:MM exercised |
| AC6: preserve identity, ownership and position | PASS | PASS | Collection IDs and other tasks checked before/after saves |
| AC7: invalidate only after a real valid change | PASS | PASS | Changes, invalid inputs and normalized no-ops exercised |
| AC8: immediate ordering and warnings | PASS | PASS | Rendered rows/warnings checked; untimed last; exact-time/date semantics |
| AC9: recurrence generated by completion | PASS | PASS | Daily and weekly edits followed by existing completion workflow |
| AC10: no duplicates; reject stale saves | PASS | PASS | Repeated saves/reruns; selected task completed before submission |
| AC11: helpful empty states | PASS | PASS | No pets, no tasks and all completed |
| AC12: preserve existing app/backend behavior | PASS | PASS | 97 baseline cases plus creation/filter/budget/priority/completion checks |

The frozen suite does not exhaust numeric input behavior, every valid time/date boundary, all recurrence transitions, recovery after every invalid submission, external removal/reordering, simultaneous sessions, very large collections, keyboard accessibility, responsive layouts, or actual browser form behavior. Deletion and persistence remain outside the requested feature.

## Supplemental evaluator observations

The evaluator ran the same [supplemental probes](prompt_comparison/supplemental_checks.py) in separate processes against both candidates, without modifying the frozen tests or candidate files. Raw outputs are [A](prompt_comparison/evaluator-reruns/a/supplemental.stdout.json) and [B](prompt_comparison/evaluator-reruns/b/supplemental.stdout.json). They do not change the 19-test frozen score.

- Last pending task completed before Save: both preserved all task fields and the cached plan, showed a stale-edit error and left no active Save button.
- Repeated rename of the second of two identical tasks: both retained the selected object, preserved the first task and created no duplicate.
- Numeric inputs `None`, `0`, `-1`, and `2.5`: in this installed Streamlit/AppTest environment, the first three became `1`, and `2.5` became `2` before saving. Both saved the valid normalized integer and proposed title. The probes' `atomic_rejection: false` is **not** evidence that invalid values reached the callbacks: the framework normalized them first. A's extra `None` guard therefore did not distinguish the candidates. Actual empty/fractional typing in a browser remains unverified; the automatic fallback deserves a usability check.
- Date widget protocol bounds: A exposed `2016-10-11` through `2036-10-11` for the fixture date, using Streamlit's defaults. B explicitly exposed `0001-01-01` through `9999-12-31`. This is a real control-configuration difference. Neither far-date browser navigation nor all extreme backend dates was exercised. B offers broader range; whether that improves this product was not specified.

## Experimental conditions and limitations

| Condition | Finding |
| --- | --- |
| Starting code and tests | Same baseline and prepared candidate hashes; frozen shared prompt prefix identical |
| Strategy difference | A says implement directly; B explicitly requests inspection, a brief risk plan, implementation, checks and review |
| Model/configuration | Both candidate `turn_context` records say `gpt-6-astra`, effort `high`, Codex CLI `0.155.1`; immutable served model/build is unavailable |
| Original reporting discrepancy | Both original final reports said exact model/settings were unavailable; later local session metadata supplies the configuration labels, not a model-build guarantee |
| Prior context: A | **Retained preparation context.** Same session contains 16 earlier task requests, including experiment planning and preparation; not a fresh-context run |
| Prior context: B | **Verified from local records**, not assumed: separate session ID, no recorded fork parent, zero earlier task requests, candidate request as its first task. It still received standard session instructions and read shared preparation artifacts during the run |
| Independence | No observed read of the other candidate's completed implementation/transcript/results during either original run. B read shared preparation metadata containing A's pre-run checks; this was not A's completed result |
| Interpreter/dependencies | Same recorded Python 3.13.7 executable; pytest 9.1.1 and Streamlit 1.60.0. Evaluator package inventory matches every dependency recorded during preparation |
| Permissions/tool conditions | Both records report `on-request`, workspace-write and restricted network. Launch directories/workspace roots differed. Both used shell and patch tools; B encountered directory/ownership errors and used scoped Git overrides. Identical effective OS permissions and every tool/backend condition cannot be established |
| Candidate order | A then B, matching preparation. No interleaved candidate implementation |
| Original timing | Request-to-final wall spans: A 235.185s, B 171.576s, both below 30 minutes. These include tools/infrastructure and are not measured active reasoning time |
| Pauses | No candidate permission-approval wait observed. B's initial path/ownership troubleshooting is visible but its duration was not separately instrumented. Preparation had earlier approved worktree retries, outside candidate runs |
| Original test execution | A ran baseline and acceptance concurrently and the demo before the combined suite; B ran sequentially. Commands were present, but original scheduling was not identical |
| Date | Original candidate and evaluator tests all recorded 2026-10-11 locally |
| Corrections | One implementation patch observed per candidate; no later candidate edits or human repairs observed. Evaluator made no candidate corrections |
| Browser review | None performed; AppTest verifies widget state and rendered data, not visual appearance or accessibility |
| Evaluator independence | Reruns were fresh processes, but this evaluator session previously implemented B. The review is not blinded or independent human judgment |

Thus the experiment did **not** isolate prompting strategy as the only changing condition. A's retained project/preparation history, B's fresh session, infrastructure differences, and single-run sample prevent causal claims about prompting effectiveness. The frozen preparation metadata still says candidates were not run and model details were not recorded; it is preserved as a historical artifact, not rewritten as current truth.

## Experimental decision and subsequent integration

**Tie.** Both pass the correctness gates: baseline preservation, task identity, atomic validation under tested inputs, and no duplicate creation. A's form and guidance and B's modular rendering and smaller scope are useful but competing advantages. No demonstrated defect or agreed usability priority justifies declaring either universally better.

No human correction was required to satisfy the frozen tests. A browser review could further assess form batching versus live reruns, date navigation and numeric-entry feedback; no such review has been performed.

After reviewing the tied result, the user explicitly approved integrating **Strategy A** because its form batches edits until **Save changes**. This is a product interaction preference, not a reversal of the experimental tie or evidence that direct prompting is generally superior.

Main's `app.py` was copied byte-for-byte from `prompt_comparison/original/a/app.py`. The frozen acceptance source was copied without edits into `tests/test_pending_task_editing.py`, adding 19 cases to the original 97. README now explains the editor. The backend, four-class architecture, original tests, preserved evidence and both candidate worktrees remain unchanged. Integration verification is recorded separately from the original candidate and evaluator runs. No packages were installed and no commit, merge, cherry-pick or push was performed; the integrated working tree awaits user review.

Integration checks on **2026-10-11** used the same recorded Python 3.13.7 executable in the original main worktree with `PYTHONDONTWRITEBYTECODE=1`. [Integration verification output](prompt_comparison/integration-verification.json) preserves the exact commands, timestamps, exit codes, stdout and stderr.

| Integration check | Actual result |
| --- | --- |
| Original baseline suite | 97 passed in 0.11s |
| Frozen acceptance suite | 19 passed in 14.76s |
| Complete pytest suite | 116 passed in 15.65s |
| `python main.py` | Exit 0; all existing demos completed |
| In-memory syntax compilation | Passed for app, backend, CLI and both test files; no bytecode written |
| `git diff --check` | Exit 0 |

The scope audit found four modified files for this integration (`app.py`, `README.md`, `ai_interactions.md`, and this report) and two additions (the frozen test file and integration verification JSON). Previously uncommitted evaluation artifacts were retained. Hashes confirmed no changes to either candidate worktree or the original preparation archive. No new or modified cache files or credential-pattern matches were found in the inspected project/evidence files. A pre-existing tracked `__pycache__/pawpal_system.cpython-314.pyc` was preserved, not generated by this integration. Browser usability, accessibility and extreme date navigation remain unverified; the experimental limitations above still apply.
