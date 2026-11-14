# Environment variables
typeset -U path
path=("$HOME/bin" "$HOME/.local/bin" $path)
export PATH

# Enable extended globbing and better autocompletion
setopt EXTENDED_GLOB
autoload -Uz compinit && compinit

# uv and uvx autocomplete
if (( $+commands[uv] )); then
  eval "$(uv generate-shell-completion zsh)"
fi
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

# Enable prompt substitution
setopt PROMPT_SUBST

# Show Git information only when repository status is available
git_prompt() {
  local branch status_output indicator
  branch=$(git symbolic-ref --quiet --short HEAD 2>/dev/null) ||
    branch=$(git rev-parse --short HEAD 2>/dev/null) || return
  status_output=$(git status --porcelain 2>/dev/null) || return
  if [[ -n $status_output ]]; then
    indicator='%F{red}✗%f'
  else
    indicator='%F{green}✔%f'
  fi
  # Escape percent signs in branch names before prompt expansion.
  print -r -- "${branch//\%/%%} $indicator"
}

RPROMPT='$(git_prompt)'

# Display current path in PROMPT
PROMPT='%F{cyan}%n@%m%f %F{white}%~%f %F{yellow}❯ %f'

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
setopt AUTO_CD  # Automatically change to a directory without `cd`
setopt PUSHD_TO_HOME
setopt AUTO_PUSHD
setopt PUSHD_IGNORE_DUPS

# Custom behavior for less
export LESS='-R'

# Source custom scripts if any
if [[ -f ~/.zsh_aliases ]]; then
  source ~/.zsh_aliases
fi

# Machine-specific settings and overrides
if [[ -f ~/.zshrc.local ]]; then
  source ~/.zshrc.local
fi

# Optional fuzzy search: Ctrl-R history, Ctrl-T files, Alt-C directories
if (( $+commands[fzf] )); then
  if _fzf_init=$(fzf --zsh 2>/dev/null); then
    eval "$_fzf_init"
  else
    # Older fzf packages provide integration as separate scripts.
    for _fzf_dir in "$HOME/.fzf/shell" \
      "${HOMEBREW_PREFIX:-/opt/homebrew}/opt/fzf/shell" \
      /usr/local/opt/fzf/shell /usr/share/fzf /usr/share/doc/fzf/examples; do
      if [[ -r "$_fzf_dir/key-bindings.zsh" ]]; then
        [[ ! -r "$_fzf_dir/completion.zsh" ]] || source "$_fzf_dir/completion.zsh"
        source "$_fzf_dir/key-bindings.zsh"
        break
      fi
    done
  fi
  unset _fzf_init _fzf_dir
fi

# Learn frequently visited directories; jump with z and select with zi.
if (( $+commands[zoxide] )); then
  eval "$(zoxide init zsh)"
fi

# Optional plugins installed by a package manager or cloned locally.
for _plugin in zsh-autosuggestions zsh-syntax-highlighting; do
  for _plugin_root in "${ZSH_PLUGIN_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/zsh/plugins}" \
    "$HOME/.zsh" "${HOMEBREW_PREFIX:-/opt/homebrew}/share" \
    /usr/local/share /usr/share; do
    if [[ -r "$_plugin_root/$_plugin/$_plugin.zsh" ]]; then
      source "$_plugin_root/$_plugin/$_plugin.zsh"
      break
    fi
  done
done
unset _plugin _plugin_root
