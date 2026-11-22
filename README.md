# dotfiles

Portable Zsh, Git and uv setup for a new machine.

```sh
git clone https://github.com/akarimbux/dotfiles.git ~/.dotfiles
~/.dotfiles/install.sh --with-tools
```

Symlinks each file in `configs/` into place (existing files are moved to `*.backup`):

| File | Linked to |
| :--- | :--- |
| `.zshrc` | `~/.zshrc` |
| `gitconfig` | `~/.config/git/config` |
| `uv.toml` | `~/.config/uv/uv.toml` |

`--with-tools` installs zsh, git, fzf, zoxide, eza, jq, uv and Zsh plugins via Homebrew or apt.

Machine-specific settings go in `~/.zshrc.local` and `~/.gitconfig` (name, email).
