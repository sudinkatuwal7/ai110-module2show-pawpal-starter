# Frozen acceptance coverage

The original 97 cases in `tests/test_pawpal.py` are unchanged. The identical
new `tests/test_pending_task_editing.py` in each worktree contains 19 collected
cases (12 test functions, including parameterization). Only syntax and collection
were checked during preparation. These new tests have NOT been executed, and no
candidate implementation has been produced or evaluated.

| Criterion | Shared test function(s) |
| --- | --- |
| AC1 | `test_pending_selector_disambiguates_equal_objects_and_ignores_browse_filters` |
| AC2 | `test_switching_tasks_discards_drafts_and_preserves_tasks_and_plan` |
| AC3 | `test_save_all_fields_uses_real_update_and_preserves_identity`, `test_optional_time_and_due_date_can_be_cleared` |
| AC4 | `test_switching_tasks_discards_drafts_and_preserves_tasks_and_plan` |
| AC5 | `test_invalid_save_is_atomic_and_keeps_existing_plan` (four inputs), `test_save_all_fields_uses_real_update_and_preserves_identity` |
| AC6 | `test_save_all_fields_uses_real_update_and_preserves_identity`, `test_pending_selector_disambiguates_equal_objects_and_ignores_browse_filters` |
| AC7 | `test_invalid_save_is_atomic_and_keeps_existing_plan`, `test_unchanged_save_keeps_plan_and_repeated_reruns_do_not_duplicate` (two inputs), valid-save and draft tests |
| AC8 | `test_time_and_date_edits_refresh_sorting_and_cross_pet_warnings`, `test_optional_time_and_due_date_can_be_cleared` |
| AC9 | `test_edit_then_complete_creates_one_occurrence_with_edited_details` (daily and weekly) |
| AC10 | recurrence and repeated-save tests; `test_stale_submission_cannot_edit_completed_task_or_redirect_to_another` |
| AC11 | `test_empty_editor_states_are_safe_and_explain_what_to_do` (three states) |
| AC12 | all 97 baseline tests; `test_edited_values_feed_the_existing_budget_and_priority_scheduler`; `test_existing_task_creation_and_filtering_still_work`; completion and warning tests |

## Evaluation boundaries

- AppTest assertions inspect public widgets, rendered table rows and warnings,
  object identity and fields, and the existing session plan. There is no required
  candidate helper function, form layout, callback design, or lookup algorithm.
- The agreed string-valued selector and widget keys are the common test interface.
  They are identical for both candidates and specified before implementation.
- Real `Task.update_details()` runs normally; one delegated wrapper records that
  the existing API is used. It never substitutes validation or hardcoded results.
- Dates are relative to the local day captured per fixture. Record and match
  local date conditions when running both candidates; no private clock API is
  required from implementations.
- Positive duration controls may prevent invalid numeric input before submission.
  Invalid title/time cases exercise atomic multi-field rejection through the UI;
  baseline tests already exercise backend duration and other validation.
- Visual readability, keyboard usability, and responsive layout require separate
  human inspection. Do not infer visual verification from AppTest collection or
  future automated passes.
- No acceptance result exists yet. If an evaluator defect is discovered later,
  retain the original version and record a protocol amendment, apply the same
  corrected test to both unchanged candidates, and rerun both. Never quietly
  tailor the tests to one implementation.
