# Function Autoload from Files

**Rule ID**: `func-autoload`
**Priority**: CRITICAL
**Category**: Functions

## What

Save functions as individual files in `~/.config/fish/functions/name.fish`. Fish automatically loads functions on-demand by matching the filename (without `.fish`) to the function name. Use `funcsave` to persist and `funced` to edit.

## Why

Fish autoloads functions by filename, eliminating the need to source or explicitly load function definitions. This provides lazy loading (functions are only read when called) and clean organization — one function per file.

## Examples

### ✅ Correct
```fish
# Create a function file manually
~/.config/fish/functions/greet.fish:
    function greet
        echo "Hello, $argv!"
    end

# Or use funced (interactive editor)
funced greet
# Opens editor with function template
# Save and exit — fish writes the .fish file

# Or use funcsave (saves current function definition)
function greet
    echo "Hello, $argv!"
end
funcsave greet
# Writes to ~/.config/fish/functions/greet.fish

# Edit existing function
funced greet

# Reload all function files (usually not needed)
functions -c greet greet_backup    # Copy definition
```

### ❌ Incorrect
```fish
# Don't put functions in config.fish
# ~/.config/fish/config.fish:
function myfunc                    # Bad: loads on every shell start
    echo "hello"
end

# Don't source function files manually
source ~/.config/fish/functions/utils.fish   # Unnecessary — fish autoloads

# Don't use bash-style function files with multiple functions
# One function per file for autoloading
```

## Best Practices

```fish
# Directory structure for autoloading
~/.config/fish/functions/
├── git_status.fish      # function git_status
├── mkcd.fish            # function mkcd
├── serve.fish           # function serve
└── ...

# Create function via command line then save
function mkcd
    mkdir -p $argv
    and cd $argv
end
funcsave mkcd

# Edit with funced (opens in $EDITOR)
funced mkcd

# List all defined functions
functions

# List function file locations
type mkcd

# Remove a function and its file
functions -e mkcd
rm ~/.config/fish/functions/mkcd.fish

# Universal functions (shared across all fish instances)
# Save to ~/.config/fish/functions/ — they persist
```

## See Also

- [`func-argv-args`](func-argv-args.md) - Access arguments via $argv
- [`func-definition`](func-definition.md) - Function definition syntax
- [`var-set-syntax`](var-set-syntax.md) - Variable management inside functions
