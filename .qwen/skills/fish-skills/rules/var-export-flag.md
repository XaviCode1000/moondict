# Use -x Flag for Exported Variables

**Rule ID**: `var-export-flag`  
**Priority**: CRITICAL  
**Category**: Variables & Scoping

## What

Use `set -x` or `set -gx` to export variables. Do not use a separate `export` command.

## Why

Fish integrates export functionality into `set`, making it more concise and consistent.

## Examples

### ✅ Correct
```fish
# Global exported (like export VAR=VAL in bash)
set -gx EDITOR nvim
set -gx PATH /usr/local/bin $PATH

# Local exported (rare but valid)
function with_temp_env
    set -lx LANG C.UTF-8
    some_command
end
```

### ❌ Incorrect
```fish
# export command exists but is unnecessary
export EDITOR=nvim

# VAR=VAL syntax
export PATH="/usr/bin:$PATH"
```

## Unexport Variables

```fish
# Remove export flag
set -gu EDITOR

# Or erase entirely
set -e EDITOR
```

## See Also

- [`anti-export-separate`](anti-export-separate.md) - Don't use separate export command
