<div align="center">

# Your terminal, upgraded.

A field guide to your Zsh setup.

**Search faster. Jump between projects. Keep Python tidy.**

[Get started](#get-started) · [Shortcuts](#at-your-fingertips) · [Python](#python-without-the-fuss) · [Customize](#make-it-yours) · [Recovery](#a-way-back)

</div>

---

> **Need this in your terminal?** Run `dothelp` from any directory.

## Get started

Git and Bash are required. On macOS, install [Homebrew](https://brew.sh) first.

```sh
git clone https://github.com/akarimbux/dotfiles.git "$HOME/.dotfiles"
cd "$HOME/.dotfiles"
bash install.sh --with-tools
exec zsh
```

**Already installed?** Get the latest configuration:

```sh
git -C "$HOME/.dotfiles" pull --ff-only
exec zsh
```

Keep the checkout in place. Your shell configuration links to it.

| Installer mode | Command |
| :--- | :--- |
| Config + tools | `bash install.sh --with-tools` |
| Preview changes | `bash install.sh --with-tools --dry-run` |
| Config only | `bash install.sh` |
| Installer help | `bash install.sh --help` |

The installer backs up an existing `.zshrc` before linking this setup. It keeps personal settings and leaves your default shell unchanged.

## At your fingertips

### Find it. Recall it. Run it.

| Action | Shortcut | Needs |
| :--- | :--- | :--- |
| Search command history | **Ctrl-R** | fzf |
| Find a file and insert its path | **Ctrl-T** | fzf |
| Pick a directory and move into it | **Alt-C** | fzf |
| Search history by the prefix you've typed | **↑ / ↓** | Built in |
| Accept a suggestion at the end of the line | **→** | Autosuggestions¹ |
| Start / end of line | **Home / End** | Terminal support |
| Move by a word | **Ctrl-← / Ctrl-→** | Terminal support |
| Delete the character under the cursor | **Delete** | Terminal support |

In a picker: **type** to filter · **↑ ↓** to move · **Enter** to choose · **Ctrl-C** to cancel.

¹ Uses the applicable keymap's forward-character binding. Personal bindings can change this behavior.

### Less typing, more moving

| Command | What it does |
| :--- | :--- |
| `z project-name` | Jump to a directory zoxide has learned |
| `zi` | Pick a frequent directory interactively; requires zoxide and fzf |
| `..` | Go up one directory |
| `./some-directory` | Enter a directory without typing `cd` |
| `dirs` | Show the directory stack |
| `popd` | Return through the directory stack |
| `cls` | Clear the screen |
| `dothelp` | Open the full terminal manual |

### A better look at your files

| Command | View |
| :--- | :--- |
| `ll` | Standard long listing with readable file sizes |
| `la` | Standard long listing, including hidden files |
| `e` | eza listing |
| `el` | Details, headers, and Git status |
| `ea` | Details and Git status, including hidden files |
| `et` | A directory tree, two levels deep |

The `e` commands appear when eza is installed. Your usual `ls` stays available.

## Know where you stand

Your prompt answers three questions: **where am I, which Python is active, and what's happening in Git?**

```text
[py:my-project/.venv] you@laptop ~/projects/my-project/src/api ❯
                                      my-project/src/api | feature/login ✗
```

The Git information appears at the right edge of the command line.

| Signal | Meaning |
| :--- | :--- |
| `[py:my-project/.venv]` | Active Python environment |
| `my-project/src/api` | Repository name + your location inside it |
| `feature/login` | Current branch |
| `✔` | Clean working tree |
| `✗` | Changes present, including untracked files |
| `detached@abc1234` | Detached checkout at a short commit ID |

Outside a repository, the Git label disappears. Without an active environment, the Python label disappears. Virtual environments take precedence over Conda; `.venv` and `venv` labels include their parent folder to distinguish projects.

## Python without the fuss

### A folder of scripts

Create an environment once, then activate it whenever you return.

```sh
cd your-project
venv 3.13
uv pip install requests
python your_script.py
deactivate
```

Next time, just run:

```sh
venv
```

| Command | Behavior |
| :--- | :--- |
| `venv` | Create `.venv` if needed, then activate it |
| `venv 3.13` | Create a new environment with Python 3.13, then activate it |
| `deactivate` | Leave the active environment |

> **Your existing environment is kept.** If `.venv` already exists, `venv 3.13` refuses to replace it. Use `venv` to activate it instead. Add `.venv/` to your project's `.gitignore`.

The helper requires uv. Python may be downloaded when requested. Entering a project directory does not automatically activate its environment.

### A project with dependencies

Let uv track the project and run commands in its environment:

```sh
uv init my-project
cd my-project
uv python pin 3.13
uv add requests
uv run python main.py
```

| Command | Use it to… |
| :--- | :--- |
| `uv sync` | Create or update an existing project's environment from its project files and lockfile |
| `uv run python main.py` | Run with project dependencies, without manual activation |
| `uv python install 3.13` | Download a Python version |
| `uv tool install ruff` | Install a standalone Python CLI |

Commit `pyproject.toml`, `uv.lock`, and `.python-version` for reproducible projects. Completion for `uv` and `uvx` loads when available.

## Make it yours

| File | Put this here |
| :--- | :--- |
| `~/.zsh_aliases` | Your aliases |
| `~/.zshrc.local` | Machine-specific paths, settings, and overrides |

For example, in `~/.zsh_aliases`:

```sh
alias projects='cd ~/projects'
```

Reload with `exec zsh`. Both files are ordinary Zsh scripts. Aliases load first, then local settings, followed by fzf, zoxide, and plugins. Syntax highlighting loads last.

History is shared between terminals, stored in `~/.zsh_history`, and limited to 10,000 saved entries. Older duplicate entries are removed.

## Keep it fresh

```sh
git -C "$HOME/.dotfiles" pull --ff-only
exec zsh
```

If an update adds tools you want, rerun `bash install.sh --with-tools` from the checkout. Use your actual checkout path if different.

## A way back

The installer prints the location of your previous configuration. Use that exact backup path:

```sh
mv -i "$HOME/.zshrc" "$HOME/.zshrc.dotfiles-link"
mv -i "$HOME/.zshrc.backup.A1B2C3D4/.zshrc" "$HOME/.zshrc"
```

Replace `A1B2C3D4` with your backup's suffix, then open a new terminal. If you use `ZDOTDIR`, substitute that directory for `$HOME` in these commands. With no previous configuration, simply move the link aside. Installed tools stay installed.

---

## Under the hood

<details>
<summary><strong>Platforms & installation behavior</strong></summary>

- **macOS:** Homebrew installs Zsh, Git, eza, jq, fzf, zoxide, uv, and both Zsh plugins.
- **Debian / Ubuntu:** apt installs available packages, including curl and CA certificates; uv comes from its [official installer](https://docs.astral.sh/uv/getting-started/installation/). sudo is used when needed.
- **Other platforms:** use config-only installation and install tools yourself. Some platform-specific commands may need adjustment.

An existing link to this checkout is kept. Other existing `.zshrc` files and links are backed up. A directory at the target is rejected. Linux keeps an existing uv found on PATH or at the selected installation path.

Tool installation failures stop before configuration replacement, but tools installed earlier in the process may remain. Unknown options return status 2; other failures return nonzero.

</details>

<details>
<summary><strong>Environment variables & file locations</strong></summary>

| Variable | Purpose |
| :--- | :--- |
| `ZDOTDIR` | Directory for `.zshrc` and its backups; defaults to `$HOME`. Export before installation. Personal settings still load from `$HOME`. |
| `UV_INSTALL_DIR` | Linux uv installation directory; defaults to `~/.local/bin`. Add a custom directory to PATH in `.zshrc.local`. |
| `ZSH_PLUGIN_DIR` | Folder containing both plugin directories; can be set in `.zshrc.local`. |
| `XDG_DATA_HOME` | Sets the local plugin root to `$XDG_DATA_HOME/zsh/plugins`; otherwise `~/.local/share/zsh/plugins`. |
| `HOMEBREW_PREFIX` | Helps find Homebrew's fzf integration and plugins. Standard package paths are also searched. |
| `VIRTUAL_ENV` | Active virtual environment; takes priority in the prompt. |
| `CONDA_DEFAULT_ENV` | Conda label when no virtual environment is active. |

The setup adds `~/bin` and `~/.local/bin` to PATH, sets `LESS=-R`, and suppresses duplicate Python activation labels with `VIRTUAL_ENV_DISABLE_PROMPT=1` and `CONDA_CHANGEPS1=false`.

| File | Role |
| :--- | :--- |
| `configs/.zshrc` | Tracked configuration in this checkout |
| `${ZDOTDIR:-$HOME}/.zshrc` | Installed link |
| `${ZDOTDIR:-$HOME}/.zshrc.backup.XXXXXXXX/.zshrc` | Previous configuration |
| `~/.zsh_history` | Shared history |
| `~/.local/bin/uv` and `uvx` | Default Linux uv executables |

</details>

<details>
<summary><strong>Troubleshooting & known limitations</strong></summary>

| Symptom | Check |
| :--- | :--- |
| `uv` is missing | Run the installer with `--with-tools`, then `exec zsh`. Check PATH for a custom installation directory. |
| Shortcuts or integrations are missing | Check the corresponding tools and plugins are installed; unavailable apt packages are skipped. |
| A new terminal opens another shell | Choose Zsh in your terminal settings. The installer leaves your default shell unchanged. |
| `dothelp` cannot open the manual | Install your operating system's `man` viewer and keep the checkout in place. |

**Known installer limitation:** do not set `ZDOTDIR` to this checkout's `configs` directory. The current installer can replace its own source with a self-referencing link.

**Known test limitation:** shell tests inherit HOME and can execute personal `.zsh_aliases` and `.zshrc.local` files. Use an isolated HOME to prevent interference.

</details>

<details>
<summary><strong>Validation & further reading</strong></summary>

From the checkout:

```sh
bash -n install.sh
zsh -n configs/.zshrc
python3 -m unittest discover -s tests
```

Automated tests mock package managers and uv environment creation. Prompt tests use real temporary Git repositories. Shell tests are skipped when Zsh is absent.

Explore the tools: [uv](https://docs.astral.sh/uv/) · [fzf](https://github.com/junegunn/fzf) · [zoxide](https://github.com/ajeetdsouza/zoxide) · [eza](https://github.com/eza-community/eza)

For command-level details, use `man zsh`, `man git`, or the installed tool's help.

</details>

---

<div align="center">

**One command away: `dothelp`**

[Back to top](#your-terminal-upgraded)

</div>
