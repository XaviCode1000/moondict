# Command Substitution with Parentheses

**Rule ID**: `cmdsub-parentheses`
**Priority**: HIGH
**Category**: Command Substitution

## What

Use `(command)` or `$(command)` syntax for command substitution. Both forms are equivalent. Backticks do not exist in fish.

## Why

Fish replaced backticks with parentheses for command substitution to improve readability, nesting, and consistency. The `$()` form is also supported for familiarity with POSIX shells.

## Examples

### ✅ Correct
```fish
# Parentheses form
set files (ls *.txt)
echo "Current dir:" (pwd)

# Dollar-parentheses form (equivalent)
set files $(ls *.txt)
echo "Current dir:" $(pwd)

# Nested command substitution
set owner (stat -c %U (ls -1 *.md | head -1))

# Command substitution in conditionals
if test (count (ls *.log)) -gt 0
    echo "Found log files"
end

# As function arguments
echo "Files:" (count (fd -e ts))
```

### ❌ Incorrect
```fish
# Backticks do not exist in fish
set files `ls *.txt`           # ERROR: backticks not supported

# Missing parentheses
set files ls *.txt             # ERROR: runs ls, doesn't capture output
```

## Best Practices

```fish
# Capture output into a list (splits on newlines)
set lines (cat config.txt)

# Single value capture
set hostname (hostname)

# Use string split for non-newline delimiters
set -l fields (string split : $PATH)

# Command substitution with pipes
set recent (git log --oneline -5)

# Safe: check command succeeded
set output (some_command 2>/dev/null)
or echo "Command failed"
```

## See Also

- [`cmdsub-newline-split`](cmdsub-newline-split.md) - How command output splits into lists
- [`anti-backtick`](anti-backtick.md) - Don't use backticks
- [`var-lists-native`](var-lists-native.md) - Captured output becomes a list
