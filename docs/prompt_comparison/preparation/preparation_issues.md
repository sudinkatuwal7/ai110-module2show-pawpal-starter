# Preparation issues and resolutions

No unresolved preparation blocker remains as of the verification report.

## Git metadata permissions

The initial sandboxed worktree creation failed with:

```text
Preparing worktree (new branch 'experiment/prompt-a')
fatal: cannot lock ref 'refs/heads/experiment/prompt-a': unable to create directory for .git/refs/heads/experiment/prompt-a
```

The approved elevated retry created `experiment/prompt-a` at the requested
baseline. The second approved worktree command created `experiment/prompt-b`
at the same baseline. No commit, merge, push, or main-branch checkout occurred.

Exact creation commands (successful retries):

```powershell
git worktree add -b experiment/prompt-a <USER_HOME>/AppData/Local/Temp/pawpal-prompt-comparison-9880594/prompt-a 98805949bffcb69f5e5299a4deaafe6b8bdb3623
git worktree add -b experiment/prompt-b <USER_HOME>/AppData/Local/Temp/pawpal-prompt-comparison-9880594/prompt-b 98805949bffcb69f5e5299a4deaafe6b8bdb3623
```

Both returned exit 0 and:

```text
HEAD is now at 9880594 docs: finalize PawPal+ UI, UML, README, and reflection
```

## Ownership check

The first sandboxed preparation-script attempt could read the original repository
but failed on `git rev-parse HEAD` in prompt-a with exit 128:

```text
fatal: detected dubious ownership in repository at '<USER_HOME>/AppData/Local/Temp/pawpal-prompt-comparison-9880594/prompt-a'
```

The worktree's `.git` link was owned by the normal user, while the sandbox process
used its separate account. The approved retry under the normal user completed
the preparation checks. No global `safe.directory` setting was changed. Future
sandbox Git checks may need the same approved execution context. Running the
recorded commands from the normal user's terminal avoids that account mismatch.

## Line endings

Eight tracked text files have different byte hashes between the original working
copy and freshly checked-out worktrees. Every difference was verified to be CRLF
versus LF only. Both candidate working copies match each other byte-for-byte and
have no tracked Git diff from the baseline. Details are in
`checkout_line_endings.json`; original and candidate byte hashes are both retained.

## Specification wording

The earlier acceptance criteria called the list "seven fields" but named six
editable attributes. The shared specification retains the acceptance criterion
and explicitly clarifies six editable attributes plus one task-selection control.
No extra backend attribute or different requirement was introduced for either run.

## Not yet verified

The new tests have been compiled and collected, not executed against an editor.
Neither candidate has started. Model/version and reasoning settings must be
recorded consistently before their authorized runs. No browser review, candidate
score, or winner has been recorded.
