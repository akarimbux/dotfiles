#!/usr/bin/env bash
set -euo pipefail

if [[ ${1:-} == --help || ${1:-} == -h ]]; then
  printf 'Usage: dothelp [topic | --all]\n'
  exit 0
fi
guide=${DOTFILES_MANUAL:-"$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)/README.md"}
if [[ ! -r $guide ]]; then
  printf 'Setup guide not found: %s\n' "$guide" >&2
  exit 1
fi
query="$*"
case "$query" in
  shortcuts) query='At your fingertips' ;;
  prompt) query='Know where you stand' ;;
esac
# Read topics from the guide, ignoring headings inside code examples.
topics=$(awk '/^```/ { fence = !fence } !fence && /^## / { print substr($0, 4) }' "$guide")
if [[ -z $query && -t 0 && -t 1 ]] && command -v fzf >/dev/null 2>&1; then
  if query=$(printf '%s\n' "$topics" | fzf --height=70% --layout=reverse --prompt='dothelp › '); then
    :
  else
    result=$?
    [[ $result == 1 || $result == 130 ]] && exit 0
    exit "$result"
  fi
fi
page=$guide
if [[ -n $query && $query != --all ]]; then
  topic=$(printf '%s\n' "$topics" | awk -v q="$query" 'index(tolower($0), tolower(q))')
  if [[ -z $topic || $topic == *$'\n'* ]]; then
    printf 'Choose a more specific topic:\n%s\n' "$topics" >&2
    exit 2
  fi
  page=$(mktemp "${TMPDIR:-/tmp}/dothelp.XXXXXXXX")
  trap 'rm -f -- "$page"' EXIT
  awk -v heading="$topic" '
    /^```/ { fence = !fence }
    !fence && /^## / { if (printing) exit; printing = substr($0, 4) == heading }
    printing { print }
  ' "$guide" > "$page"
fi
if [[ -t 1 ]] && command -v glow >/dev/null 2>&1; then
  command glow -p "$page"
elif [[ -t 1 ]] && command -v less >/dev/null 2>&1; then
  command less "$page"
else
  command cat -- "$page"
fi
