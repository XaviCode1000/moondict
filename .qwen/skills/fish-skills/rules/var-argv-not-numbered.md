# Use $argv Not Positional Parameters

**Rule ID**: `var-argv-not-numbered`  
**Priority**: CRITICAL  
**Category**: Variables & Scoping

## What

Access function arguments via `$argv` list, not `$1`, `$2`, etc.

## Why

Fish passes all arguments as a single list `$argv`. This is more consistent and enables list operations.

## Examples

### ✅ Correct
```fish
function greet
    echo "Hello" $argv
    # Or specific elements:
    echo "First:" $argv[1]
    echo "Last:" $argv[-1]
    echo "Count:" (count $argv)
end

function copy_files
    set -l source $argv[1]
    set -l dest $argv[2]
    cp $source $dest
end
```

### ❌ Incorrect
```fish
# $1, $2, etc. do not exist in fish
function greet
    echo "Hello" $1  # ERROR
    echo "Args:" $#  # ERROR
end
```

## Best Practices

```fish
# Pass all arguments to another command
function wrapper
    actual_command $argv
end

# Iterate over arguments
function process
    for file in $argv
        echo "Processing: $file"
    end
end

# Check argument count
function requires_args
    if test (count $argv) -eq 0
        echo "Usage: requires_args <file>" >&2
        return 1
    end
end

# Default values
function with_defaults
    set -l mode ${argv[2]:-default_mode}
    # Or use test:
    set -l mode $argv[2]
    if not set -q mode
        set mode default_mode
    end
end
```

## See Also

- [`func-argv-args`](func-argv-args.md) - Access arguments via $argv
- [`var-lists-native`](var-lists-native.md) - All variables are lists
