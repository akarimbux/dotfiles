#!/usr/bin/env bash
# Validate the checkout without changing your shell or installing packages.
set -euo pipefail
repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
for tool in bash zsh git uv; do
  command -v "$tool" >/dev/null 2>&1 || { printf 'Missing required tool: %s\n' "$tool" >&2; exit 1; }
done
check_dir=$(mktemp -d "${TMPDIR:-/tmp}/dotfiles-check.XXXXXXXX")
trap 'rm -rf -- "$check_dir"' EXIT
mkdir -p "$check_dir/home"
sandbox=(env -i PATH="$PATH" HOME="$check_dir/home" ZDOTDIR="$check_dir/home"
  TMPDIR="$check_dir" TERM="${TERM:-dumb}" UV_CACHE_DIR="$check_dir/cache"
  UV_PYTHON_DOWNLOADS=never UV_NO_CONFIG=1 skip_global_compinit=1)

printf 'Checking shell syntax...\n'
bash -n "$repo_dir/install.sh"
bash -n "$repo_dir/configs/dothelp.sh"
bash -n "$repo_dir/check.sh"
zsh -n "$repo_dir/configs/.zshrc"
printf 'Running focused tests through uv...\n'
"${sandbox[@]}" uv run --no-project --no-managed-python python -m unittest discover -s "$repo_dir/tests"
printf 'Checking fresh installation and shell startup...\n'
"${sandbox[@]}" bash "$repo_dir/install.sh"
"${sandbox[@]}" zsh -ic 'dothelp python' > "$check_dir/topic.md" 2> "$check_dir/startup.log"
cat "$check_dir/startup.log"
[[ ! -s "$check_dir/startup.log" ]]
[[ $(<"$check_dir/topic.md") == *'## Python without the fuss'* ]]
if command -v glow >/dev/null 2>&1; then
  "${sandbox[@]}" glow -s dark "$check_dir/topic.md" > "$check_dir/rendered.txt"
  [[ -s "$check_dir/rendered.txt" ]]
else
  printf 'Glow not installed; plain Markdown help checked.\n'
fi
if command -v fzf >/dev/null 2>&1; then
  "${sandbox[@]}" fzf --version
else
  printf 'fzf not installed; full-guide fallback remains available.\n'
fi
printf 'Checking a native uv project...\n'
"${sandbox[@]}" uv init --bare --no-managed-python "$check_dir/uv project"
cd "$check_dir/uv project"
"${sandbox[@]}" uv run --no-managed-python python -c 'print("uv run works")'
"${sandbox[@]}" uv sync --locked --no-managed-python
printf 'Checking repeated installation...\n'
"${sandbox[@]}" bash "$repo_dir/install.sh"
printf '\nAll checks passed.\n'
