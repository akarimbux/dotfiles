# Working in this repository

Carry a requested fix through investigation, implementation, validation, and a
reviewable pull request. Treat “can you fix…” as a request to do the work.
Ask a short question only when missing information materially changes the fix;
continue independent work while waiting. Follow the user's latest instructions.

## Repository map

- GitHub: https://github.com/akarimbux/dotfiles
- Default branch: `master`
- `configs/.zshrc`: shell settings, prompt, integrations, `venv`, and `dothelp`.
- `install.sh`: configuration links, backups, and optional tool installation.
- `REFERENCE.md`: styled Markdown guide and the document opened by `dothelp`.
- `README.md`: introduction and installation instructions.
- `tests/`: Python unittest suite for installer and shell behavior.

The former `dotfiles.7` was deliberately removed. Keep the guide in Markdown;
do not recreate a roff manual or require `man` for `dothelp`. Glow provides
optional terminal styling, with `less` and plain-text fallbacks.

## Find the work before asking the user

1. Check the current directory, Git status, and hidden files. Use
   `rg --files --hidden -g '!.git/**'`; normal file searches omit `.zshrc`.
2. If the workspace is empty, use an available GitHub connector to locate this
   repository and inspect its default branch. An empty workspace does not mean
   the user's file is missing from GitHub.
3. Clone into a writable workspace when possible. If shell networking fails,
   use the GitHub connector to inspect files or prepare changes. Request an
   environment permission only when needed; do not retry a rejected action
   unchanged or evade access restrictions.
4. Read the relevant files and existing tests. Search references before renaming
   a file. If ambiguity remains, ask one concrete question based on findings.

## Implement the smallest complete fix

- Inspect local changes before editing; preserve unrelated user work.
- Work on a focused branch from the current default branch. Keep an existing
  dirty checkout intact; use another checkout or worktree when necessary.
- Update callers and documentation together when changing names or behavior.
- Keep optional tools optional. Do not install packages or run `install.sh`
  against the user's real shell configuration just to verify a change.

## Validate

Run the checks relevant to the change from the repository root:

```sh
bash -n install.sh
zsh -n configs/.zshrc
python3 -m unittest discover -s tests
git diff --check
```

Shell tests require Zsh and can be skipped by the suite when it is absent;
report that limitation rather than describing skipped checks as passed.
Shell tests source the configuration and may read personal startup files.
Use a temporary HOME when running them in an environment with personal files.
Preserve PATH and any environment needed by the tests.

Add focused tests when changing meaningful behavior. For documentation-only
changes, check links, paths, and consistency with the implementation; avoid
adding tests that simply assert prose. Do not repeat passing checks unless
new edits or evidence justify it.

## Deliver and follow through

- When GitHub access permits, commit the focused changes to a branch and open
  a PR. Use the available GitHub connector when it supports the needed action.
- Explain the concrete result and relevant validation in the PR description.
- Return the actual PR link and state clearly whether it is open or merged.
- Merge when the user requests it. Recheck the current PR head and checks;
  pass the expected head SHA to the merge operation. Resolve fixable failures
  within scope; do not bypass required checks or branch protections.
- A request to merge one PR does not authorize automatically merging future
  PRs. Honor any explicit standing authorization the user gives later.
- Confirm success from the tool result. Never claim a remote update succeeded
  based only on a local edit or an attempted command.
- If access blocks delivery, keep the completed work available as a local
  change or patch and explain the exact blocker and next step. Do not discard
  useful work or stop at the first failed tool call.

Keep progress updates concise. Lead the final reply with the result, link to
the PR, and mention validation and any material remaining limitation.
