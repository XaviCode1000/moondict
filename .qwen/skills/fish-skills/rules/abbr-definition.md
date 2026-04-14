# Use abbr for Abbreviations

**Rule ID**: `abbr-definition`  
**Priority**: HIGH  
**Category**: Interactive Features

## What

Use `abbr -a name expansion` to define abbreviations that expand as you type.

## Why

Abbreviations are better than aliases because you see the full command before execution, and they work in history.

## Examples

### ✅ Correct
```fish
# Simple abbreviation
abbr -a gs git status
abbr -a gc git commit
abbr -a gco git checkout

# With description
abbr -a dockerps --description 'Docker running containers' -- docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### ❌ Incorrect
```fish
# Using alias function (works but abbr is better)
alias gs='git status'

# Function wrapper (overkill for simple substitutions)
function gs
    git status $argv
end
```

## Best Practices

```fish
# Common git abbreviations
abbr -a gs git status
abbr -a ga git add
abbr -a gc git commit
abbr -a gco git checkout
abbr -a gb git branch
abbr -a gd git diff

# Docker abbreviations
abbr -a d docker
abbr -a dc docker compose
abbr -a di docker images
abbr -a dps docker ps

# System tools
abbr -a please sudo
abbr -a la ls -la
```

## Save Abbreviations

```fish
# Add to ~/.config/fish/conf.d/20-abbreviations.fish
# Or define interactively and save:
abbr -a gs git status
# Will persist if added to config file
```

## See Also

- [`abbr-regex`](abbr-regex.md) - Use regex for dynamic abbreviations
