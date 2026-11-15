# My terminal setup

A small Zsh setup with searchable history, directory jumps, readable listings,
a Python environment helper, and a Git prompt.

## Install

Git and Bash are required. For automatic tool installation, use
[Homebrew](https://brew.sh) on macOS or apt on Debian/Ubuntu.

```sh
git clone https://github.com/akarimbux/dotfiles.git "$HOME/.dotfiles"
cd "$HOME/.dotfiles"
bash install.sh --with-tools
exec zsh
```

The installer backs up your existing `.zshrc` and links the config from this
checkout. Keep the checkout in place. Personal settings and your default
shell are left unchanged.

- Preview: `bash install.sh --with-tools --dry-run`
- Config only: `bash install.sh`
- Personal settings: `~/.zsh_aliases` and `~/.zshrc.local`

## Find help

```sh
dothelp              # Search topics with fzf; full guide without it
dothelp python       # Python environments and uv
dothelp shortcuts    # Keys and everyday commands
dothelp prompt       # Understand the prompt
dothelp --all        # Complete guide
```

[Read the guide](REFERENCE.md) for commands, customization, recovery, and
installation details. [Glow](https://github.com/charmbracelet/glow) adds
terminal styling; `less` or plain text works without it.

## Update

```sh
git -C "$HOME/.dotfiles" pull --ff-only
exec zsh
```

Use your actual checkout path if different. Rerun the installer with
`--with-tools` to install newly added tools.

## Check

```sh
bash -n install.sh
bash -n configs/dothelp.sh
zsh -n configs/.zshrc
python3 -m unittest discover -s tests
```

Tests use temporary homes and mock package installation. Shell tests require
Zsh and are skipped when it is absent.
