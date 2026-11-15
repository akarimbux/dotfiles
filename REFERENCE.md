# Terminal setup reference

Run `dothelp` in Zsh to open the terminal version of this reference.

## Name

dotfiles - personal Zsh terminal setup and installer

## Synopsis

```sh
bash install.sh [--with-tools] [--dry-run]
bash install.sh --help

venv [python-version]
dothelp
```

## Description

This setup provides shared command history, completion, searchable history,
directory navigation, optional command suggestions and syntax highlighting,
and a prompt showing Python environment and Git information.

The installer links the checkout's configs/.zshrc to
${ZDOTDIR:-$HOME}/.zshrc. Keep the checkout in place: moving or deleting it
breaks the link. The installer does not change your default shell.

## Installation

Git and Bash are required. For a new installation:

```sh
git clone https://github.com/akarimbux/dotfiles.git "$HOME/.dotfiles"
cd "$HOME/.dotfiles"
bash install.sh --with-tools
exec zsh
```

On macOS, install Homebrew first. Automatic tool installation supports
Homebrew on macOS and apt on Debian/Ubuntu. For another platform, install
the tools yourself and run the installer without --with-tools.

### Installer options

**--with-tools**

Install Zsh, Git, eza, jq, fzf, zoxide, uv, zsh-autosuggestions, and
zsh-syntax-highlighting. Linux also requests curl and ca-certificates,
skips packages whose metadata is unavailable, and installs uv using its
official installer. Apt uses sudo when necessary.

**--dry-run**

Print planned changes without writing files or installing tools.
May be combined with --with-tools.

**-h, --help**

Print installer help and exit.

Without --with-tools, only the configuration link is installed.
Optional integrations activate when their tools are available.

### Backups and repeated installation

An existing .zshrc, including a dangling symbolic link, is moved into a
new .zshrc.backup.XXXXXXXX directory beside the target. The installer
prints the backup path. A directory at the target is rejected.

An existing link to this checkout is kept. Local settings and alias files
are not replaced. On Linux, an existing uv on PATH or at the selected
installation path is kept.

## Daily commands

**dothelp**

Open this setup's manual from any directory. Requires the system man viewer.

**ll**

List files with ls -lh.

**la**

List files, including hidden files, with ls -lha.

**cls**

Clear the terminal screen.

**..**

Move to the parent directory.

**e**

List files with eza, when installed.

**el**

Show an eza long listing with headers and Git status.

**ea**

Like el, including hidden files.

**et**

Show an eza directory tree, two levels deep.

**z directory-name**

Jump to a frequently visited directory using zoxide.

**zi**

Choose a directory interactively using zoxide and fzf.

Typing a directory path by itself changes to it. Directory changes also
maintain a directory stack; use dirs, pushd, and popd to inspect or use it.

## Keyboard shortcuts

Bindings apply when the relevant integration is available and can be
affected by terminal settings or personal overrides.

**Ctrl-R**

Search command history with fzf.

**Ctrl-T**

Choose files with fzf and insert their paths into the command line.

**Alt-C**

Choose a directory with fzf and change to it.

**Up / Down**

Search history using the text already typed as a prefix.

**Right arrow**

Accept a history suggestion at the end of the line when autosuggestions
is loaded and the applicable keymap uses forward-char.

**Home / End**

Move to the beginning or end of the command line.

**Delete**

Delete the character under the cursor.

**Ctrl-Right / Ctrl-Left**

Move forward or backward by a word.

In an fzf picker, type to filter, use Up and Down to move, Enter to select,
or Ctrl-C to cancel.

## Python environments

**venv**

Create .venv in the current directory using uv if it does not exist,
then activate it in the current shell. Reuse an existing environment.

**venv python-version**

Create and activate a new .venv with the requested Python version,
for example venv 3.13. uv may download a suitable Python interpreter.
If .venv already exists, refuse to replace it; run venv without a version
to activate it.

**deactivate**

Leave the active virtual environment.

venv requires uv, accepts at most one argument, and refuses to activate
an existing .venv without a bin/activate file. It does not activate an
environment merely because you enter a project directory.

### Folder of scripts

```sh
cd your-project
venv 3.13
uv pip install requests
python your_script.py
deactivate
```

Add .venv/ to the project's .gitignore.

### Projects with tracked dependencies

```sh
uv init my-project
cd my-project
uv python pin 3.13
uv add requests
uv run python main.py
```

For an existing project, uv sync creates or updates its environment from
project files and the lockfile. uv run does not require manual activation.
Commit pyproject.toml, uv.lock, and .python-version for reproducibility.

### Other uv commands

```sh
uv python install 3.13     # Download a Python version
uv tool install ruff      # Install a standalone Python CLI
```

Completion for uv and uvx is initialized when those commands are available.

## Prompt

The left prompt shows the active Python environment, if any, followed by
user@host, the current directory, and a command marker.

The right prompt shows the repository directory name, the path within it,
the branch, and a status symbol. A check mark means clean; a cross means
uncommitted changes, including untracked files. Outside a repository,
the Git label disappears. A detached checkout shows detached@ followed
by its short commit ID.

Virtual environments take precedence over Conda. An environment named
.venv or venv includes its parent directory name, such as
[py:my-project/.venv]. Activation and deactivation update the label.

## History

History is shared between terminals and stored in ~/.zsh_history.
HISTSIZE and SAVEHIST are set to 10000. Older duplicate entries are removed.

## Customization

Put personal aliases in ~/.zsh_aliases and machine-specific settings in
~/.zshrc.local. These files are sourced in that order after the main
aliases and prompt definitions, before fzf, zoxide, and optional plugins.
They can execute ordinary Zsh code.

For example, add this to ~/.zsh_aliases:

```sh
alias projects='cd ~/projects'
```

Reload with exec zsh or open a new Zsh terminal.

## Environment

**ZDOTDIR**

Select the directory containing .zshrc and its backups. Defaults to HOME.
Export it before running the installer if needed. Personal aliases and
local settings are still read from HOME.

**UV_INSTALL_DIR**

Override the Linux uv installation directory. Defaults to ~/.local/bin.
For a custom directory, also add it to PATH in ~/.zshrc.local; the setup
automatically adds only ~/bin and ~/.local/bin.

**ZSH_PLUGIN_DIR**

Directory containing the zsh-autosuggestions and zsh-syntax-highlighting
subdirectories. May be set in ~/.zshrc.local.

**XDG_DATA_HOME**

Changes the default local plugin root to $XDG_DATA_HOME/zsh/plugins.
Otherwise it is ~/.local/share/zsh/plugins.

**HOMEBREW_PREFIX**

Used to find Homebrew fzf integration and plugins. Standard Apple Silicon,
Intel Homebrew, and Linux package locations are also searched.

**VIRTUAL_ENV, CONDA_DEFAULT_ENV**

Determine the Python environment label. VIRTUAL_ENV takes precedence.

The setup sets VIRTUAL_ENV_DISABLE_PROMPT=1 and CONDA_CHANGEPS1=false
to avoid duplicate activation labels, and LESS=-R for colored output.

## Files

**configs/.zshrc**

Tracked configuration inside the checkout.

**${ZDOTDIR:-$HOME}/.zshrc**

Installed symbolic link.

**${ZDOTDIR:-$HOME}/.zshrc.backup.XXXXXXXX/.zshrc**

Previous configuration, when one existed.

**~/.zsh_aliases**

Optional personal aliases.

**~/.zshrc.local**

Optional machine-specific settings.

**~/.zsh_history**

Persistent command history.

**~/.local/bin/uv, ~/.local/bin/uvx**

Default Linux uv executables.

## Updates

```sh
git -C "$HOME/.dotfiles" pull --ff-only
exec zsh
```

Use your actual checkout path if different. The symbolic link picks up
configuration updates automatically. To install newly added tools:

```sh
cd "$HOME/.dotfiles"
bash install.sh --with-tools
```

## Restoring the previous configuration

Use the exact backup path printed during installation. For example:

```sh
mv -i "$HOME/.zshrc" "$HOME/.zshrc.dotfiles-link"
mv -i "$HOME/.zshrc.backup.A1B2C3D4/.zshrc" "$HOME/.zshrc"
```

Replace A1B2C3D4 with the actual suffix. If ZDOTDIR is set, substitute that
directory for HOME in these two commands. Open a new terminal afterward.
If no previous config existed, move the link aside without restoring a backup.
Installed tools remain installed.

## Diagnostics

**uv is missing**

Run bash install.sh --with-tools from the checkout, then exec zsh.
For a custom UV_INSTALL_DIR, ensure that directory is on PATH.

**Optional commands or shortcuts are missing**

Check that the corresponding tools and plugins are installed. A Linux
package unavailable through apt is skipped. The config remains usable.

**New terminals open another shell**

Choose Zsh in your terminal settings. The installer does not change the
account's default shell.

**Installer exit status**

Zero indicates success or help; unknown options return 2. Other failures
return a nonzero status. A failed tool installation stops before replacing
the shell configuration, but may leave tools already installed.

## Checking the setup

From the checkout:

```sh
bash -n install.sh
zsh -n configs/.zshrc
python3 -m unittest discover -s tests
```

Package managers and uv creation are mocked in the automated tests.
Prompt tests use real temporary Git repositories. Shell tests require Zsh;
they are skipped when it is absent.

## Known limitations

Do not point ZDOTDIR at the checkout's configs directory: the current
installer can replace its source file with a self-referencing link.

Shell tests currently inherit HOME and can execute your personal
~/.zsh_aliases and ~/.zshrc.local. Run them with an isolated HOME when
personal startup code could interfere.

## See also

zsh(1), zshbuiltins(1), git(1), fzf(1), zoxide(1), eza(1), jq(1)

Repository: https://github.com/akarimbux/dotfiles

uv documentation: https://docs.astral.sh/uv/
