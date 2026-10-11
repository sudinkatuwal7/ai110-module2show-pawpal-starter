"""Preserve local candidate evidence before evaluation; never edit candidates."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime

DEST = Path(__file__).resolve().parent
MAIN = DEST.parents[1]
ARCHIVE = Path(r"<USER_HOME>\AppData\Local\Temp\pawpal-prompt-comparison-9880594")
SESSIONS = Path(r"<USER_HOME>\.codex\sessions\2026\10\11")
BASE = "98805949bffcb69f5e5299a4deaafe6b8bdb3623"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(root, *args):
    result = subprocess.run(["git", "-c", f"safe.directory={root.as_posix()}", *args],
                            cwd=root, capture_output=True, check=True)
    return result.stdout


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    original = DEST / "original"
    original.mkdir(exist_ok=False)
    shutil.copytree(ARCHIVE / "preparation", DEST / "preparation")
    # Preserve bytes but avoid adding an executable test to main's discovery.
    (DEST / 'preparation/test_pending_task_editing.py').rename(
        DEST / 'preparation/test_pending_task_editing.py.txt')
    manifest = json.loads((ARCHIVE / "preparation/baseline_manifest.json").read_text())
    environment = {
        "captured_at": datetime.now().astimezone().isoformat(),
        "python_executable": sys.executable, "python_version": sys.version,
        "dependencies": dict(sorted((d.metadata['Name'], d.version)
                                    for d in importlib.metadata.distributions() if d.metadata['Name'])),
        "environment_overrides": {"PYTHONDONTWRITEBYTECODE": "1"},
        "main_head": git(MAIN, "rev-parse", "HEAD").decode().strip(),
        "main_status_before_documentation": "Clean, independently observed before creating docs.",
        "main_initial_hashes": {name: digest(MAIN / name)
                                for name in manifest['original_tracked_sha256']},
        "candidate_order": ["a", "b"], "candidate_sessions": {},
    }
    sessions = {
        "a": ("rollout-2026-10-11T15-47-52-01a12cb8-d320-75c0-9d0e-7e1a584a5d57.jsonl", 792),
        "b": ("rollout-2026-10-11T17-06-54-01a12d01-2cdc-7a83-80e7-9deecd96436b.jsonl", 9),
    }
    for candidate, (session_name, first_line) in sessions.items():
        root = ARCHIVE / f"prompt-{candidate}"
        folder = original / candidate
        folder.mkdir()
        shutil.copyfile(root / "app.py", folder / "app.py")
        (folder / "app.patch").write_bytes(git(root, "diff", "--binary", BASE, "--", "app.py"))
        (folder / "git-status.txt").write_bytes(git(root, "status", "--short", "--branch"))
        (folder / "diff-stat.txt").write_bytes(git(root, "diff", "--stat", BASE))
        (folder / "diff-numstat.txt").write_bytes(git(root, "diff", "--numstat", BASE))
        hashes = {name: digest(root / name) for name in manifest['candidates'][candidate]['starting_sha256']}
        write_json(folder / "file-hashes.json", hashes)
        protected = {name: hashes[name] == expected for name, expected in
                     manifest['candidates'][candidate]['starting_sha256'].items() if name != 'app.py'}
        assert all(protected.values()), protected
        path = SESSIONS / session_name
        lines = path.read_bytes().splitlines(keepends=True)
        records = [json.loads(line) for line in lines]
        # Keep original visible records verbatim, excluding system/developer messages
        # and internal reasoning. This is an excerpt, not a reconstructed dialogue.
        end = len(records)
        for index in range(first_line, len(records)):
            p = records[index].get('payload', {})
            if p.get('type') == 'message' and p.get('role') == 'user':
                end = index
                break
        selected, locations, results, finals = [], [], [], []
        for index in range(first_line - 1, end):
            obj = records[index]
            p = obj.get('payload', {})
            visible_message = p.get('type') == 'message' and (
                p.get('role') == 'user' or
                (p.get('role') == 'assistant' and p.get('phase') in ('commentary', 'final_answer')))
            tool_record = p.get('type') in ('function_call', 'function_call_output', 'custom_tool_call', 'custom_tool_call_output')
            if obj.get('type') == 'response_item' and (visible_message or tool_record):
                selected.append(lines[index]); locations.append(index + 1)
                if tool_record and 'output' in p:
                    results.append({'source_line': index + 1, 'timestamp': obj.get('timestamp'),
                                    'call_id': p.get('call_id'), 'output': p['output']})
                if visible_message and p.get('phase') == 'final_answer':
                    finals.append('\n'.join(c.get('text', '') for c in p.get('content', [])))
        (folder / 'transcript.visible.jsonl').write_bytes(b''.join(selected))
        write_json(folder / 'tool-results.json', results)
        (folder / 'final-response.md').write_text('\n\n'.join(finals) + '\n', encoding='utf-8')
        contexts = [r['payload'] for r in records[:first_line] if r.get('type') == 'turn_context']
        context = contexts[-1]
        prior_users = []
        for index, record in enumerate(records[:first_line - 1]):
            p = record.get('payload', {})
            if p.get('type') == 'message' and p.get('role') == 'user':
                txt = '\n'.join(c.get('text', '') for c in p.get('content', []))
                if not txt.startswith('<environment_context>'):
                    prior_users.append({'source_line': index + 1, 'timestamp': record.get('timestamp'),
                                        'message': txt})
        provenance = {
            'source_path': str(path), 'source_snapshot_sha256': hashlib.sha256(b''.join(lines)).hexdigest(),
            'source_snapshot_bytes': sum(map(len, lines)),
            'candidate_first_line': first_line, 'candidate_last_line': end,
            'preserved_source_lines': locations,
            'extraction': 'Verbatim visible response_item JSONL records; excludes internal reasoning, system/developer messages, and evaluation turn.',
            'session_id': records[0]['payload'].get('id'),
            'session_started': records[0]['payload'].get('timestamp'),
            'cli_version': records[0]['payload'].get('cli_version'),
            'forked_from_id': records[0]['payload'].get('forked_from_id'),
            'candidate_context': {k: context.get(k) for k in ('model', 'effort', 'cwd', 'approval_policy', 'sandbox_policy')},
            'first_request_at': records[first_line-1].get('timestamp'),
            'prior_task_requests': prior_users,
            'protected_hash_matches': protected,
        }
        write_json(folder / 'provenance.json', provenance)
        environment['candidate_sessions'][candidate] = provenance['candidate_context']
    write_json(DEST / 'environment.json', environment)
    files = {str(p.relative_to(DEST)).replace('\\', '/'): digest(p)
             for directory in (original, DEST / 'preparation') for p in sorted(directory.rglob('*')) if p.is_file()}
    write_json(DEST / 'evidence-sha256.json', files)
    print('Preserved both candidate snapshots, diffs, visible transcripts, original tool results, preparation and environment.')


if __name__ == '__main__':
    main()
