# Evidence index

Read [the comparison report](../prompt_comparison.md) for findings. This directory preserves original evidence separately from evaluator reruns.

## Submission privacy cleanup

Personal Windows home paths and machine account identifiers have been replaced with `<USER_HOME>`, `<LOCAL_USER>`, `<SANDBOX_USER>` or `<LOCAL_SID>` in the submission copies. Test counts, results, timings and candidate code were not changed. **These are disclosed redacted copies, not byte-identical raw transcripts.** The frozen prompts, frozen acceptance source and both original `app.py` snapshots remain byte-identical.

Before redaction, the complete raw documentation/evidence tree was copied outside Git to the local temporary folder `pawpal-submission-original-evidence-20261011`. Nothing was silently deleted. The evidence tree was under 1 MB and its largest file under 200 KB, so all grading evidence was retained rather than pruned. Virtual environments and caches are not part of this archive.

[redaction-manifest.json](redaction-manifest.json) lists each affected file with before/after hashes. Historical `evidence-sha256.json`, frozen manifests and integrity reports describe the earlier raw state and are retained as historical records; their hashes can differ for redacted files. [submission-sha256.json](submission-sha256.json) records the final distributed evidence hashes. JSON/JSONL syntax was checked after redaction. Historical executable paths and script constants now contain placeholders; configure local paths before reusing those scripts.

| Location | Contents |
| --- | --- |
| `preparation/` | Frozen prompts, shared specification, coverage map, manifests, original environment and preparation logs; historical NOT RUN text is intentionally unchanged |
| `original/a/`, `original/b/` | Unchanged source snapshots, original diffs, status, file hashes, actual visible JSONL transcript records, tool results, final reports and provenance |
| `environment.json` | Evaluator interpreter/dependencies, candidate session configuration, original main-file hashes |
| `evidence-sha256.json` | SHA-256 hashes of preserved original and preparation artifacts |
| `review-metrics.json` | Frozen-file integrity, common prompt prefix, dependency comparison, AST function/line metrics and original wall times |
| `final-integrity.json` | Final candidate/evidence hashes, unchanged main code, main's 97-test run and documentation checks |
| `evaluator-reruns/commands.json` | Exact eight commands per candidate, argv, cwd, timestamps, exit codes and output paths |
| `evaluator-reruns/a/`, `evaluator-reruns/b/` | Independent stdout/stderr for frozen verification; separately named supplemental observations |
| `capture_evidence.py` | Capture procedure; refuses to overwrite an existing `original/` directory |
| `verify_candidates.py` | Sequential A/B verification procedure; refuses to overwrite existing rerun evidence |
| `supplemental_checks.py` | Identical evaluator-only AppTest probes, separate from frozen tests |

Transcript excerpts were extracted from actual visible message and tool records from the local sessions, then redacted as disclosed above. They omit internal reasoning and system/developer messages. Provenance records list the original source lines and raw source snapshot hash; a growing session file need not retain the same whole-file hash later. No missing dialogue was invented. Each candidate's final response is extracted from its actual final message, with the same path redactions.

The archived acceptance source is `preparation/test_pending_task_editing.py.txt`. Only the archive copy's suffix differs; its bytes match the frozen `.py` source. This prevents pytest from collecting documentation evidence as a new main-branch test. `review-metrics.json` verifies the original frozen filename-to-hash mapping with this one explicit filename translation.

Do not treat preparation logs or test output embedded in a read README as post-implementation results. Original candidate outcomes are in their actual tool records/final reports; evaluator outcomes have their own directory. No candidate was repaired during evaluation.

To reproduce without overwriting evidence, run the documented frozen commands in each existing candidate worktree with a matching interpreter and `PYTHONDONTWRITEBYTECODE=1`. The archived scripts record the original procedure with personal paths now replaced by placeholders; they are evidence, not portable deployment tools.
