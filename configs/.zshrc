# Enable extended globbing and better autocompletion
setopt EXTENDED_GLOB
autoload -Uz compinit && compinit

# uvx autocomplete
if (( $+commands[uvx] )); then
  eval "$(uvx --generate-shell-completion zsh)"
fi

# History settings
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt HIST_IGNORE_ALL_DUPS    # Remove older duplicates from history
setopt SHARE_HISTORY           # Share history across terminals

# Aliases
alias ll="ls -lh"               # Long format with human-readable sizes
alias la="ls -lha"              # Include hidden files
alias cls="clear"               # Clear screen
alias ..="cd .."

# Environment variables
typeset -U path
path=("$HOME/bin" "$HOME/.local/bin" $path)
export PATH

# Enable prompt substitution
setopt PROMPT_SUBST

# Function to display the current Git branch
git_branch() {
  git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "_"
}

# Function to display Git status
git_status() {
  local git_status=$(git status --porcelain 2>/dev/null)
  if [[ -n $git_status ]]; then
    echo "%F{red}✗%f"  # Uncommitted changes
  else
    echo "%F{green}✔%f"  # Clean working directory
  fi
}

# Dynamically evaluate the prompt with proper function calls
RPROMPT='$(git_branch) $(git_status)'

# Display current path in PROMPT
PROMPT='%F{cyan}%n@%m%f %F{white}%~%f %F{yellow}❯ %f'

# Keybindings for navigation
bindkey '^[[H' beginning-of-line  # Home key
bindkey '^[[F' end-of-line        # End key
bindkey '^[[3~' delete-char       # Delete key
bindkey '^[[1;5C' forward-word    # Ctrl+Right
bindkey '^[[1;5D' backward-word   # Ctrl+Left

# Colorful `ls`
export LS_COLORS="di=34:fi=0:ln=36:pi=33:so=35:bd=33;01:cd=33;01:or=31;01"
alias ls="ls --color=auto"

# Improve directory navigation
setopt AUTO_CD  # Automatically change to a directory without `cd`
setopt PUSHD_TO_HOME
setopt AUTO_PUSHD
setopt PUSHD_IGNORE_DUPS

# Custom behavior for less
export LESS='-R'

# Source custom scripts if any
[ -f ~/.zsh_aliases ] && source ~/.zsh_aliases
