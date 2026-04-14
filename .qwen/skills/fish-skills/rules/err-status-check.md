# Error Status Checking

**Rule ID**: `err-status-check`
**Priority**: MEDIUM
**Category**: Error Handling

## What

Check `$status` after commands to detect failures. Capture it immediately with `set -l s $status` before any other command overwrites it.

## Why

Fish doesn't have `set -e` as default behavior (though `fish -e` exists). The `$status` variable contains the exit code of the last command, but it's overwritten by every command execution. Capturing it immediately is essential for reliable error handling.

## Examples

### ✅ Correct
```fish
# Check status after command
cmd
if test $status -ne 0
    echo "Command failed"
end

# Capture status immediately
some_command
set -l exit_code $status
echo "Cleanup..."
if test $exit_code -ne 0
    echo "Command failed with code: $exit_code"
end

# Use 'or' for failure handling
some_command or echo "Failed with status $status"

# Use 'and' for success handling
some_command and echo "Success"

# Combine or/and
some_command and echo "OK" or echo "FAILED"

# Check for specific exit code
grep "pattern" file.txt
set -l s $status
if test $s -eq 0
    echo "Found"
else if test $s -eq 1
    echo "Not found"
else if test $s -eq 2
    echo "Error occurred"
end

# Status in function returns
function check_file --argument filepath
    if not test -e $filepath
        return 1
    end
    return 0
end

check_file config.toml
if test $status -ne 0
    echo "Config missing"
end
```

### ❌ Incorrect
```fish
# Status overwritten by echo
some_command
echo "checking..."    # Overwrites $status!
if test $status -ne 0    # Wrong - checking echo's status
    echo "Failed"
end

# Assuming non-zero exits halt execution
some_command
echo "This runs even if some_command failed"

# Using $? like bash
echo $?    # ERROR: fish uses $status, not $?

# Checking status too late
command1
command2
test $status -ne 0    # Checking command2's status, not command1
```

## Best Practices

```fish
# Capture immediately for later use
deploy_app
set -l deploy_status $status
cleanup_temp_files
if test $deploy_status -ne 0
    echo "Deployment failed"
    notify_team "Deploy failed (code: $deploy_status)"
end

# Use or for simple error handling
mkdir -p $dir or return 1
cp $source $dest or echo "Copy failed" >&2

# Chain with status checking
build_project
and test_project
and deploy
or echo "Pipeline failed at some stage"

# Custom error messages with status
function run_cmd --argument-list cmd_args
    eval $cmd_args
    set -l s $status
    if test $s -ne 0
        echo "Command failed: $cmd_args (exit code: $s)" >&2
    end
    return $s
end

# Preserve status across function calls
function my_wrapper
    some_command
    set -l s $status
    # Do cleanup, logging, etc.
    log_result $s
    return $s    # Preserve original status
end

# Safe: check in conditionals directly
if not some_command
    echo "Command failed"
end

# Use status for flow control
function process_or_skip --argument file
    test -e $file
    or return 0    # Skip if file doesn't exist

    validate $file
    or return 1    # Abort if validation fails

    transform $file
end

# Combine with fish's or/and operators
create_backup
and copy_new_version
and verify_integrity
and switch_symlink
or begin
    echo "Deployment failed, rolling back" >&2
    restore_backup
end
```

## See Also

- [`syn-and-or-combiner`](syn-and-or-combiner.md) - and/or control flow
- [`var-status-not-question`](var-status-not-question.md) - $status vs $?
- [`begin-block`](syn-begin-block.md) - Grouping commands for error handling
