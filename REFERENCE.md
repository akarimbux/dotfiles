# Your terminal, upgraded.

A field guide to your Zsh setup.

[Shortcuts](#at-your-fingertips) · [Prompt](#know-where-you-stand) ·
[Python](#python-without-the-fuss) · [Customize](#make-it-yours) ·
[Recovery](#a-way-back)

Run `dothelp` from any directory to search these topics with fzf. Without
fzf, it opens the full guide. Glow adds Markdown styling; otherwise it uses
`less` or plain text.

```sh
dothelp python
dothelp shortcuts
dothelp prompt
dothelp --all
```

You can also type part of a heading: `dothelp fresh`. Esc cancels the menu.
Redirected output is plain Markdown: `dothelp python > python-help.md`.

## Get started

Git and Bash are required. For automatic tool installation, use
[Homebrew](https://brew.sh) on macOS or apt on Debian/Ubuntu.

```sh
git clone https://github.com/akarimbux/dotfiles.git "$HOME/.dotfiles"
cd "$HOME/.dotfiles"
bash install.sh --with-tools
exec zsh
```

| Installer mode | Command |
| :--- | :--- |
| Config and tools | `bash install.sh --with-tools` |
| Preview changes | `bash install.sh --with-tools --dry-run` |
| Config only | `bash install.sh` |
| Help | `bash install.sh --help` |

The installer links `configs/.zshrc` to `${ZDOTDIR:-$HOME}/.zshrc`. Keep
the checkout in place. Existing files or links, including dangling links,
are backed up to `.zshrc.backup.XXXXXXXX/.zshrc` beside the target. An
existing link to this checkout is kept. Directories and targets in the
checkout's own `configs` directory are rejected.

Personal settings and the default shell are unchanged. If new terminals
open another shell, select Zsh in your terminal settings.

## At your fingertips

| Action | Shortcut | Needs |
| :--- | :--- | :--- |
| Search history | **Ctrl-R** | fzf |
| Insert a file path | **Ctrl-T** | fzf |
| Pick a directory | **Alt-C** | fzf |
| Search history by typed prefix | **↑ / ↓** | Built in |
| Accept a suggestion at end of line | **→** | Autosuggestions¹ |
| Start / end of line | **Home / End** | Terminal support |
| Move by a word | **Ctrl-← / Ctrl-→** | Terminal support |
| Delete character under cursor | **Delete** | Terminal support |

In a picker: type to filter, **↑ ↓** to move, **Enter** to choose,
**Ctrl-C** to cancel. ¹ Suggestion acceptance uses the applicable keymap's
forward-character binding; personal bindings can change it.

| Command | What it does |
| :--- | :--- |
| `z project-name` | Jump to a directory zoxide has learned |
| `zi` | Pick a frequent directory; requires zoxide and fzf |
| `..` | Go up one directory |
| `./some-directory` | Enter a directory without typing `cd` |
| `dirs`, `pushd`, `popd` | Inspect and use the directory stack |
| `cls` | Clear the screen |
| `ll`, `la` | Long listing; `la` includes hidden files |
| `e`, `el`, `ea`, `et` | eza listing, details with Git, hidden files, two-level tree |
| `dothelp` | Open this guide |

The `e` aliases appear when eza is installed. Your usual `ls` stays available.
Use `jq . data.json` to format JSON, or `jq -r '.items[] | .name' data.json`
to extract names from an `items` list.

## Know where you stand

```text
[py:my-project/.venv] you@laptop ~/projects/my-project/src/api ❯
                                      my-project/src/api | feature/login ✗
```

The left prompt shows the active Python environment, user, host, and current
directory. The Git label sits at the right edge of the same command line:
repository name, path within it, branch, and status.

- `✔`: clean working tree. `✗`: changes, including untracked files.
- `detached@abc1234`: detached checkout at a short commit ID.
- Virtual environments take precedence over Conda. `.venv` and `venv` labels
  include the parent directory to distinguish projects.

Outside a repository, the Git label disappears. Activation and deactivation
update the Python label; entering a directory does not activate an environment.

## Python without the fuss

For a folder of scripts:

```sh
cd your-project
venv 3.13
uv pip install requests
python your_script.py
deactivate
```

`venv` requires uv, accepts at most one version argument, and creates `.venv`
only if absent. Next time, run `venv` to activate it. An existing environment
is never replaced: specifying a version then fails, as does an existing
`.venv` without `bin/activate`. Add `.venv/` to your project's `.gitignore`.
Python may be downloaded when requested.

For projects with tracked dependencies:

```sh
uv init my-project
cd my-project
uv python pin 3.13
uv add requests
uv run python main.py
```

| Command | Purpose |
| :--- | :--- |
| `uv sync` | Update an existing project's environment from project files and lockfile |
| `uv run python main.py` | Run with project dependencies without manual activation |
| `uv python install 3.13` | Download a Python version |
| `uv tool install ruff` | Install a standalone Python CLI |

Commit `pyproject.toml`, `uv.lock`, and `.python-version` for reproducibility.
Completion for uv and uvx loads when available.

## Make it yours

Put aliases in `~/.zsh_aliases` and machine-specific paths or settings in
`~/.zshrc.local`. For example:

```sh
alias projects='cd ~/projects'
```

Both are optional Zsh scripts. Aliases load first, then local settings,
followed by fzf, zoxide, and plugins. Syntax highlighting loads last.
Reload with `exec zsh`.

History is shared between terminals in `~/.zsh_history`, with 10,000 saved
entries and older duplicates removed.

## Keep it fresh

```sh
git -C "$HOME/.dotfiles" pull --ff-only
exec zsh
```

Use your actual checkout path if different. Rerun `bash install.sh --with-tools`
from the checkout to install newly added tools.

## A way back

Use the exact backup path printed by the installer:

```sh
mv -i "$HOME/.zshrc" "$HOME/.zshrc.dotfiles-link"
mv -i "$HOME/.zshrc.backup.A1B2C3D4/.zshrc" "$HOME/.zshrc"
```

Replace `A1B2C3D4` with your backup suffix. With `ZDOTDIR`, substitute that
directory for `$HOME`. If no previous config existed, just move the link aside.
Open a new terminal. Installed tools stay installed.

## Under the hood

`--with-tools` installs Zsh, Git, eza, jq, fzf, zoxide, uv, autosuggestions,
and syntax highlighting. Homebrew handles macOS; apt handles Debian/Ubuntu
and also requests curl and CA certificates. Unavailable apt packages are
skipped; sudo is used when needed. On other platforms, install tools yourself
and run the config-only installer.

Linux installs uv using its [official installer](https://docs.astral.sh/uv/getting-started/installation/),
without editing shell files. Existing uv on PATH or at the selected location
is kept. Tool installation failures stop before replacing the configuration,
but tools already installed may remain. Unknown options return 2; other
failures return nonzero.

| Variable | Purpose |
| :--- | :--- |
| `ZDOTDIR` | Directory for `.zshrc` and backups; defaults to HOME. Export before installation. Personal settings still load from HOME. |
| `UV_INSTALL_DIR` | Linux uv directory; defaults to `~/.local/bin`. Add custom directories to PATH. |
| `ZSH_PLUGIN_DIR` | Directory containing both plugin subdirectories; set in `.zshrc.local`. |
| `XDG_DATA_HOME` | Local plugin root is `$XDG_DATA_HOME/zsh/plugins`, otherwise `~/.local/share/zsh/plugins`. |
| `HOMEBREW_PREFIX` | Helps find fzf and plugins; standard package locations are also searched. |
| `VIRTUAL_ENV`, `CONDA_DEFAULT_ENV` | Active environment labels; virtualenv takes precedence. |

The config adds `~/bin` and `~/.local/bin` to PATH, sets `LESS=-R`, and
suppresses duplicate environment labels with `VIRTUAL_ENV_DISABLE_PROMPT=1`
and `CONDA_CHANGEPS1=false`.

For manual installation, use the same package list with Homebrew or apt
(install uv separately on Linux). Plugins can also be cloned into
`~/.local/share/zsh/plugins`, each in its named subdirectory, or `~/.zsh`.
See the tools' installation guides for packages unavailable on your platform:
[uv](https://docs.astral.sh/uv/) · [fzf](https://github.com/junegunn/fzf) ·
[zoxide](https://github.com/ajeetdsouza/zoxide) · [eza](https://github.com/eza-community/eza).

If help fails, keep the checkout, `REFERENCE.md`, and `configs/dothelp.sh`
in place. For missing integrations, check installed tools and plugin paths.
For a custom uv directory, check PATH.

Validation commands are in the [README](README.md#check). Tests isolate HOME,
mock package managers and uv creation, and use real temporary Git repositories.
Shell tests require Zsh. For command details, use `man zsh`, `man git`, or the
tool's own help.
