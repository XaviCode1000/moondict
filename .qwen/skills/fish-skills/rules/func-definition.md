# Function Definition Syntax

**Rule ID**: `func-definition`  
**Priority**: CRITICAL  
**Category**: Functions

## What

Use `function name ... end` syntax. Do not use `name() {}` bash-style syntax.

## Why

Fish has its own function syntax that is more consistent and readable. All blocks end with `end`.

## Examples

### ✅ Correct
```fish
function greet
    echo "Hello" $argv
end

function copy_files --description 'Copy files with backup'
    set -l source $argv[1]
    set -l dest $argv[2]
    cp -b $source $dest
end

# With event handler
function on_git_commit --on-event git_commit
    echo "New commit detected"
end
```

### ❌ Incorrect
```fish
# Bash syntax - does not work in fish
greet() {
    echo "Hello" $1
}
```

## Function Components

```fish
function name                    # Function name
    --description 'text'         # Optional description
    --on-event event_name        # Event handler
    --on-variable var_name       # Variable watcher
    --on-signal SIGINT           # Signal handler
    --inherit-variable name      # Inherit variable from caller
    
    # Function body
    commands...
    
    return $status               # Optional return
end
```

## Best Practices

```fish
# Always add descriptions
function deploy --description 'Deploy application to production'
    # ...
end

# Keep functions focused
function backup_file --description 'Create timestamped backup'
    set -l file $argv[1]
    set -l timestamp (date +%Y%m%d_%H%M%S)
    cp $file "$file.backup.$timestamp"
end

# Use return for exit codes
function check_file
    if not test -e $argv[1]
        echo "File not found" >&2
        return 1
    end
    return 0
end
```

## See Also

- [`func-argv-args`](func-argv-args.md) - Access arguments via $argv
- [`func-autoload`](func-autoload.md) - Save functions for autoloading
- [`func-description`](func-description.md) - Add descriptions to functions
