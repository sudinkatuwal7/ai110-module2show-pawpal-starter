# AI110 verification record

Observed November 5, 2026 UTC on Windows, Python 3.13.7. Commands ran from the repository root.

| Check | Actual result |
| --- | --- |
| `python -m compileall -q app.py pawpal_system.py persistence.py ai tests/test_ai_evaluation.py` | Exit 0, no syntax errors |
| `python -m ai.evaluate` | 23 passed in 5.27s, exit 0; mocked API, no live provider calls |
| `python -m pytest -p no:cacheprovider --basetemp=<FRESH_TEMP_DIR>` | 178 passed in 32.06s, exit 0. The personal temp-root path is redacted here. |
| `python -m streamlit run app.py --server.headless true --server.port 8503` | Server started and announced `http://localhost:8503`; stopped after startup check. Automated AppTest cases cover AI controls, but no manual browser review was performed. |
| Mermaid 11.12.0 `mermaid.parse()` on `diagrams/architecture.mmd` | Returned `{ diagramType: 'flowchart-v2', config: {} }` |
| `git diff --check` and `git diff --cached --check` | Exit 0; no whitespace errors. Git reported Windows LF/CRLF conversion warnings. |
| Secret pattern scan of changed code/docs | No Google-style API key found; no key value printed in this record. |

The first full pytest attempt used the pre-existing `.pytest_temp` as `--basetemp` and produced 21 fixture setup errors because Windows denied pytest permission to remove that directory; 154 tests passed in that attempt. Re-running with a fresh temp path passed all 175 then-collected tests. After two more UI cases and one citation case were added, the final full run above passed all 178. The temp-directory failure was environmental, not a test assertion failure.

The [live comparison](ai_live_comparison.json) was run separately with a real Gemini API key in the environment. The initial sandboxed call could not complete; the approved network run recorded one direct answer, one grounded answer, and one planning response. The comparison file contains no credentials. It is one example, not a general accuracy score.

## Local submission recheck — November 5, 2026 UTC

The following commands ran from the repository root on Windows with Python 3.13.7. This section preserves the earlier record above. The test harness mocks Gemini; the application safety response below is deterministic. No new live Gemini call was made. Personal root paths and the server's LAN URL are omitted.

### Full project tests

Command: `python -m pytest -p no:cacheprovider` (exit 0). Terminal output excerpt, with the private `rootdir` path replaced; the final file's progress arrived in two streamed chunks:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
rootdir: <REPOSITORY_ROOT>
plugins: anyio-4.12.1
collected 178 items

tests\test_ai_evaluation.py .......................                      [ 12%]
tests\test_ai_retriever.py .....                                         [ 15%]
tests\test_bonus_features.py ..................................          [ 34%]
tests\test_pawpal.py ................................................... [ 63%]
..............................................                           [ 89%]
tests\test_pending_task_editing.py .............
......                   [100%]

============================ 178 passed in 34.94s =============================
```

Command: `python -m ai.evaluate` (exit 0). This runs 23 deterministic cases with mocked model output and no provider call:

```text
.......................                                                  [100%]
23 passed in 6.65s
```

Command: `python -m compileall -q app.py pawpal_system.py persistence.py ai tests` (exit 0, no output). Python syntax passed for the application and tests.

### Streamlit startup

Command: `python -m streamlit run app.py --server.headless true --server.port 8503`. The process announced `Local URL: http://localhost:8503`. A separate command, `python -c "import urllib.request; r=urllib.request.urlopen('http://localhost:8503', timeout=5); print('HTTP', r.status); print('Content-Type:', r.headers.get('Content-Type'))"`, returned:

```text
HTTP 200
Content-Type: text/html; charset=utf-8
```

The server was then stopped with Ctrl+C. Startup and HTTP response do not replace a manual browser or accessibility review.

### Deterministic safety and planning behavior

Command: `python -c "import json; from ai.gemini_client import ask_gemini; print(json.dumps(ask_gemini('My dog swallowed poison'), ensure_ascii=False, indent=2))"` (exit 0). No API key or model call was needed:

```json
{
  "answer": "If this may be an emergency, contact a veterinarian or emergency veterinary clinic immediately. For suspected poisoning, contact a veterinarian or animal poison control. Do not rely on a care plan.",
  "sources": [],
  "status": "guarded"
}
```

The current `tests/test_ai_evaluation.py` cases also check that a mocked proposal receives a Scheduler budget result, that a 3-minute budget can reject a proposed 5-minute task, and that the original owner has no new tasks after a proposal. The live [comparison record](ai_live_comparison.json) contains the observed three-task plan, each `budget_result`, and the `Present for review` trace step. That record is from a previous real API run; it was not regenerated here. The comparison script can be rerun with `python -m ai.compare` when a key and network access are available, but doing so would replace the historical JSON record, so this recheck did not run it.

### Submission checks and limits

`git diff --check` exited 0. A scan for Google-style API keys and long token assignments in the submission documentation and architecture file found no matches. Mermaid 11.12.0 parsed the earlier architecture file as recorded above; a local Mermaid parser was not available to reparse this edit. The Mermaid source remains a standard `flowchart LR` with an explicit human-review loop. A read-only GitHub repository metadata lookup reported `visibility: public` and `default_branch: main` for `sudinkatuwal7/ai110-module2show-pawpal-starter`. Manual browser accessibility and pushing final commits to `main` require separate checks. The current local checkout is `feature/applied-ai-pawpal`; local `main` and the `origin/main` tracking ref point to the earlier bonus-feature commit.
