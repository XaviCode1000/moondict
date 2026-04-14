# Variable Definition Syntax

**Rule ID**: `var-set-syntax`  
**Priority**: CRITICAL  
**Category**: Variables & Scoping

## What

Always use the `set` command to define, modify, or erase variables. Do not use `VAR=VAL` syntax.

## Why

Fish does not support `VAR=VAL` as a statement (only as an environment override for a single command). The `set` command provides explicit, consistent variable management with built-in scope and export control.

## Examples

### ✅ Correct
```fish
# Simple assignment
set name "Gazadev"
set count 42

# Multiple values
set fruits apple banana cherry

# Environment override (single command only)
EDITOR=nvim git commit
```

### ❌ Incorrect
```fish
# This is an error in fish
name="Gazadev"

# This sets variable "name" to "=" and "Gazadev" (two values!)
set name = "Gazadev"
```

## Best Practices

```fish
# Good: Clear, explicit
set -gx PATH /usr/local/bin $PATH

# Good: Multiple values in one command
set editors nvim emacs vscode

# Good: Capture command output
set files (ls *.txt)
```

## See Also

- [`var-scope-explicit`](var-scope-explicit.md) - Always specify scope
- [`anti-var-assign`](anti-var-assign.md) - Don't use VAR=VAL to set variables
