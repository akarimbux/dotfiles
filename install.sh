#!/usr/bin/env bash
# Usage: ./install.sh [--with-tools]
set -euo pipefail

repo_dir=$(cd "$(dirname "$0")" && pwd)
target=${ZDOTDIR:-$HOME}/.zshrc

if [[ ${1:-} == --with-tools ]]; then
  packages=(zsh git fzf zoxide eza jq zsh-autosuggestions zsh-syntax-highlighting)
  if command -v brew >/dev/null; then
    brew install "${packages[@]}" uv
  elif command -v apt-get >/dev/null; then
    sudo apt-get update
    for pkg in "${packages[@]}"; do
      apt-cache show "$pkg" >/dev/null 2>&1 && sudo apt-get install -y "$pkg" || echo "Skipping $pkg"
    done
    command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | UV_NO_MODIFY_PATH=1 sh
  else
    echo "No brew or apt-get found; install tools manually." >&2
  fi
fi

if [[ -e $target && ! -L $target ]]; then
  mv "$target" "$target.backup"
  echo "Backed up existing config to $target.backup"
fi
ln -sfn "$repo_dir/configs/.zshrc" "$target"
echo "Linked $target. Run: exec zsh"
