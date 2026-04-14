# Explicit Variable Scoping

**Rule ID**: `var-scope-explicit`  
**Priority**: CRITICAL  
**Category**: Variables & Scoping

## What

Always specify the scope flag (`-g`, `-l`, `-U`, `-f`) when setting variables to make intent clear.

## Why

Fish has four variable scopes. Without an explicit flag, variables default to function scope inside functions and global scope outside. Being explicit prevents accidental scope leakage and improves readability.

## Scopes

| Flag | Name | Lifetime | Use Case |
|------|------|----------|----------|
| `-l` | Local | Current block/function | Temporary variables, loop counters |
| `-g` | Global | Current session | Session-wide settings |
| `-U` | Universal | Persistent across restarts | User preferences, themes |
| `-f` | Function | Function scope (deprecated) | Legacy; use `-l` instead |

## Examples

### ✅ Correct
```fish
# Local to function or block
set -l last_status $status
set -l temp_file (mktemp)

# Global for the session
set -gx EDITOR nvim
set -g fish_autosuggestion_enabled 1

# Universal (persists across sessions)
set -U fish_color_command blue
set -U my_theme default

# Function-specific (legacy, prefer -l)
set -f _internal_cache "value"
```

### ❌ Incorrect
```fish
# Implicit scope - confusing intent
set EDITOR nvim

# This is local inside a function but not explicit
function my_func
    set temp "foo"  # Should be: set -l temp "foo"
end
```

## Best Practices

```fish
# In functions: default to local
function process_files
    set -l count (count $argv)
    set -l result ""

    for file in $argv
        set -l basename (path basename $file)
        # ...
    end
end

# In config.fish: use global or universal
set -gx PATH /usr/local/bin $PATH
set -U fish_greeting ""  # Silent greeting
```

## See Also

- [`var-set-syntax`](var-set-syntax.md) - Use set for all variable operations
- [`var-universal-persist`](var-universal-persist.md) - Universal variables for persistence
