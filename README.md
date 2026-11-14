# dotfiles

Collection of files to manage configurations and migrations.

## Install

Requires Git and Bash. Clone this repository into a permanent location:

```sh
git clone https://github.com/akarimbux/dotfiles.git "$HOME/.dotfiles"
cd "$HOME/.dotfiles"
bash install.sh --dry-run
bash install.sh --with-tools
```

Already have a checkout? Run the last two commands from that checkout.

- `bash install.sh` installs the configuration only.
- `--with-tools` also installs Zsh, Git, eza, jq, fzf, zoxide,
  zsh-autosuggestions, and zsh-syntax-highlighting through Homebrew on macOS
  or apt on Debian/Ubuntu. Install Homebrew first on macOS: https://brew.sh
- `--dry-run` previews changes; combine it with `--with-tools` to preview packages.
  Apt package availability is checked during the real install after updating metadata.
- Apt may ask for your sudo password. Packages absent from your distribution's
  repositories are skipped with a message; the config still works without them.
  Other operating systems can install the config and manage tools separately.

Existing `~/.zshrc` files or symlinks are moved into a unique
`~/.zshrc.backup.XXXXXXXX/.zshrc` backup, with the exact location printed.
The installer then creates a symlink to this checkout's `configs/.zshrc`.
Running it again keeps the existing link. It refuses to replace directories.

If `ZDOTDIR` is set, installation and backups use that directory instead of
your home directory. Keep the checkout in place so the symlink stays valid.
The installer leaves your login shell unchanged. Open Zsh with `exec zsh`;
to use it by default, choose Zsh in your terminal settings.

### Update

```sh
git -C "$HOME/.dotfiles" pull --ff-only
exec zsh
```

Use your checkout's actual path if it differs. The symlink picks up config
changes automatically. Re-run `bash install.sh --with-tools` for new dependencies.

### Restore your previous configuration

Move the installed symlink aside, then restore the backup printed by the installer:

```sh
mv "$HOME/.zshrc" "$HOME/.zshrc.dotfiles-link"
mv "$HOME/.zshrc.backup.XXXXXXXX/.zshrc" "$HOME/.zshrc"
```

Replace `XXXXXXXX` with your actual backup suffix. If you set `ZDOTDIR`,
use that directory in both paths. Package installations remain installed.

## Zsh

Keep machine-specific settings in `~/.zshrc.local` and custom aliases in
`~/.zsh_aliases`; the installer does not modify either file.

### Optional shell tools

The configuration loads these only when installed:

- **eza**: `e` lists files, `el` shows details and Git status, `ea` includes hidden files, and `et` shows a two-level tree. Existing `ls`, `ll`, and `la` aliases remain available.
- **jq**: query and format JSON directly with `jq`; no shell initialization needed.
- **fzf**: Ctrl-R searches history, Ctrl-T selects files, Alt-C selects directories.
- **zoxide**: `z name` jumps to a frequently visited directory; `zi` selects one with fzf.
- **zsh-autosuggestions**: suggests commands from history; Right accepts a suggestion.
- **zsh-syntax-highlighting**: highlights commands and syntax as you type.

On macOS with Homebrew:

```sh
brew install eza jq fzf zoxide zsh-autosuggestions zsh-syntax-highlighting
```

On Debian/Ubuntu (where available in your distribution):

```sh
sudo apt update
sudo apt install eza jq fzf zoxide zsh-autosuggestions zsh-syntax-highlighting
```

Alternatively, clone the plugins locally:

```sh
mkdir -p "${XDG_DATA_HOME:-$HOME/.local/share}/zsh/plugins"
git clone https://github.com/zsh-users/zsh-autosuggestions.git \
  "${XDG_DATA_HOME:-$HOME/.local/share}/zsh/plugins/zsh-autosuggestions"
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git \
  "${XDG_DATA_HOME:-$HOME/.local/share}/zsh/plugins/zsh-syntax-highlighting"
```

For another plugin location, set `ZSH_PLUGIN_DIR` in `~/.zshrc.local`.
It should contain the two plugin directories. Homebrew and standard Linux
package locations are detected automatically. Syntax highlighting loads last.

Open a new terminal after installing dependencies or updating the configuration.
Up/Down searches history by the prefix you have typed.

### JSON with jq

```sh
jq . data.json                        # Pretty-print JSON
jq '.items[] | .name' data.json        # Extract names
jq -r '.items[] | .name' data.json     # Output names without JSON quotes
```

The optional tools must be installed on each machine. If your distribution
does not package eza, follow its installation instructions:
https://github.com/eza-community/eza/blob/main/INSTALL.md

### Installer checks

```sh
bash -n install.sh
python3 -m unittest discover -s tests
```

The tests use temporary directories and mock package managers; they do not
install packages or modify your shell configuration.
