# Path Builtin Command

**Rule ID**: `path-command`
**Priority**: HIGH
**Category**: Paths & Files

## What

Use the `path` builtin command for all path manipulation operations. It replaces external tools like `dirname`, `basename`, `realpath`, and `readlink`.

## Why

The `path` builtin is built into fish, avoiding process spawning for common path operations. It's faster, more reliable, and handles edge cases better than external commands. It also works consistently across platforms.

## Examples

### ✅ Correct
```fish
# Get directory portion
path dirname /home/user/docs/file.txt
# → /home/user/docs

# Get filename
path basename /home/user/docs/file.txt
# → file.txt

# Get file extension
path extension /home/user/docs/file.txt
# → .txt

# Get stem (filename without extension)
path change_extension '' /home/user/docs/file.txt
# → /home/user/docs/file

# Resolve to absolute path
path resolve ./relative/path
# → /home/user/project/relative/path

# Check if path is absolute
path is-absolute /home/user/file
# → exits 0
path is-absolute relative/file
# → exits 1

# Join path components
path join /home/user docs file.txt
# → /home/user/docs/file.txt

# Get file type
path type /home/user/file
# → file (or dir, symlink, etc.)

# Work with multiple paths
path basename *.txt
# → Basename of each matching file
```

### ❌ Incorrect
```fish
# Using external dirname command
dirname /home/user/file.txt    # Spawns external process

# Using external basename
basename /home/user/file.txt   # Spawns external process

# Using external realpath
realpath ./file.txt            # May not exist on all systems

# Manual string manipulation for paths
string replace '*/' '' $path   # Fragile basename attempt

# Assuming string split works for paths
string split / $path           # Breaks on paths with spaces
```

## Best Practices

```fish
# Portable path extraction
function get_dir --argument filepath
    path dirname $filepath
end

# Handle paths with spaces safely
path basename "/path/with spaces/file.txt"
# → file.txt

# Build paths portably
set -l config_dir (path join $HOME .config myapp)
mkdir -p $config_dir

# Resolve symlinks
path resolve --no-symlinks ./link
# → Physical path, not following symlinks

# Filter by path type
for item in *
    if path type $item = dir
        echo "Directory: $item"
    end
end

# Change extension safely
path change_extension '.bak' /home/user/file.txt
# → /home/user/file.bak

# Safe: handle missing files
if path type $filepath = file
    process $filepath
else
    echo "File not found or not a regular file"
end

# Process batch of files
for file in $argv
    set -l dir (path dirname $file)
    set -l name (path basename $file)
    set -l ext (path extension $file)
    echo "Dir: $dir, Name: $name, Ext: $ext"
end

# Combine with other string operations
path filter -f *.txt    # Only regular files
path filter -d */       # Only directories
```

## See Also

- [`wildcard-recursive`](wildcard-recursive.md) - Recursive file matching
- [`string-replace`](string-replace.md) - For complex path transformations
- [`var-scope-explicit`](var-scope-explicit.md) - Variable scoping for path vars
