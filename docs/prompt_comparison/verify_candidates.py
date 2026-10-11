"""Run the frozen checks sequentially against unchanged candidates."""
from datetime import date, datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

DEST = Path(__file__).resolve().parent
ARCHIVE = Path(r"<USER_HOME>\AppData\Local\Temp\pawpal-prompt-comparison-9880594")
PYTHON = json.loads((DEST / 'preparation/environment.json').read_text())['python_executable']


def hashes(root, names):
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}


def main():
    out = DEST / 'evaluator-reruns'
    out.mkdir(exist_ok=False)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    records = []
    initial_date = date.today()
    for candidate in ('a', 'b'):
        root = ARCHIVE / f'prompt-{candidate}'
        folder = out / candidate
        folder.mkdir()
        frozen = json.loads((DEST / f'original/{candidate}/file-hashes.json').read_text())
        assert hashes(root, frozen) == frozen, 'Candidate changed since evidence capture'
        git = ['git', '-c', f'safe.directory={root.as_posix()}']
        commands = [
            ('baseline', [PYTHON, '-m', 'pytest', 'tests/test_pawpal.py', '-p', 'no:cacheprovider']),
            ('acceptance', [PYTHON, '-m', 'pytest', 'tests/test_pending_task_editing.py', '-p', 'no:cacheprovider']),
            ('combined', [PYTHON, '-m', 'pytest', '-p', 'no:cacheprovider']),
            ('demo', [PYTHON, 'main.py']),
            ('syntax', [PYTHON, '-c', "from pathlib import Path; compile(Path('app.py').read_text(encoding='utf-8'), 'app.py', 'exec'); print('app.py syntax OK')"]),
            ('diff-check', git + ['diff', '--check']),
            ('diff-stat', git + ['diff', '--stat']),
            ('status', git + ['status', '--short']),
        ]
        for label, argv in commands:
            started = datetime.now().astimezone().isoformat()
            tick = time.monotonic()
            result = subprocess.run(argv, cwd=root, env=env, capture_output=True)
            elapsed = time.monotonic() - tick
            stdout = folder / f'{label}.stdout.txt'
            stderr = folder / f'{label}.stderr.txt'
            stdout.write_bytes(result.stdout)
            stderr.write_bytes(result.stderr)
            records.append({'candidate': candidate, 'label': label, 'cwd': str(root),
                            'argv': argv, 'environment_overrides': {'PYTHONDONTWRITEBYTECODE': '1'},
                            'started_at': started, 'elapsed_seconds': elapsed,
                            'local_test_date': str(date.today()), 'exit_code': result.returncode,
                            'stdout': str(stdout.relative_to(DEST)), 'stderr': str(stderr.relative_to(DEST))})
            (out / 'commands.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
            print(candidate.upper(), label, 'exit', result.returncode, f'{elapsed:.2f}s', flush=True)
            if label in ('baseline', 'acceptance', 'combined'):
                print(result.stdout.decode('utf-8', errors='replace').splitlines()[-1], flush=True)
        assert hashes(root, frozen) == frozen, 'Verification changed candidate files'
        assert date.today() == initial_date, 'Local midnight crossed; both candidates need matched reruns'
    print('Both candidate hashes unchanged; all checks used local date', initial_date, flush=True)


if __name__ == '__main__':
    main()
