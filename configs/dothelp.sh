#!/usr/bin/env bash
# Browse the Markdown guide without requiring a renderer or fuzzy finder.
set -euo pipefail

guide=${DOTFILES_MANUAL:-"$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)/REFERENCE.md"}
usage() {
  cat <<'HELP'
Usage: dothelp [topic | --all | --list | --help]

Browse topics interactively, or jump straight to one:
  dothelp python       Python environments and uv
  dothelp shortcuts    Keyboard shortcuts and everyday commands
  dothelp prompt       Understand your prompt
  dothelp install      Installation and updates
  dothelp customize    Personal settings
  dothelp recovery     Restore your previous configuration
  dothelp --all        Read the complete guide
  dothelp --list       List available topics

Type in the fzf menu to search, Enter to open, or Esc to cancel.
Without fzf, select a number or type part of a topic name.
HELP
}
if [[ ${1:-} == --help || ${1:-} == -h ]]; then usage; exit 0; fi
if [[ ! -r $guide ]]; then
  printf 'Setup guide not found: %s\n' "$guide" >&2
  exit 1
fi
if [[ ${1:-} == --* && $1 != --all && $1 != --list ]]; then
  usage >&2
  exit 2
fi

# Only top-level sections outside fenced examples are navigation entries.
topics=$(awk '/^```/ { fence = !fence } !fence && /^## / { print substr($0, 4) }' "$guide")
if [[ ${1:-} == --list ]]; then printf '%s\n' "$topics"; exit 0; fi
query="$*"
if [[ -z $query && -t 0 && -t 1 ]]; then
  if command -v fzf >/dev/null 2>&1; then
    if query=$(printf '%s\n' "$topics" | fzf --height=70% --layout=reverse \
      --border --prompt='dothelp › ' --header='Search topics · Enter open · Esc back'); then
      :
    else
      result=$?
      [[ $result == 1 || $result == 130 ]] && exit 0
      exit "$result"
    fi
  else
    printf '\n  dothelp — your terminal guide\n\n'
    printf '%s\n' "$topics" | awk '{ printf "  %2d  %s\n", NR, $0 }'
    printf '\nChoose a number or search a topic (Enter to cancel): '
    IFS= read -r query || exit 0
    [[ -n $query ]] || exit 0
    if [[ $query =~ ^[0-9]+$ ]]; then
      query=$(printf '%s\n' "$topics" | awk -v n="$query" 'NR == n')
      if [[ -z $query ]]; then printf 'No topic with that number.\n' >&2; exit 2; fi
    fi
  fi
fi

# With redirected input/output, the default is a readable, complete guide.
if [[ -z $query || $query == --all ]]; then
  section=''
else
  case "$query" in
    python|venv|uv) query='Python without the fuss' ;;
    shortcuts|keys|commands) query='At your fingertips' ;;
    prompt|git) query='Know where you stand' ;;
    install|setup) query='Get started' ;;
    customize|aliases) query='Make it yours' ;;
    update|updates) query='Keep it fresh' ;;
    recovery|restore) query='A way back' ;;
  esac
  section=$(printf '%s\n' "$topics" | awk -v q="$query" 'index(tolower($0), tolower(q))')
  if [[ -z $section ]]; then
    printf 'No topic matches "%s". Try dothelp --list.\n' "$query" >&2
    exit 2
  fi
  if [[ $section == *$'\n'* ]]; then
    printf 'More than one topic matches "%s":\n%s\nUse a more specific topic.\n' "$query" "$section" >&2
    exit 2
  fi
fi

# Render a temporary Markdown file so Glow can page a single section.
page=$(mktemp "${TMPDIR:-/tmp}/dothelp.XXXXXXXX.md")
trap 'rm -f -- "$page"' EXIT
if [[ -z $section ]]; then
  cat -- "$guide" > "$page"
else
  awk -v heading="$section" '
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
