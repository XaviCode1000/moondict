# Logical Combiners: and / or / not

**Rule ID**: `syn-and-or-combiner`
**Priority**: CRITICAL
**Category**: Syntax & Control Flow

## What

Use `and`, `or`, and `not` as commands to combine conditions. The `&&` and `||` operators are also supported but have lower precedence — `and`/`or`/`not` bind tighter.

## Why

Fish's logical combiners are commands, not operators. This means they operate on the exit status of the preceding command. Using `&&`/`||` is valid but behaves differently in precedence, which can lead to unexpected results in complex expressions.

## Examples

### ✅ Correct
```fish
# and / or as command combiners
test -f /etc/hosts
and echo "hosts file exists"

test -d /tmp/backup
or mkdir -p /tmp/backup

# not for negation
not test -f /var/run/lock
and echo "No lock file found"

# Chaining conditions
test -f config.yml
and test -r config.yml
and echo "Config exists and is readable"

# Mixing && and || (lower precedence)
cmd1 && cmd2
and echo "both succeeded"

cmd1 || cmd2
or echo "both failed"
```

### ❌ Incorrect
```fish
# Bash-style && || in if conditions
if test -f foo.txt && echo "found"    # ERROR: && in if needs care
    echo "inside if"
end

# Using ! for negation
if ! test -f foo.txt                  # ERROR: use 'not' instead
    echo "not found"
end

# Assuming && has same precedence as and
test -f a.txt && test -f b.txt
and echo "both exist"
# This works but the grouping differs from what you might expect
```

## Best Practices

```fish
# Preferred: use and/or/not consistently
if test -f config.yml
    and test -s config.yml            # Non-empty
    echo "Config exists and has content"
end

# Safe file operations
test -d $target
or mkdir -p $target
and cd $target

# Guard patterns
command -v jq >/dev/null 2>&1
or begin
    echo "jq is required but not installed" >&2
    return 1
end

# Complex conditions (use if with test -a / -o or nested ifs)
if test -f $file
    and test -r $file
    and test -s $file
    echo "File exists, readable, and non-empty"
end

# Negation with not
not command -v python3 >/dev/null 2>&1
and begin
    echo "Python 3 not found" >&2
    return 1
end
```

## See Also

- [`syn-if-test`](syn-if-test.md) - Conditional syntax with if/test
- [`var-status-not-question`](var-status-not-question.md) - Checking variable existence
