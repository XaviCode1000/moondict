# Use $status Not $?

**Rule ID**: `var-status-not-question`  
**Priority**: CRITICAL  
**Category**: Variables & Scoping

## What

Use `$status` to access the exit status of the last command. Do not use `$?`.

## Why

Fish uses `$status` instead of `$?` for consistency and readability. The name is self-documenting.

## Examples

### ✅ Correct
```fish
false
echo $status  # Prints: 1

if test $status -ne 0
    echo "Command failed"
end

# Capture immediately
set -l exit_code $status
```

### ❌ Incorrect
```fish
# $? does not exist in fish
echo $?

# Wrong variable name
echo $status_code
```

## Best Practices

```fish
# Capture status immediately after command
some_command
set -l status $status

# Use in conditionals
if test $status -eq 0
    echo "Success"
else
    echo "Failed with code $status"
end

# Status is 0-255
test $status -ge 0 -a $status -le 255
```

## See Also

- [`var-pipestatus-list`](var-pipestatus-list.md) - Pipeline exit codes
- [`err-status-check`](err-status-check.md) - Check status after commands
