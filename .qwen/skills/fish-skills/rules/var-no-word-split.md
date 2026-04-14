# No Word Splitting

**Rule ID**: `var-no-word-split`  
**Priority**: CRITICAL  
**Category**: Variables & Scoping

## What

Fish does not perform word splitting on variable expansion. Variables expand as-is, preserving spaces.

## Why

Word splitting is a common source of bugs in bash. Fish eliminates this, making variables predictable.

## Examples

### ✅ Correct
```fish
set name "Mister Noodle"
mkdir $name
# Creates one directory: "Mister Noodle"

set files "file with spaces.txt"
cat $files
# Reads one file: "file with spaces.txt"
```

### ❌ Bash Behavior (NOT fish)
```bash
# In bash, this would create TWO files:
name="Mister Noodle"
mkdir $name  # Creates "Mister" and "Noodle" directories
```

## Best Practices

```fish
# No need to quote for word splitting prevention
set path_with_spaces "/path/with spaces/file.txt"
cat $path_with_spaces  # Works correctly

# Lists expand to multiple arguments
set files file1.txt file2.txt
ls $files  # Expands to: ls file1.txt file2.txt

# But each element stays intact
set names "John Doe" "Jane Smith"
echo $names  # Prints: John Doe Jane Smith (2 arguments)
```

## When You DO Need Splitting

```fish
# Split on specific delimiter
set -f path_components (echo "$PATH_VAR" | string split :)

# Use string split
set words (string split ' ' $sentence)
```

## See Also

- [`var-lists-native`](var-lists-native.md) - All variables are lists
- [`anti-word-split`](anti-word-split.md) - Don't quote variables to prevent word splitting
