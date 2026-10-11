"""Check the frozen experiment inputs without executing either candidate."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys


PREP = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    return json.loads((PREP / name).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true", help="Create the initial manifest/report once")
    args = parser.parse_args()
    commands = []
    checks = []

    def git(path, *arguments):
        result = subprocess.run(["git", *arguments], cwd=path, capture_output=True)
        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")
        commands.append({
            "cwd": str(path), "argv": ["git", *arguments],
            "exit_code": result.returncode, "stdout": stdout, "stderr": stderr,
        })
        if result.returncode:
            raise RuntimeError(f"Git verification blocked: {stderr}")
        return stdout

    def passed(message):
        checks.append(message)
        print(f"PASS: {message}")

    baseline = load("baseline_manifest.json")
    original = Path(baseline["original_repository"])
    assert git(original, "rev-parse", "HEAD").strip() == baseline["commit"]
    assert git(original, "branch", "--show-current").strip() == "main"
    assert git(original, "status", "--porcelain=v1") == ""
    assert git(original, "diff", "--check") == ""
    for name, expected in baseline["original_tracked_sha256"].items():
        assert digest(original / name) == expected, f"Original file changed: {name}"
    passed("Original main is clean at the baseline; every original tracked hash is unchanged")

    candidate_hashes = []
    for key in ("a", "b"):
        details = baseline["candidates"][key]
        path = Path(details["path"])
        assert git(path, "rev-parse", "HEAD").strip() == baseline["commit"]
        assert git(path, "branch", "--show-current").strip() == details["branch"]
        assert git(path, "diff", "--name-only", baseline["commit"]) == ""
        assert git(path, "diff", "--check") == ""
        assert git(path, "status", "--porcelain=v1").strip() == "?? tests/test_pending_task_editing.py"
        actual = {name: digest(path / name) for name in details["starting_sha256"]}
        assert actual == details["starting_sha256"], f"Candidate {key} changed after preparation"
        assert actual["tests/test_pending_task_editing.py"] == baseline["acceptance_test_sha256"]
        source = path / "tests/test_pending_task_editing.py"
        compile(source.read_text(encoding="utf-8"), str(source), "exec")
        candidate_hashes.append(actual)
        passed(f"Candidate {key.upper()}: baseline HEAD/branch, no tracked changes, supplied test only, hashes and syntax OK")
    assert candidate_hashes[0] == candidate_hashes[1]
    passed(f"Both candidates match byte-for-byte across {len(candidate_hashes[0])} controlled files")

    master = PREP / "test_pending_task_editing.py"
    assert digest(master) == baseline["acceptance_test_sha256"]
    spec = (PREP / "shared_spec.md").read_text(encoding="utf-8")
    for number in range(1, 13):
        assert f"| AC{number} |" in spec
    endings = {
        "a": "Implement the feature now according to the shared specification. Run the required checks and report the completed changes and results.\n",
        "b": "Work in stages. First inspect the relevant code and provide a brief implementation plan identifying selection, validation, and session-state risks. Then implement the feature, run the required checks, and review the result against the acceptance criteria. Report the completed changes and results.\n",
    }
    prefixes = []
    for key, ending in endings.items():
        prompt = (PREP / f"prompt_{key}.txt").read_text(encoding="utf-8")
        assert prompt.endswith(ending)
        prefix = prompt[:-len(ending)]
        assert spec in prefix
        assert master.read_text(encoding="utf-8") in prefix
        assert hashlib.sha256(prefix.encode("utf-8")).hexdigest() == baseline["common_prompt_prefix_sha256"]
        prefixes.append(prefix)
    assert prefixes[0] == prefixes[1]
    passed("Prompts embed the same 12-criterion specification and full tests; only strategy endings differ")

    collected = []
    for key in ("a", "b"):
        text = (PREP / "logs" / f"{key}-acceptance-collection.stdout.txt").read_text(encoding="utf-8")
        ids = [line for line in text.splitlines() if line.startswith("tests/test_pending_task_editing.py::")]
        assert len(ids) == 19
        collected.append(ids)
        assert "97 passed" in (PREP / "logs" / f"{key}-baseline-pytest.stdout.txt").read_text(encoding="utf-8")
    assert collected[0] == collected[1]
    assert "97 passed" in (PREP / "logs" / "baseline-pytest.stdout.txt").read_text(encoding="utf-8")
    assert all(item["exit_code"] == 0 for item in load("commands.json"))
    passed("Recorded checks: main/A/B baseline each 97 passed; A/B collected the same 19 acceptance cases")

    line_endings = load("checkout_line_endings.json")
    candidate_a = Path(baseline["candidates"]["a"]["path"])
    for name in baseline["original_vs_checkout_byte_differences"]:
        assert line_endings[name]["equal_after_CRLF_normalization"]
        assert (original / name).read_bytes().replace(b"\r\n", b"\n") == (candidate_a / name).read_bytes().replace(b"\r\n", b"\n")
    passed("Original versus checkout byte differences are verified line endings only")

    manifest_path = PREP / "frozen_manifest.json"
    excluded = {"frozen_manifest.json", "verification_report.json"}
    if args.freeze:
        assert not manifest_path.exists(), "Already frozen; run without --freeze"
        files = {
            path.relative_to(PREP).as_posix(): digest(path)
            for path in sorted(PREP.rglob("*"))
            if path.is_file() and path.relative_to(PREP).as_posix() not in excluded
        }
        manifest_path.write_text(json.dumps({
            "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
            "algorithm": "SHA-256", "files": files,
        }, indent=2) + "\n", encoding="utf-8")
    frozen = load("frozen_manifest.json")
    for name, expected in frozen["files"].items():
        assert digest(PREP / name) == expected, f"Frozen preparation artifact changed: {name}"
    passed(f"Frozen archive hashes verified for {len(frozen['files'])} artifacts")
    passed("Candidate implementation and acceptance execution remain NOT RUN during preparation")
    if args.freeze:
        (PREP / "verification_report.json").write_text(json.dumps({
            "verified_at_utc": datetime.now(timezone.utc).isoformat(),
            "invocation": [sys.executable, str(Path(__file__).resolve()), "--freeze"],
            "checks": checks, "git_commands": commands,
            "candidate_implementation_status": {"A": "NOT RUN", "B": "NOT RUN"},
            "acceptance_execution_status": "NOT RUN; syntax and collection only",
            "unresolved_preparation_blockers": [],
        }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
