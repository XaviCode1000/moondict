# String Replace for Pattern Substitution

**Rule ID**: `string-replace`
**Priority**: HIGH
**Category**: String Manipulation

## What

Use `string replace` for pattern-based string replacement. For regular expressions, add the `-r` flag. It operates on each element of a list independently.

## Why

Fish provides the `string` builtin for all text manipulation, replacing the need for `sed`, `awk`, or parameter expansion patterns. `string replace` is the dedicated tool for substitution operations.

## Examples

### ✅ Correct
```fish
# Literal replacement (first match only)
string replace .txt .md "notes.txt"
# → notes.md

# Replace all occurrences with -a
string replace -a e E "hello world"
# → hEllo world

# Regex replacement with -r
string replace -r '\.txt$' '.md' "notes.txt file.txt"
# → notes.md file.md

# Operates on lists element-by-element
set files report.txt data.txt notes.txt
string replace .txt .md $files
# → report.md
# → data.md
# → notes.md

# Case-insensitive with -i
string replace -i FISH Fish "i love fish shell"
# → i love Fish shell

# Use in variable assignment
set md_files (string replace .txt .md $txt_files)
```

### ❌ Incorrect
```fish
# Bash parameter expansion doesn't work in fish
set name "file.txt"
echo ${name/.txt/.md}      # ERROR: no parameter expansion

# Using sed when string replace suffices
echo "file.txt" | sed 's/.txt/.md/'    # Unnecessary, use string replace
```

## Best Practices

```fish
# Build safe filenames
set src (string replace -r '\.ts$' '.js' $source_files)

# Clean up paths
set clean (string replace -r '/+' '/' "/home//gazadev///docs")

# Remove prefixes
set names (string replace -r '^src/' '' $paths)

# Replace with captured groups (regex)
string replace -r '(\w+)@(\w+)\.com' '$1 at $2' "user@domain.com"
# → user at domain

# Chain replacements
set result (echo "file.TXT" | string replace -i .txt .md)

# Escape special regex chars with -r by escaping manually
string replace -r '\.' '-' "192.168.1.1"
# → 192-168-1-1
```

## See Also

- [`string-split`](string-split.md) - Split strings on delimiters
- [`cmdsub-parentheses`](cmdsub-parentheses.md) - Command substitution syntax
- [`var-lists-native`](var-lists-native.md) - String operations on list elements
