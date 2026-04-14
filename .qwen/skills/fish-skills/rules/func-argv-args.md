# Function Arguments via $argv

**Rule ID**: `func-argv-args`
**Priority**: CRITICAL
**Category**: Functions

## What

Access function arguments via the `$argv` list variable, not positional parameters like `$1`, `$2`, `$3`.

## Why

Fish uses a single `$argv` list for all function arguments, consistent with its "everything is a list" model. This eliminates positional parameter confusion and enables powerful list operations on arguments.

## Examples

### ✅ Correct
```fish
function greet
    echo "Hello" $argv
end

greet World                    # Hello World
greet Gazadev and friends      # Hello Gazadev and friends

function copy_args
    # Access specific arguments by index (1-based)
    set -l src $argv[1]
    set -l dst $argv[2]
    cp $src $dst
end

function show_args
    # Count total arguments
    echo "Got" (count $argv) "arguments"

    # Iterate over all arguments
    for arg in $argv
        echo "Arg:" $arg
    end

    # Last argument
    echo "Last:" $argv[-1]
end
```

### ❌ Incorrect
```fish
# Bash-style positional parameters do not exist
function greet
    echo "Hello" $1        # ERROR: $1 doesn't exist
    echo "Second:" $2      # ERROR
    echo "Count:" $#       # ERROR
end

# $@ and $* also don't exist
function wrapper
    some_command $@        # ERROR: use $argv instead
end
```

## Best Practices

```fish
# Argument validation
function requires_file
    if test (count $argv) -eq 0
        echo "Usage: requires_file <file>" >&2
        return 1
    end
    set -l file $argv[1]
    test -f $file
    or begin
        echo "File not found: $file" >&2
        return 1
    end
end

# Default values for optional arguments
function connect
    set -l host $argv[1]
    set -l port $argv[2]

    if not set -q host
        set host localhost
    end
    if not set -q port
        set port 8080
    end

    echo "Connecting to $host:$port"
end

# Forward all arguments
function git_wrapper
    command git $argv
end

# Shift pattern (remove first element)
function process_queue
    while test (count $argv) -gt 0
        set -l item $argv[1]
        set -e argv[1]    # Remove first element
        echo "Processing: $item"
    end
end
```

## See Also

- [`var-lists-native`](var-lists-native.md) - All variables are lists
- [`func-definition`](func-definition.md) - Function definition syntax
- [`var-set-syntax`](var-set-syntax.md) - Variable assignment with `set`
