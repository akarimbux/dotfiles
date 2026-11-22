# dotfiles

My Zsh config.

## Install

```sh
git clone https://github.com/akarimbux/dotfiles.git ~/.dotfiles
cd ~/.dotfiles
./install.sh --with-tools   # or just ./install.sh to link the config only
exec zsh
```

`install.sh` symlinks `configs/.zshrc` to `~/.zshrc`, moving any existing file
to `~/.zshrc.backup`. `--with-tools` also installs zsh, git, eza, jq, fzf,
zoxide, uv and the autosuggestions/syntax-highlighting plugins using Homebrew
(macOS) or apt (Debian/Ubuntu).

## What's included

- Prompt showing the active Python env, current directory, and Git branch/status
- History shared across terminals, prefix search with the arrow keys
- fzf, zoxide, autosuggestions and syntax highlighting when installed
- Aliases: `ll`, `la`, `..`, `cls`, and `e`/`el`/`ea`/`et` for eza
- `venv [version]`: create `.venv` with uv if missing, then activate it

Machine-specific settings go in `~/.zshrc.local`, aliases in `~/.zsh_aliases`.
