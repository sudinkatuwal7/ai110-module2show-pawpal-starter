"""Prepare evidence and identical test inputs; never run a candidate agent."""

from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


PREP = Path(__file__).resolve().parent
ROOT = PREP.parent
MAIN = Path(r"<USER_HOME>\Downloads\ai110-module2show-pawpal-starter-main\ai110-module2show-pawpal-starter")
BASELINE = "98805949bffcb69f5e5299a4deaafe6b8bdb3623"
CANDIDATES = {"a": ROOT / "prompt-a", "b": ROOT / "prompt-b"}
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
COMMANDS = []


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name, value):
    (PREP / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def command(label, args, cwd=MAIN):
    """Capture exact subprocess output and exit status outside every worktree."""
    result = subprocess.run(args, cwd=cwd, env=ENV, capture_output=True)
    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    log_dir = PREP / "logs"
    log_dir.mkdir(exist_ok=True)
    (log_dir / f"{label}.stdout.txt").write_bytes(result.stdout)
    (log_dir / f"{label}.stderr.txt").write_bytes(result.stderr)
    COMMANDS.append({
        "label": label, "cwd": str(cwd), "argv": [str(arg) for arg in args],
        "environment_overrides": {"PYTHONDONTWRITEBYTECODE": "1"},
        "exit_code": result.returncode,
        "stdout": str(log_dir / f"{label}.stdout.txt"),
        "stderr": str(log_dir / f"{label}.stderr.txt"),
    })
    write_json("commands.json", COMMANDS)
    if result.returncode:
        raise RuntimeError(f"{label}: exit {result.returncode}\n{stdout}\n{stderr}")
    return stdout


def main():
    """Create frozen inputs and record preparation-only verification."""
    assert not (PREP / "frozen_manifest.json").exists(), "Already frozen; do not overwrite an experiment"
    assert command("main-head", ["git", "rev-parse", "HEAD"]).strip() == BASELINE
    assert command("main-branch", ["git", "branch", "--show-current"]).strip() == "main"
    assert command("main-status-before", ["git", "status", "--porcelain=v1"]) == ""
    tracked = command("tracked-paths", ["git", "ls-files"]).splitlines()
    original_hashes = {name: digest(MAIN / name) for name in tracked}
    baseline_output = command(
        "baseline-pytest", [sys.executable, "-m", "pytest", "tests/test_pawpal.py", "-p", "no:cacheprovider"]
    )
    assert "97 passed" in baseline_output
    print(baseline_output.strip())

    environment = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "local_test_date": datetime.now().date().isoformat(),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "dependencies": dict(sorted(
            (dist.metadata["Name"], dist.version)
            for dist in importlib.metadata.distributions() if dist.metadata["Name"]
        )),
        "candidate_model": "NOT RECORDED: no candidate session has started",
        "candidate_reasoning_setting": "NOT RECORDED: select the same setting before either run",
        "candidate_order": ["A", "B"],
        "candidate_status": {"A": "NOT RUN", "B": "NOT RUN"},
        "package_installations": "NONE",
    }
    write_json("environment.json", environment)

    test_source = PREP / "test_pending_task_editing.py"
    compile(test_source.read_text(encoding="utf-8"), str(test_source), "exec")
    spec = (PREP / "shared_spec.md").read_text(encoding="utf-8")
    tests = test_source.read_text(encoding="utf-8")
    common = (
        "# PawPal+ pending-task editor: controlled prompt comparison\n\n"
        "Execute only in the candidate worktree assigned to this fresh session. "
        "Do not start until the user authorizes this candidate run.\n\n"
        "The complete shared specification follows, then the exact frozen acceptance test. "
        "Do not modify either. Only app.py may change.\n\n"
        + spec
        + "\n## Frozen acceptance tests: tests/test_pending_task_editing.py\n\n```python\n"
        + tests + "```\n\n## Strategy instruction\n\n"
    )
    endings = {
        "a": "Implement the feature now according to the shared specification. Run the required checks and report the completed changes and results.\n",
        "b": "Work in stages. First inspect the relevant code and provide a brief implementation plan identifying selection, validation, and session-state risks. Then implement the feature, run the required checks, and review the result against the acceptance criteria. Report the completed changes and results.\n",
    }
    for key, ending in endings.items():
        (PREP / f"prompt_{key}.txt").write_text(common + ending, encoding="utf-8")
    assert (PREP / "prompt_a.txt").read_text(encoding="utf-8").split("## Strategy instruction\n\n")[0] == (
        PREP / "prompt_b.txt"
    ).read_text(encoding="utf-8").split("## Strategy instruction\n\n")[0]

    baseline = {
        "commit": BASELINE, "original_repository": str(MAIN),
        "original_tracked_sha256": original_hashes,
        "candidates": {}, "acceptance_test_sha256": digest(test_source),
        "common_prompt_prefix_sha256": hashlib.sha256(common.encode("utf-8")).hexdigest(),
    }
    for key, path in CANDIDATES.items():
        assert command(f"{key}-head", ["git", "rev-parse", "HEAD"], path).strip() == BASELINE
        branch = command(f"{key}-branch", ["git", "branch", "--show-current"], path).strip()
        assert branch == f"experiment/prompt-{key}"
        assert command(f"{key}-status-before", ["git", "status", "--porcelain=v1"], path) == ""
        shutil.copyfile(test_source, path / "tests" / test_source.name)
        hashes = {name: digest(path / name) for name in tracked}
        hashes[f"tests/{test_source.name}"] = digest(path / "tests" / test_source.name)
        baseline["candidates"][key] = {"path": str(path), "branch": branch, "starting_sha256": hashes}
        output = command(f"{key}-baseline-pytest", [
            sys.executable, "-m", "pytest", "tests/test_pawpal.py", "-p", "no:cacheprovider"
        ], path)
        assert "97 passed" in output
        collected = command(f"{key}-acceptance-collection", [
            sys.executable, "-m", "pytest", "tests/test_pending_task_editing.py", "--collect-only", "-q", "-p", "no:cacheprovider"
        ], path)
        print(f"Candidate {key.upper()}: baseline 97 passed; {collected.strip().splitlines()[-1]}")
        command(f"{key}-diff-check", ["git", "diff", "--check"], path)
        assert command(f"{key}-tracked-diff", ["git", "diff", "--name-only", BASELINE], path) == ""
        assert command(f"{key}-status-after", ["git", "status", "--porcelain=v1"], path).strip() == "?? tests/test_pending_task_editing.py"

    assert baseline["candidates"]["a"]["starting_sha256"] == baseline["candidates"]["b"]["starting_sha256"]
    baseline["original_vs_checkout_byte_differences"] = [
        name for name in tracked if original_hashes[name] != baseline["candidates"]["a"]["starting_sha256"][name]
    ]
    write_json("baseline_manifest.json", baseline)
    command("worktrees", ["git", "worktree", "list", "--porcelain"])
    command("main-diff-check", ["git", "diff", "--check"])
    assert command("main-status-after", ["git", "status", "--porcelain=v1"]) == ""
    assert {name: digest(MAIN / name) for name in tracked} == original_hashes
    print("Candidate tracked files and supplied tests match byte-for-byte.")
    print("Original repository remains clean with all tracked hashes unchanged.")
    print("No candidate implementation or acceptance-test execution was started.")


if __name__ == "__main__":
    main()
