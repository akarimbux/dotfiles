# My terminal setup

A small Zsh setup that makes the terminal easier to use: searchable history,
quick directory jumps, readable file listings, and a Git prompt.

Zsh is the shell that reads your commands. This repository holds its settings
and an installer to help you get set up on another computer.

## Get started

You'll need Git and Bash. On macOS, install [Homebrew](https://brew.sh) first
if you want the installer to add the tools for you.

Run these commands in your terminal:

```sh
git clone https://github.com/akarimbux/dotfiles.git "$HOME/.dotfiles"
cd "$HOME/.dotfiles"
bash install.sh --with-tools
```

Then start Zsh:

```sh
exec zsh
```

That's it. Keep the `~/.dotfiles` folder where it is: your shell settings
link to the file inside it.

Already cloned this repository? Open that folder and run
`bash install.sh --with-tools`.

### What does the installer change?

It backs up your existing `~/.zshrc`, then links this setup in its place.
A `.zshrc` file contains the settings Zsh loads when you open a terminal.

With `--with-tools`, it also installs Zsh, Git, eza, jq, fzf, zoxide, and
the suggestion and highlighting plugins. It uses Homebrew on macOS or apt
on Debian/Ubuntu. Apt may ask for your password.

You can run the installer again; it keeps the link if it's already set up.
Your `~/.zshrc.local` and `~/.zsh_aliases` files are left alone.

Want to see the plan first?

```sh
bash install.sh --with-tools --dry-run
```

Already have the tools, or want to install them yourself?

```sh
bash install.sh
```

The config works without the optional tools. If your Linux version doesn't
offer a package, the installer skips it and tells you. On other operating
systems, use the config-only command and install tools with your usual
package manager.

The installer doesn't change your default shell. If new terminals still
open another shell, choose Zsh in your terminal settings.

## Try these first

| What you want to do | What to use |
| --- | --- |
| Find a command you ran before | **Ctrl-R**, then type to search |
| Find a file and insert its path | **Ctrl-T** |
| Pick a directory to move into | **Alt-C** |
| Search history by what you've already typed | Type a prefix, then press **Up / Down** |
| Accept a suggested command | **Right arrow** at the end of the line |
| Jump to a directory you've visited | `z project-name` |
| Pick a frequently visited directory | `zi` |
| List files with eza | `e` |
| Show file details and Git status | `el` |
| Include hidden files | `ea` |
| Show a directory tree, two levels deep | `et` |
| Clear the screen | `cls` |
| Go up one directory | `..` |

In an fzf search, type to narrow the list, use **Up / Down** to move,
**Enter** to choose, or **Ctrl-C** to cancel.

Fuzzy search shortcuts need fzf. Directory jumps need zoxide, which learns
as you visit folders. The eza shortcuts appear when eza is installed.
Your usual `ls`, `ll`, and `la` commands are still available.

### Working with JSON

Use jq to make JSON easier to read:

```sh
jq . data.json
```

Given a file with an `items` list, print each item's name:

```sh
jq -r '.items[] | .name' data.json
```

### What else is included?

- A prompt showing your current directory and, inside Git repositories,
  the branch and whether there are uncommitted changes.
- Shared command history across terminals, with duplicate entries removed.
- Command suggestions from your history and syntax highlighting, when the
  plugins are installed.
- Completion for `uv` and `uvx`, if you already have them installed.
  The installer doesn't install uv.

## Make it yours

Put your own aliases in `~/.zsh_aliases`:

```sh
alias projects='cd ~/projects'
```

Put settings specific to this computer in `~/.zshrc.local`, such as extra
paths or tool settings. Both files are optional. Open a new terminal after
editing them.

## Get updates

If you used the folder in the installation instructions:

```sh
git -C "$HOME/.dotfiles" pull --ff-only
exec zsh
```

The link picks up the updated configuration automatically. If an update adds
tools you want, run the installer again with `--with-tools`.

If you cloned into a different folder, use that path instead of
`$HOME/.dotfiles`.

## Go back to your old setup

The installer prints the location of your backup. It looks like:

```text
~/.zshrc.backup.A1B2C3D4/.zshrc
```

Move this setup's link aside, then put your backup back:

```sh
mv -i "$HOME/.zshrc" "$HOME/.zshrc.dotfiles-link"
mv -i "$HOME/.zshrc.backup.A1B2C3D4/.zshrc" "$HOME/.zshrc"
```

Replace `A1B2C3D4` with the suffix from your actual backup. Open a new
terminal afterward. If there was no previous config, there's no backup to
restore; you can just move the link aside.

This restores your shell settings. Tools installed by Homebrew or apt stay
installed.

## A few extra details

<details>
<summary>What is ZDOTDIR?</summary>

Zsh normally looks for `.zshrc` in your home folder. `ZDOTDIR` lets you
choose another folder for Zsh's configuration files.

You don't need to set it. If you already use it, the installer puts the
`.zshrc` link and backups there instead. Use that folder instead of
`$HOME` in the restore commands above. This config still reads personal
aliases and local settings from `~/.zsh_aliases` and `~/.zshrc.local`.

Check the folder the installer will use:

```sh
echo "${ZDOTDIR:-$HOME}"
```

</details>

<details>
<summary>Installing tools or plugins yourself</summary>

On macOS:

```sh
brew install zsh git eza jq fzf zoxide zsh-autosuggestions zsh-syntax-highlighting
```

On Debian/Ubuntu, where the packages are available:

```sh
sudo apt update
sudo apt install zsh git eza jq fzf zoxide zsh-autosuggestions zsh-syntax-highlighting
```

If eza isn't available in your Linux repositories, see its
[installation guide](https://github.com/eza-community/eza/blob/main/INSTALL.md).

You can also clone the Zsh plugins into your home folder:

```sh
mkdir -p "${XDG_DATA_HOME:-$HOME/.local/share}/zsh/plugins"
git clone https://github.com/zsh-users/zsh-autosuggestions.git \
  "${XDG_DATA_HOME:-$HOME/.local/share}/zsh/plugins/zsh-autosuggestions"
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git \
  "${XDG_DATA_HOME:-$HOME/.local/share}/zsh/plugins/zsh-syntax-highlighting"
```

For another location, set `ZSH_PLUGIN_DIR` in `~/.zshrc.local` to the
folder containing both plugin directories. Homebrew and standard Linux
package locations are detected automatically. Syntax highlighting loads last.

</details>

<details>
<summary>Checking the installer</summary>

From the repository folder:

```sh
bash -n install.sh
python3 -m unittest discover -s tests
```

The tests use temporary folders and mock package managers. They don't install
packages or change your shell settings.

</details>
