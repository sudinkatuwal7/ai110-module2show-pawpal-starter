# Bonus-feature verification

Date: October 11, 2026. This follow-up starts from the already pushed project commit `7013138f8599520c275fd9cf47a59f329e346bfc`, on `main`. The user supplied the corrected five bonus categories and authorized implementing the remaining work, committing and pushing. This record is separate from the original Strategy A/B experiment and the earlier 116-test audit.

## Rubric evidence

| Bonus category | Implemented evidence |
| --- | --- |
| Advanced algorithm via Agent Mode | `Scheduler.next_available_slot()` sorts reservations across pets and scans for the earliest sufficient gap. Agent request, files, work and corrections are recorded in `ai_interactions.md`. |
| JSON persistence | `persistence.save_owner()` / `load_owner()`, explicit Streamlit controls, validated schema and dates, atomic file replacement, and a test that loads in a separate Python process. README explains the workflow and modified files. |
| Advanced scheduling | Existing priority/budget planning remains functional. The additional free-slot search handles nested/partial overlaps, adjacent endpoints and previous-day spillover. README includes actual CLI output. |
| Professional formatting | Existing Streamlit tables, grouped fields, forms, headings, emoji and feedback are now explicitly mapped to their APIs in README, along with the structured CLI output functions. |
| Thorough prompt comparison | Existing structured A/B comparison and all archived evidence are preserved. The result remains a tie; the student selected A for form-based editing. |

These are implementation and evidence checks, not a promise of awarded points.

## Actual verification

Environment: Windows, Python 3.13.7, pytest 9.1.1, Streamlit 1.60.0. No packages were installed or dependency pins changed. Checks used `PYTHONDONTWRITEBYTECODE=1`; pytest disabled its cache provider.

| Check | Actual result |
| --- | --- |
| Initial new-test run | 31 passed, 3 failed in 3.26s. All failures were in the new test helper, which inspected the clicked Button rather than the returned AppTest. The agent fixed the helper. |
| `python -m pytest tests/test_bonus_features.py -q -p no:cacheprovider` | 34 passed in 3.57s; exit 0 |
| `python -m pytest -q -p no:cacheprovider` | 150 passed in 12.88s; exit 0. Includes unchanged original 97 and frozen 19 cases. |
| `python main.py` | Exit 0; existing priority/filter/recurrence/conflict demos and the new interval-search example printed successfully. |
| In-memory `compile()` of every published Python source | 14 files compiled; exit 0; no bytecode written. |
| Architecture/UML source checks | Exactly Task, Pet, Owner and Scheduler; public method names present in both matching final UML files. Draft UML unchanged. |
| Preservation checks | Git object hashes confirm both original test files, requirements and draft UML unchanged. All 137 public comparison-archive SHA-256 entries match. |
| `git diff --check` | Exit 0; LF/CRLF conversion advisories only. |
| Ignore rules | Environment, `.env`, bytecode, pytest-cache and `data/pawpal.json` probes all ignored. |

Actual combined-suite summary:

```text
150 passed in 12.88s
```

Actual new CLI excerpt:

```text
Next Available Slot Demo (09:00-11:00)
Reserved: Biscuit 09:00-09:30; Mochi 09:15-09:45 and 10:00-10:15
- 15 minutes: 09:45
- 20 minutes: 10:15
- 60 minutes: No available slot
```

The new tests verify JSON round trips with duplicate names, Unicode, nullable fields, completed and recurring tasks, and owner preferences; schema/date/value rejection; absent and malformed files; failed replacement preserving the previous file and removing the temporary file; and invalid live data being rejected before overwriting a save. UI tests save, start a new app session, load, clear stale drafts/plans, and edit restored objects. Failed loads preserve the live owner and plan. Search tests include an independent exhaustive small-case oracle (360 interval/duration combinations), cross-pet overlaps, midnight boundaries, invalid inputs, and UI success/no-fit/error messages.

## Scope and limitations

- The new persistence layer uses functions, retaining the four domain classes. The existing editor and backend methods retain their behavior; `Scheduler` gains one method.
- Local saves require explicit Save/Load and are ignored by Git. Loading replaces session data only after validation. The file is shared by sessions on the same server, so this is a single-owner local workflow, without accounts, locking or concurrent merge support. Hosting must provide persistent disk for saves to survive host replacement.
- Slot search suggests room for an additional task. It does not reserve or move tasks, repair existing conflicts, or make the priority plan enforce appointment times. Dates and recurrence semantics are documented in README.
- No manual browser, accessibility or rendered-Mermaid review was performed. AppTest is automated UI verification. No clean dependency reinstall was attempted.
- The frozen evidence archive, candidate worktrees and original tests were not edited. Historical audit/report text is retained with explicit pointers to this follow-up. No private transcripts or real saved pet data were added.
- The user's manual correction was supplying the actual bonus rubric; no manual code repair was reported. The agent's test-helper correction is disclosed above.

Changed files: `.gitignore`, `README.md`, `ai_interactions.md`, `app.py`, `main.py`, `pawpal_system.py`, `persistence.py`, `reflection.md`, `diagrams/uml.mmd`, `diagrams/uml_final.mmd`, `tests/test_bonus_features.py`, this verification file, `docs/prompt_comparison.md`, and `docs/submission_readiness.md`.
