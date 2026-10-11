# PawPal+ prompt-comparison preparation

Status: PREPARATION ONLY. Both candidate runs are NOT STARTED.

## Exact locations

- Original repository (unchanged main):
  `<USER_HOME>\Downloads\ai110-module2show-pawpal-starter-main\ai110-module2show-pawpal-starter`
- This external preparation archive:
  `<USER_HOME>\AppData\Local\Temp\pawpal-prompt-comparison-9880594\preparation`
- Candidate A, branch `experiment/prompt-a`:
  `<USER_HOME>\AppData\Local\Temp\pawpal-prompt-comparison-9880594\prompt-a`
- Candidate B, branch `experiment/prompt-b`:
  `<USER_HOME>\AppData\Local\Temp\pawpal-prompt-comparison-9880594\prompt-b`
- Both candidate HEADs:
  `98805949bffcb69f5e5299a4deaafe6b8bdb3623`

## Artifacts

| File | Purpose |
| --- | --- |
| shared_spec.md | All 12 acceptance criteria, common UI test interface, controls, commands |
| test_pending_task_editing.py | Master acceptance test; identical copies are in both candidates' tests directories |
| prompt_a.txt / prompt_b.txt | Full specification and full test source embedded in both; only the final strategy instruction differs |
| acceptance_coverage.md | Mapping of 19 acceptance cases to AC1-AC12 and verification limits |
| environment.json | Actual Python executable/version, installed distribution versions, candidate settings not yet recorded |
| baseline_manifest.json | Original tracked hashes and both candidate starting hashes/paths/branches |
| checkout_line_endings.json | Verified original/checkout line-ending differences |
| frozen_manifest.json | SHA-256 hashes of all preparation inputs/evidence at freeze time |
| commands.json | Exact preparation subprocess arguments, working directories, exit codes, raw output paths |
| logs/ | Actual stdout and stderr, including baseline pytest and acceptance collection in each worktree |
| verify_preparation.py | Rechecks frozen inputs, both candidate starting states, and original cleanliness |
| verification_report.json | Final preparation checks and exact verification commands/results |
| prepare_artifacts.py | Preparation procedure; refuses to overwrite a frozen experiment |
| preparation_issues.md | Resolved permission/ownership issues and known verification boundaries |
| comparison_template.md | Unfilled results structure for later documentation; no invented candidate results |

The baseline includes 13 tracked files. Each candidate adds only
`tests/test_pending_task_editing.py`; no existing file was changed. The Git `.git`
link necessarily differs between worktrees and is not a candidate input.

## Verification performed

- Original main: clean at the specified commit, 97 baseline cases passed.
- Each candidate: 97 baseline cases passed, 19 acceptance cases collected.
- New test source compiled successfully. Acceptance cases were NOT executed.
- Both candidates have matching tracked-file and acceptance-test SHA-256 hashes.
- Both prompts contain identical shared specification and tests; only the final
  strategy paragraph differs.
- `git diff --check` passes. The original main remains clean and its original
  tracked-file hashes are unchanged.

See raw logs for exact timings; these statements do not claim feature correctness.

## Recheck without running a candidate

Run under the normal user's terminal (sandbox ownership restrictions are recorded
in preparation_issues.md):

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python <USER_HOME>/AppData/Local/Temp/pawpal-prompt-comparison-9880594/preparation/verify_preparation.py
```

The verification script makes no candidate edits and does not run an agent or
acceptance tests. Its initial `--freeze` invocation creates the hash manifest and
verification report outside both worktrees. Later invocations without that flag
are read-only. A changed source file, supplied test, prompt, or starting commit
causes verification to fail.

## Before any implementation run

Wait for explicit user approval to run Strategy A. Record the actual exposed
model/version and reasoning setting at launch; reuse them for B or document the
confound. The order is A then B, matching the user's approval sequence. Use two
fresh sessions without this conversation's history or each other's outputs.
Give each its assigned worktree and complete prompt. Same tools, permissions,
Python environment, and 30-minute active-time allowance; no human hints.

Store future transcripts, patches, raw tests, and human review outside the frozen
preparation archive and both worktrees, for example in sibling
`<USER_HOME>\AppData\Local\Temp\pawpal-prompt-comparison-9880594\results`.
Do not let either candidate inspect the other or the results archive. Worktrees
separate files but share Git metadata; they are not a security isolation boundary.
Do not merge, commit, push, or integrate either candidate without later approval.

This archive is in a temporary directory. Preserve it before operating-system
temporary-file cleanup; moving/copying it into final project documentation is a
separate, later integration step. Nothing has been added to main for this archive.
