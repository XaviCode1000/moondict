# Don't Use VAR=VAL to Set Variables

**Rule ID**: `anti-var-assign`  
**Priority**: REFERENCE  
**Category**: Anti-patterns

## What

Never use `VAR=VAL` as a standalone statement to set variables. Use `set VAR VAL` instead.

## Why

Fish does not support `VAR=VAL` as a variable assignment statement. This syntax is only valid as an environment override preceding a command.

## Examples

### ✅ Correct
```fish
# Setting variables
set name "Gazadev"
set count 10

# Environment override (this is fine)
EDITOR=nvim git commit
HOME=/tmp some_command
```

### ❌ Incorrect
```fish
# These are ERRORS in fish
name="Gazadev"
count=10
PATH="/usr/bin:$PATH"

# This sets "name" to TWO values: "=" and "Gazadev"
set name = "Gazadev"
```

## Migration from Bash

```bash
# Bash
export PATH="$HOME/bin:$PATH"
EDITOR=vim
```

```fish
# Fish
set -gx PATH ~/bin $PATH
set -gx EDITOR vim
```

## See Also

- [`var-set-syntax`](var-set-syntax.md) - Use set for all variable operations
- [`var-export-flag`](var-export-flag.md) - Use -x flag for exported variables
