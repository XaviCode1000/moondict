# String Split for Delimiter-Based Splitting

**Rule ID**: `string-split`
**Priority**: HIGH
**Category**: String Manipulation

## What

Use `string split` to split strings on a specified delimiter. Use the `-n` flag to skip empty elements from the result.

## Why

Since command substitutions only split on newlines, `string split` is the tool for splitting on any custom delimiter (colons, commas, pipes, etc.). This replaces bash's IFS manipulation.

## Examples

### ✅ Correct
```fish
# Split on a delimiter
string split , "apple,banana,cherry"
# → apple
# → banana
# → cherry

# Split PATH on colons
set -l paths (string split : $PATH)
echo $paths[1]         # First path component

# Skip empty elements with -n
string split -n : "a::b:c:"
# → a
# → b
# → c
# (empty elements removed)

# Capture result into a variable
set -l fields (string split : "user:1000:home")
echo $fields[1]        # user
echo $fields[2]        # 1000
echo $fields[3]        # home

# Split on multi-character delimiter
string split -- " -> " "A -> B -> C"
# → A
# → B
# → C
```

### ❌ Incorrect
```fish
# Bash IFS manipulation doesn't work in fish
IFS=: read -ra parts <<< "$PATH"    # ERROR: bashism

# Assuming command substitution splits on spaces
set words (echo "hello world")
# $words is ONE element: "hello world"
# Need string split for space splitting
```

## Best Practices

```fish
# Parse colon-separated config lines
set -l parts (string split : "username:x:1000:1000:User:/home:/bin/bash")
set -l username $parts[1]
set -l uid $parts[3]
set -l shell $parts[7]

# Split and filter
set -l csv_fields (string split -n , "name,,age,,city")
# → name, age, city (empties removed)

# Split key-value pairs
set -l kv (string split = "KEY=value=with=equals")
set -l key $kv[1]
set -l val (string join = $kv[2..])    # Rejoin rest

# Split on newline explicitly
set -l lines (string split \n $multiline_string)

# Combine with string replace for cleanup
set cleaned (string split -n , "a,b,,c," | string trim)

# Safe: handle missing delimiter gracefully
set -l parts (string split = "no_equals_here")
# → "no_equals_here" (single element)
```

## See Also

- [`string-replace`](string-replace.md) - Pattern-based string replacement
- [`cmdsub-newline-split`](cmdsub-newline-split.md) - Command output splits on newlines
- [`var-lists-native`](var-lists-native.md) - List operations on split results
