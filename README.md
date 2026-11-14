# dotfiles

Collection of files to manage configurations and migrations.

## Zsh

Copy or symlink `configs/.zshrc` to `~/.zshrc`. Keep machine-specific
settings in `~/.zshrc.local` and custom aliases in `~/.zsh_aliases`.

### Optional shell tools

The configuration loads these only when installed:

- **fzf**: Ctrl-R searches history, Ctrl-T selects files, Alt-C selects directories.
- **zoxide**: `z name` jumps to a frequently visited directory; `zi` selects one with fzf.
- **zsh-autosuggestions**: suggests commands from history; Right accepts a suggestion.
- **zsh-syntax-highlighting**: highlights commands and syntax as you type.

On macOS with Homebrew:

```sh
brew install fzf zoxide zsh-autosuggestions zsh-syntax-highlighting
```

On Debian/Ubuntu (where available in your distribution):

```sh
sudo apt update
sudo apt install fzf zoxide zsh-autosuggestions zsh-syntax-highlighting
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
