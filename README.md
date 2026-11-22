# dotfiles

Portable Zsh setup for a new machine.

```sh
git clone https://github.com/akarimbux/dotfiles.git ~/.dotfiles
~/.dotfiles/install.sh --with-tools
```

Links `configs/.zshrc` to `~/.zshrc` (existing file moved to `~/.zshrc.backup`).
`--with-tools` installs zsh, git, fzf, zoxide, eza, jq, uv and Zsh plugins via Homebrew or apt.

Machine-specific settings go in `~/.zshrc.local`.
