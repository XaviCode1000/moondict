# Begin/End Block Grouping

**Rule ID**: `syn-begin-block`
**Priority**: CRITICAL
**Category**: Syntax & Control Flow

## What

Use `begin; ...; end` blocks to group commands together without creating a subshell. This is fish's only true block grouping construct.

## Why

Fish does not have subshells like bash `( cmd; cmd )`. The `begin/end` block groups commands in the same process, making it free and efficient. Variables set inside begin/end blocks are visible outside, unlike bash subshells.

## Examples

### ✅ Correct
```fish
# Group commands for piping
begin
    set -l VAR value
    echo $VAR
    echo "another line"
end | string upper

# Scope variables locally
begin
    set -l temp_file (mktemp)
    echo "data" > $temp_file
    process $temp_file
    rm $temp_file
end
# $temp_file no longer exists here

# Group with conditionals
begin
    cd /tmp/project
    git status
    git log --oneline -5
end

# Begin/end in pipelines
begin
    echo "header"
    cat data.csv
    echo "footer"
end | less

# Nested begin blocks
begin
    set -l outer "visible outside"
    begin
        set -l inner "visible only here"
        echo $inner
    end
    echo $outer    # Works
    echo $inner    # Empty - was local
end
```

### ❌ Incorrect
```fish
# Bash subshell syntax - does not exist in fish
( set -l VAR value; echo $VAR ) | process    # ERROR: not fish syntax

# Assuming parentheses create subshells
( cd subdir; ls )    # ERROR: this is command substitution, not grouping

# Using functions when begin/end suffices
function _temp_helper
    cd /tmp
    ls -la
end
_temp_helper    # Overkill - use begin/end instead
```

## Best Practices

```fish
# Isolate temporary state changes
begin
    set -l OLD_PWD $PWD
    cd /some/dir
    do_something
    cd $OLD_PWD
end

# Group related operations with shared local vars
begin
    set -l config (read_config)
    set -l host $config[1]
    set -l port $config[2]
    connect $host $port
end

# Feed multiple lines into a command
begin
    echo "line1"
    echo "line2"
    echo "line3"
end | sort

# Combine with redirects
begin
    echo "timestamp:" (date)
    echo "status:" (systemctl is-active myservice)
    echo "memory:" (free -h)
end >> /var/log/status.log

# Safe: clean up after grouped commands
begin
    set -l lock_file /tmp/mylock
    touch $lock_file
    run_critical_task
    rm -f $lock_file
end
```

## See Also

- [`anti-subshell-group`](anti-subshell-group.md) - Don't use bash subshell syntax
- [`var-scope-explicit`](var-scope-explicit.md) - Variable scoping rules
- [`var-set-syntax`](var-set-syntax.md) - Set variable syntax
