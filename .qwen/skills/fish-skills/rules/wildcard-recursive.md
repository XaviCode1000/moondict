# Recursive Wildcard Matching

**Rule ID**: `wildcard-recursive`
**Priority**: HIGH
**Category**: Paths & Files

## What

Use `**` for recursive directory matching in glob patterns. This finds files at any depth in the directory tree.

## Why

Fish's `**` wildcard provides a clean, built-in way to search recursively without needing external commands like `find`. It follows symlinks and returns results in natural sorted order, making it both powerful and predictable.

## Examples

### ✅ Correct
```fish
# Find all .log files recursively
ls **/*.log

# Find all markdown files
cat **/*.md

# Match files in current directory and all subdirs
rm -- **/*.tmp

# Find specific file anywhere
vim **/config.toml

# Combine with file type filter
ls -d **/       # Directories only
ls -f **/*      # Files only (with type suffix)

# Filter by name pattern
ls **/test_*.py

# Count all matching files
count **/*.js

# Use in for loops
for file in **/*.md
    echo "Processing: $file"
end
```

### ❌ Incorrect
```fish
# Using find for simple recursive glob
find . -name '*.log'    # Overkill - use **/*.log instead

# Manual recursion with external tools
ls -R | grep '\.log$'   # Fragile and slow

# Assuming * matches recursively
ls *.log    # Only matches current directory

# Using fd when glob suffices (for simple cases)
fd -e log   # fd is powerful but ** is built-in for simple cases
```

## Best Practices

```fish
# Safe deletion with confirmation
rm -i **/*.cache

# Combine with path command
for file in **/*.txt
    set -l dir (path dirname $file)
    echo "Found in: $dir"
end

# Process all config files
for config in **/config.{toml,yaml,yml}
    validate_config $config
end

# Find recently modified files
ls -lt **/* | head -20

# Combine with string match for filtering
set -l files **/*
set -l logs (string match -r '\.log$' $files)

# Handle large directories efficiently
# Limit results with head
ls **/*.bak | head -50

# Safe: check if glob matches anything
if count **/*.tmp > /dev/null
    rm **/*.tmp
    echo "Cleaned temp files"
else
    echo "No temp files found"
end

# Exclude hidden directories
set -l files (string match -rv '^\.' **/*)

# Combine with wildcards for specific patterns
ls **/{test,spec}_*.ts
```

## See Also

- [`path-command`](path-command.md) - Path manipulation builtin
- [`string-match`](string-match.md) - Filter glob results
- [`anti-backtick`](anti-backtick.md) - Command substitution syntax
