# Use if test, Not [ or [[

**Rule ID**: `syn-if-test`  
**Priority**: CRITICAL  
**Category**: Syntax & Control Flow

## What

Use `if test ...` for conditionals. Do not use `[ ... ]` or `[[ ... ]]`.

## Why

Fish's `test` builtin is clearer and supports floating point comparisons. Square brackets work but are unnecessary compatibility.

## Examples

### ✅ Correct
```fish
# String comparison
if test "$name" = "gazadev"
    echo "Welcome"
end

# Numeric comparison
if test $count -gt 10
    echo "Too many"
end

# Float comparison (bash can't do this)
if test $temperature -gt 98.6
    echo "Fever detected"
end

# File tests
if test -e /etc/hosts
    echo "Hosts file exists"
end

if test -f "$file"
    echo "Regular file"
end

# Multiple conditions
if test -n "$var" -a -f "$file"
    echo "Var set and file exists"
end
```

### ⚠️ Works but Discouraged
```fish
# This works but why use it?
if [ "$name" = "gazadev" ]
    echo "Welcome"
end
```

### ❌ Incorrect
```fish
# [[ ]] does not exist in fish
if [[ "$name" == "gazadev" ]]
    echo "Welcome"
end
```

## Best Practices

```fish
# Prefer test for clarity
if test (count $files) -eq 0
    echo "No files found"
end

# Use set -q for variable existence
if set -q $var
    echo "Variable is set"
end

# Combine with and/or
if test -f "$file"
    and test -r "$file"
    echo "File exists and is readable"
end

# Negation
if not test -e "$file"
    echo "File missing"
end

# Or use !
if ! test -e "$file"
    echo "File missing"
end
```

## Common Test Operators

| Operator | Meaning |
|----------|---------|
| `-eq`, `-ne` | Equal, not equal (integers) |
| `-gt`, `-ge`, `-lt`, `-le` | Greater/less than (integers) |
| `=`, `!=` | String equal, not equal |
| `-n`, `-z` | String non-empty, empty |
| `-e`, `-f`, `-d` | Exists, file, directory |
| `-r`, `-w`, `-x` | Readable, writable, executable |
| `-s` | File exists and has size > 0 |

## See Also

- [`syn-and-or-combiner`](syn-and-or-combiner.md) - Use and/or/not combinators
- [`syn-test-float`](syn-test-float.md) - Test supports floating point
- [`syn-test-query`](syn-test-query.md) - Use set -q to check existence
