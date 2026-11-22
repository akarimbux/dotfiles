typeset -U path
path=(~/bin ~/.local/bin $path)

autoload -Uz compinit && compinit -i
(( $+commands[uv] )) && eval "$(uv generate-shell-completion zsh)"

HISTFILE=~/.zsh_history HISTSIZE=10000 SAVEHIST=10000
setopt HIST_IGNORE_ALL_DUPS SHARE_HISTORY AUTO_CD EXTENDED_GLOB PROMPT_SUBST

# Up/down search history by typed prefix; Ctrl-arrows move by word
autoload -Uz up-line-or-beginning-search down-line-or-beginning-search
zle -N up-line-or-beginning-search; zle -N down-line-or-beginning-search
bindkey '^[[A' up-line-or-beginning-search '^[OA' up-line-or-beginning-search
bindkey '^[[B' down-line-or-beginning-search '^[OB' down-line-or-beginning-search
bindkey '^[[H' beginning-of-line '^[[F' end-of-line '^[[3~' delete-char
bindkey '^[[1;5C' forward-word '^[[1;5D' backward-word

[[ $OSTYPE == darwin* ]] && alias ls='ls -G' || alias ls='ls --color=auto'
alias ll='ls -lh' la='ls -lha' ..='cd ..'
(( $+commands[eza] )) && alias ll='eza -l --git' la='eza -la --git'

# venv [python-version]: create .venv with uv if missing, then activate
venv() {
  [[ -d .venv ]] || uv venv ${1:+--python} $1 .venv || return
  source .venv/bin/activate
}

# Prompt: [py:env] ~/dir ❯            branch ✗
export VIRTUAL_ENV_DISABLE_PROMPT=1
_py() { [[ -n $VIRTUAL_ENV ]] && print -r -- "%F{magenta}[py:${VIRTUAL_ENV:h:t}]%f " }
_git() {
  local b; b=$(git branch --show-current 2>/dev/null) || return
  [[ -n $(git status --porcelain 2>/dev/null) ]] && b+=' %F{red}✗%f'
  print -r -- "%F{blue}${b:-detached}%f"
}
PROMPT='$(_py)%F{cyan}%~%f %F{yellow}❯%f '
RPROMPT='$(_git)'

[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local

# Optional tools
if (( $+commands[fzf] )); then
  f=$(fzf --zsh 2>/dev/null) && eval "$f" || source /usr/share/doc/fzf/examples/key-bindings.zsh 2>/dev/null
fi
(( $+commands[zoxide] )) && eval "$(zoxide init zsh)"
for p in zsh-autosuggestions zsh-syntax-highlighting; do
  for d in ${HOMEBREW_PREFIX:-/opt/homebrew}/share /usr/share; do
    [[ -r $d/$p/$p.zsh ]] && source $d/$p/$p.zsh && break
  done
done
unset f p d
