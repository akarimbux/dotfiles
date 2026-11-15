#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bash install.sh [--with-tools] [--dry-run]

Link configs/.zshrc into ${ZDOTDIR:-$HOME}, backing up any existing file.
  --with-tools  Install zsh, git, eza, jq, fzf, zoxide, uv and two Zsh plugins.
                Uses Homebrew (macOS), or apt plus uv's installer (Linux).
  --dry-run     Print planned changes without writing files or installing tools.
  -h, --help    Show this help.

Local settings (.zshrc.local) and aliases (.zsh_aliases) are left untouched.
EOF
}

dry_run=false
with_tools=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) dry_run=true ;;
    --with-tools) with_tools=true ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$arg" >&2; usage >&2; exit 2 ;;
  esac
done

repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
source_file="$repo_dir/configs/.zshrc"
target_dir=${ZDOTDIR:-$HOME}
target_file="$target_dir/.zshrc"

if [[ ! -f "$source_file" ]]; then
  printf 'Missing %s. Run the installer from a complete repository checkout.\n' "$source_file" >&2
  exit 1
fi
if [[ -d $target_dir && "$(cd -- "$target_dir" && pwd -P)" == "$repo_dir/configs" ]]; then
  printf 'Refusing to replace the source config in %s.\n' "$target_dir" >&2
  exit 1
fi
if [[ -d "$target_file" ]]; then
  printf 'Refusing to replace a directory: %s\n' "$target_file" >&2
  exit 1
fi

run() {
  printf '+'
  printf ' %q' "$@"
  printf '\n'
  if ! $dry_run; then
    "$@"
  fi
}

install_tools() {
  local os package
  local packages=()
  os=$(uname -s)
  case "$os" in
    Darwin)
      if ! command -v brew >/dev/null 2>&1; then
        printf 'Install Homebrew first: https://brew.sh\n' >&2
        return 1
      fi
      run brew install zsh git eza jq fzf zoxide zsh-autosuggestions zsh-syntax-highlighting uv
      ;;
    Linux)
      if ! command -v apt-get >/dev/null 2>&1; then
        printf 'Automatic tool installation supports macOS/Homebrew and Debian/Ubuntu/apt.\nRun without --with-tools and install tools with your package manager.\n' >&2
        return 1
      fi
      if (( EUID != 0 )) && ! command -v sudo >/dev/null 2>&1; then
        printf 'sudo is needed for apt installation. Run without --with-tools to install only the config.\n' >&2
        return 1
      fi
      apt_run update
      for package in zsh git eza jq fzf zoxide zsh-autosuggestions zsh-syntax-highlighting curl ca-certificates; do
        if $dry_run || apt-cache show "$package" >/dev/null 2>&1; then
          packages+=("$package")
        else
          printf 'Skipping unavailable package: %s (optional integrations remain disabled).\n' "$package" >&2
        fi
      done
      if (( ${#packages[@]} )); then
        apt_run install -y "${packages[@]}"
      fi
      install_uv
      ;;
    *)
      printf 'Automatic tool installation is not supported on %s. Run without --with-tools.\n' "$os" >&2
      return 1
      ;;
  esac
}

# A subshell scopes the cleanup trap to this download.
install_uv() (
  local uv_dir=${UV_INSTALL_DIR:-$HOME/.local/bin}
  local download_dir
  if command -v uv >/dev/null 2>&1 || [[ -x "$uv_dir/uv" ]]; then
    printf 'uv is already installed; keeping the existing version.\n'
    return
  fi
  if $dry_run; then
    printf 'Would download https://astral.sh/uv/install.sh and install uv into %s (without editing shell files).\n' "$uv_dir"
    return
  fi
  download_dir=$(mktemp -d "${TMPDIR:-/tmp}/dotfiles-uv.XXXXXXXX")
  trap 'rm -rf -- "$download_dir"' EXIT
  run curl --proto '=https' --tlsv1.2 -LsSf https://astral.sh/uv/install.sh -o "$download_dir/install.sh"
  run env UV_INSTALL_DIR="$uv_dir" UV_NO_MODIFY_PATH=1 sh "$download_dir/install.sh"
)

apt_run() {
  if (( EUID == 0 )); then
    run apt-get "$@"
  else
    run sudo apt-get "$@"
  fi
}

if $with_tools; then
  install_tools
fi

if [[ -L "$target_file" && "$(readlink "$target_file")" == "$source_file" ]]; then
  printf 'Already installed: %s\n' "$target_file"
else
  if [[ -e "$target_file" || -L "$target_file" ]]; then
    if $dry_run; then
      printf 'Would back up %s into a new .zshrc.backup.* directory.\n' "$target_file"
    else
      backup_dir=$(mktemp -d "$target_dir/.zshrc.backup.XXXXXXXX")
      mv -- "$target_file" "$backup_dir/.zshrc"
      printf 'Backup: %s/.zshrc\n' "$backup_dir"
    fi
  fi
  run mkdir -p -- "$target_dir"
  if ! run ln -s -- "$source_file" "$target_file"; then
    if [[ -n ${backup_dir:-} && ! -e "$target_file" && ! -L "$target_file" ]]; then
      mv -- "$backup_dir/.zshrc" "$target_file"
      printf 'Restored original config after link failure.\n' >&2
    fi
    exit 1
  fi
fi

if $dry_run; then
  printf 'Dry run complete; no changes made.\n'
else
  printf 'Installed. Keep this checkout in place; git pull updates the linked config.\n'
  printf 'Open a new Zsh terminal, or run: exec zsh\n'
  if ! command -v zsh >/dev/null 2>&1; then
    printf 'Zsh is not installed yet. Re-run with --with-tools or install it manually.\n'
  fi
fi
