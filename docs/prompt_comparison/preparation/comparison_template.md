# Prompt comparison - experiment not run

This is an external preparation template. It has not been added to the main
repository. After actual runs and review, it can become
`docs/prompt_comparison.md`; copy only supported findings into
`ai_interactions.md`'s existing Prompt Comparison section.

| Measure | Strategy A: direct | Strategy B: staged |
| --- | --- | --- |
| Starting commit | 98805949bffcb69f5e5299a4deaafe6b8bdb3623 | 98805949bffcb69f5e5299a4deaafe6b8bdb3623 |
| Prepared prompt | prompt_a.txt | prompt_b.txt |
| Shared specification/tests | See frozen_manifest.json | Identical; see frozen_manifest.json |
| Model/version and reasoning setting | NOT RECORDED | NOT RECORDED |
| Run status | NOT RUN | NOT RUN |
| Actual transcript and patch | Not produced | Not produced |
| Baseline after implementation | NOT RUN | NOT RUN |
| AC1-AC12 after implementation | NOT VERIFIED | NOT VERIFIED |
| Identity, atomicity, duplicate protection | NOT VERIFIED | NOT VERIFIED |
| Invalidated plans and reruns | NOT VERIFIED | NOT VERIFIED |
| Changed files / scope violations | Not evaluated | Not evaluated |
| Elapsed time / self-corrections | Not recorded | Not recorded |
| Human usability/readability observations | Not recorded | Not recorded |
| Human corrections after frozen result | Not performed | Not performed |
| Decision | Undecided | Undecided |

The preparation-only 97-test passes must not be represented as post-implementation
results. Keep raw output and diffs for failed candidates as well as successful
ones. A tie or neither acceptable is a valid conclusion. This is one controlled
case study, not proof of a universally better model or prompt.

## Mapping to ai_interactions.md

| Existing row | Evidence to insert after the runs |
| --- | --- |
| Model / tool used | Actual exposed identity and settings; unavailable fields explicitly labeled |
| Prompt | Link to each complete, unedited prompt |
| Response summary | What that candidate actually implemented |
| What was useful | Specific observed strengths |
| Problems noticed | Actual test failures or review findings |
| Decision | Evidence-based selection, tie, or neither acceptable |

Do not fill the final-implementation conclusion until a candidate is reviewed and
the user authorizes integration. Distinguish agent self-corrections during a run
from human corrections afterward.
