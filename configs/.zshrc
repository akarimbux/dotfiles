# Environment variables
typeset -U path
path=("$HOME/bin" "$HOME/.local/bin" $path)
export PATH

# Enable extended globbing and better autocompletion
setopt EXTENDED_GLOB
autoload -Uz compinit && compinit -i

# uv and uvx autocomplete
if (( $+commands[uv] )); then
  eval "$(uv generate-shell-completion zsh)"
fi
if (( $+commands[uvx] )); then
  eval "$(uvx --generate-shell-completion zsh)"
fi

# venv [python-version]: create .venv with uv if missing, then activate it.
venv() {
  [[ -d .venv ]] || uv venv ${1:+--python} $1 .venv || return
  source .venv/bin/activate
}

# History settings
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt HIST_IGNORE_ALL_DUPS SHARE_HISTORY

# Aliases
alias ll="ls -lh"               # Long format with human-readable sizes
alias la="ls -lha"              # Include hidden files
alias cls="clear"               # Clear screen
alias ..="cd .."

# Optional enhanced directory listings
if (( $+commands[eza] )); then
  alias e='eza'
  alias el='eza --long --header --git'
  alias ea='eza --long --all --header --git'
  alias et='eza --tree --level=2'
fi

# Enable prompt substitution
setopt PROMPT_SUBST

# Render environments ourselves so activation does not add a second label.
export VIRTUAL_ENV_DISABLE_PROMPT=1
export CONDA_CHANGEPS1=false

python_env_prompt() {
  local env_path env_name
  if [[ -n ${VIRTUAL_ENV:-} ]]; then
    env_path=${VIRTUAL_ENV%/}
    env_name=${env_path:t}
    if [[ $env_name == .venv || $env_name == venv ]]; then
      env_name="${env_path:h:t}/$env_name"
    fi
  elif [[ -n ${CONDA_DEFAULT_ENV:-} ]]; then
    env_name=$CONDA_DEFAULT_ENV
  else
    return 0
  fi
  print -r -- "%F{magenta}[py:${env_name//\%/%%}]%f "
}

# Show the repository, path from its root, branch, and working-tree status.
git_prompt() {
  local root prefix location branch status_output indicator
  root=$(git rev-parse --show-toplevel 2>/dev/null) || return 0
  prefix=$(git rev-parse --show-prefix 2>/dev/null) || return 0
  location="${root:t}"
  [[ -z $prefix ]] || location+="/${prefix%/}"
  branch=$(git symbolic-ref --quiet --short HEAD 2>/dev/null) ||
    branch="detached@$(git rev-parse --short HEAD 2>/dev/null)" || return 0
  status_output=$(git status --porcelain 2>/dev/null) || return 0
  if [[ -n $status_output ]]; then
    indicator='%F{red}✗%f'
  else
    indicator='%F{green}✔%f'
  fi
  # Escape percent signs in names before Zsh interprets prompt formatting.
  print -r -- "%F{blue}${location//\%/%%}%f | ${branch//\%/%%} $indicator"
}

RPROMPT='$(git_prompt)'
PROMPT='$(python_env_prompt)%F{cyan}%n@%m%f %F{white}%~%f %F{yellow}❯ %f'

# Keybindings for navigation
bindkey '^[[H' beginning-of-line  # Home key
bindkey '^[[F' end-of-line        # End key
bindkey '^[[3~' delete-char       # Delete key
bindkey '^[[1;5C' forward-word    # Ctrl+Right
bindkey '^[[1;5D' backward-word   # Ctrl+Left

# Search history for commands beginning with the text already typed
autoload -Uz up-line-or-beginning-search down-line-or-beginning-search
zle -N up-line-or-beginning-search
zle -N down-line-or-beginning-search
bindkey '^[[A' up-line-or-beginning-search
bindkey '^[[B' down-line-or-beginning-search
bindkey '^[OA' up-line-or-beginning-search
bindkey '^[OB' down-line-or-beginning-search

# Colorful ls on macOS and Linux
if [[ $OSTYPE == darwin* ]]; then
  alias ls="ls -G"
else
  export LS_COLORS="di=34:fi=0:ln=36:pi=33:so=35:bd=33;01:cd=33;01:or=31;01"
  alias ls="ls --color=auto"
fi

# Improve directory navigation
setopt AUTO_CD AUTO_PUSHD PUSHD_TO_HOME PUSHD_IGNORE_DUPS

# Custom behavior for less
export LESS='-R'

# Personal aliases and machine-specific settings
[[ -f ~/.zsh_aliases ]] && source ~/.zsh_aliases
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local

# fzf: Ctrl-R history, Ctrl-T files, Alt-C directories
if (( $+commands[fzf] )); then
  # Older fzf (e.g. Ubuntu 22.04) has no --zsh flag
  _fzf_init=$(fzf --zsh 2>/dev/null) && eval "$_fzf_init" ||
    source /usr/share/doc/fzf/examples/key-bindings.zsh 2>/dev/null
  unset _fzf_init
fi

# Learn frequently visited directories; jump with z and select with zi.
if (( $+commands[zoxide] )); then
  eval "$(zoxide init zsh)"
fi

# Plugins (Homebrew or apt locations)
for _plugin in zsh-autosuggestions zsh-syntax-highlighting; do
  for _dir in "${HOMEBREW_PREFIX:-/opt/homebrew}/share" /usr/local/share /usr/share; do
    [[ -r $_dir/$_plugin/$_plugin.zsh ]] && source "$_dir/$_plugin/$_plugin.zsh" && break
  done
done
unset _plugin _dir
