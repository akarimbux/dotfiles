#!/usr/bin/env bash
# Usage: ./install.sh [--with-tools]
set -euo pipefail

repo_dir=$(cd "$(dirname "$0")" && pwd)

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

link() {
  mkdir -p "$(dirname "$2")"
  if [[ -e $2 && ! -L $2 ]]; then
    mv "$2" "$2.backup" && echo "Backed up $2 to $2.backup"
  fi
  ln -sfn "$repo_dir/configs/$1" "$2" && echo "Linked $2"
}

config=${XDG_CONFIG_HOME:-$HOME/.config}
link .zshrc "${ZDOTDIR:-$HOME}/.zshrc"
link gitconfig "$config/git/config"
link uv.toml "$config/uv/uv.toml"
touch ~/.gitconfig  # so `git config --global` writes here, not into this repo
echo "Run: exec zsh"
