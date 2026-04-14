# Function Command Wrapper

**Rule ID**: `func-alias-wrapper`
**Priority**: CRITICAL
**Category**: Functions

## What

Use `command actual_cmd $argv` inside functions that share the same name as an existing command to prevent infinite recursion.

## Why

When a function has the same name as a built-in or external command, calling that command by name inside the function would recursively call the function itself, causing infinite recursion. The `command` builtin bypasses function lookup and calls the actual external command directly.

## Examples

### ✅ Correct
```fish
# Wrap ls with color and icons
function ls --description 'List files with color and icons'
    command ls --color=auto --group-directories-first $argv
end

# Safe grep wrapper with line numbers
function grep --description 'grep with line numbers and color'
    command grep --color=auto -n $argv
end

# Wrapper that adds default flags
function docker --description 'Docker with socket timeout'
    command docker --context default $argv
end

# Conditional wrapper
function rm --description 'Safe rm with trash'
    if contains -- --force $argv
        command rm $argv
    else
        trash-put $argv
    end
end

# Multiple default options
function ll --description 'Long list with hidden files'
    command ls -alhF --color=auto $argv
end
```

### ❌ Incorrect
```fish
# Infinite recursion - ls calls itself
function ls
    ls --color=auto $argv    # ERROR: calls ls function recursively
end

# Same problem with grep
function grep
    grep -n $argv            # ERROR: infinite loop
end

# Missing command bypass
function find
    find . -type f $argv     # ERROR: calls itself
end
```

## Best Practices

```fish
# Always use command in wrappers
function cp --description 'Copy with backup'
    command cp --backup=numbered $argv
end

# Preserve exit status
function make --description 'Make with parallel jobs'
    command make -j (math (nproc) - 1) $argv
    return $status
end

# Combine with other utilities safely
function cat --description 'cat with syntax highlighting for code'
    if string match -qr '\.(py|rs|ts|js|fish|toml|json)$' $argv[1]
        bat --color=always $argv
    else
        command cat $argv
    end
end

# Pass through all arguments including flags
function git --description 'Git with pager override'
    command git --no-pager $argv
end

# Wrapper with environment variables
function nvim --description 'Neovim with config'
    command nvim --cmd 'set clipboard=unnamedplus' $argv
end
```

## See Also

- [`func-definition`](func-definition.md) - Function definition syntax
- [`func-argv-args`](func-argv-args.md) - Access arguments via $argv
- [`func-autoload`](func-autoload.md) - Save functions for autoloading
