# Command Substitution Splits on Newlines

**Rule ID**: `cmdsub-newline-split`
**Priority**: HIGH
**Category**: Command Substitution

## What

Command substitutions split output on newlines only, not on spaces or tabs. A line containing spaces becomes a single list element. Use `string split` for custom delimiter-based splitting.

## Why

Unlike bash which splits on IFS (spaces, tabs, newlines by default), fish splits only on newlines. This prevents word-splitting bugs with filenames containing spaces and makes behavior predictable.

## Examples

### ✅ Correct
```fish
# Each line becomes one list element (even with spaces)
set files (ls -1)
echo $files[1]         # First file (spaces preserved)

# Single-line output = single element
set hostname (hostname)
count $hostname        # 1

# Multi-line output = multiple elements
set users (cat /etc/passwd | string split \n)
count $users           # Number of lines

# Use string split for space/tab delimiters
set -l words (string split " " "hello world foo")
echo $words[1]         # hello
echo $words[2]         # world
```

### ❌ Incorrect
```fish
# Assuming spaces split list elements
set line "one two three"
# $line is ONE element, not three
count $line            # 1, NOT 3

# Assuming bash-like word splitting
set data (echo "a b c")
echo $data[2]          # ERROR: there's only one element "a b c"
```

## Best Practices

```fish
# Split colon-separated PATH
set -l paths (string split : $PATH)
for p in $paths
    test -d $p
    and echo "Dir: $p"
end

# Split comma-separated values
set -l items (string split , "apple,banana,cherry")

# Skip empty elements
set -l lines (string split -n \n (cat file.txt))

# Split on custom delimiter
set -l fields (string split '|' "name|age|city")

# Handle filenames with spaces safely
for file in (fd -e txt)
    echo "Found: $file"
end
```

## See Also

- [`cmdsub-parentheses`](cmdsub-parentheses.md) - Command substitution syntax
- [`string-split`](string-split.md) - Split strings on delimiters
- [`var-lists-native`](var-lists-native.md) - All variables are lists
