# Anti-pattern: Subshell Grouping

**Rule ID**: `anti-subshell-group`
**Priority**: REFERENCE
**Category**: Anti-patterns

## What

Do not use `( cmd; cmd )` parentheses syntax for grouping commands. Fish has no subshells. Use `begin; ...; end` instead. Both sides of a pipe run in the same process.

## Why

Bash users often try to use `( cmd; cmd )` for command grouping, which in bash creates a subshell. Fish doesn't have subshells, so this syntax means command substitution instead. Using it for grouping is a critical misunderstanding that causes unexpected behavior.

## Examples

### ✅ Correct
```fish
# Group commands with begin/end
begin
    cd /tmp
    ls -la
    rm -f *.tmp
end

# Pipeline with grouped commands
begin
    echo "header"
    cat data.txt
    echo "footer"
end | less

# Local variable scope in block
begin
    set -l temp (mktemp)
    process $temp
    rm $temp
end
# $temp doesn't exist here

# Multiple commands in pipeline
begin
    git log --oneline
    git status
end | grep -i "fix:"

# Redirect output from multiple commands
begin
    echo "=== Build Log ==="
    make
    echo "=== Build Complete ==="
end > build.log 2>&1
```

### ❌ Incorrect
```fish
# Parentheses mean command substitution in fish
( cd /tmp; ls )    # ERROR: tries to execute "cd /tmp; ls" as command

# Assuming subshell behavior
( set -x VAR value; echo $VAR ) | cat
# This is command substitution, not grouping
# Won't work as expected

# Trying to isolate variables
( set -l x=5; echo $x )    # ERROR: not grouping syntax

# Assuming pipe creates subshell
echo "data" | begin
    set -l input (cat)
    process $input
end
# This works but begin doesn't create a subshell
# Variables are still in same process
```

## Key Differences from Bash

| Feature | Bash | Fish |
|---------|------|------|
| Group commands | `{ cmd; cmd; }` | `begin; cmd; cmd; end` |
| Subshell | `( cmd; cmd )` | Does not exist |
| Pipe process | May fork | Same process |
| Variable scope | Subshell isolates | `set -l` in begin/end |
| Variable visibility | Subshell can't modify parent | All in same process |

## Best Practices

```fish
# Replace bash subshells with begin/end
# Bash: (cd /tmp && ls) | grep pattern
# Fish:
begin
    cd /tmp
    ls
end | grep pattern

# Replace bash variable isolation with begin/end locals
# Bash: (export VAR=value; cmd) # VAR doesn't leak
# Fish:
begin
    set -lx VAR value    # -l for local, -x for export
    cmd
end
# VAR doesn't exist here

# Feed multiple lines to commands
begin
    echo "line1"
    echo "line2"
    echo "line3"
end | sort > sorted.txt

# Combine multiple outputs
begin
    echo "System Info"
    uname -a
    echo "Disk Usage"
    df -h
    echo "Memory"
    free -h
end > system_report.txt

# Safe: understand that pipes don't fork
echo "data" | begin
    read -l input
    echo "Got: $input"
end
# Both commands run in the same process
# No subshell isolation to worry about

# Complex multi-command pipelines
begin
    git diff --name-only
    git status --porcelain
end | string match -r '\.rs$' | string sort -u

# Avoid: trying to capture subshell output
# This doesn't isolate variables
begin
    set -l changed=false
    modify_something
    set changed true
end
# $changed might exist outside if not set -l
```

## See Also

- [`syn-begin-block`](syn-begin-block.md) - Correct begin/end usage
- [`var-scope-explicit`](var-scope-explicit.md) - Variable scoping rules
- [`anti-backtick`](anti-backtick.md) - Command substitution anti-patterns
