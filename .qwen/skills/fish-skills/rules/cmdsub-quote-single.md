# Command Substitution Quoting

**Rule ID**: `cmdsub-quote-single`
**Priority**: HIGH
**Category**: Command Substitution

## What

Quote command substitutions with `"(command)"` to keep the output as a single argument. Without quotes, the output splits into multiple arguments on newlines.

## Why

Understanding the difference between quoted and unquoted command substitutions is critical for correct argument passing. Unquoted substitutions split on newlines into multiple list elements, while quoted substitutions preserve the entire output as one string.

## Examples

### ✅ Correct
```fish
# Quoted: single argument, preserves newlines
set x "$(cat file.txt)"
# $x is one element with embedded newlines

# Quoted with $() form
set content "$(git log --oneline -1)"
echo $content    # Entire log line as single string

# Unquoted: multiple arguments (splits on newlines)
set lines (cat file.txt)
# $lines is a list, one element per line

# Pass single value to command
echo "Config: $(cat config.txt)"

# Unquoted for iteration
for line in (cat file.txt)
    echo "Processing: $line"
end

# Quoted when filename might have spaces
process_file "$(cat name_file.txt)"

# Combine quoted substitutions
echo "$(date) - $(whoami)" >> log.txt
```

### ❌ Incorrect
```fish
# Unquoted when single value needed
set config (cat config.txt)
some_command $config    # WRONG: passes each line as separate arg

# Assuming quotes don't matter
set data (cat file)     # Splits into list
set data "$(cat file)"  # Single string - different behavior!

# Passing multi-line content as separate args unexpectedly
grep "pattern" (cat file_list.txt)
# If file_list has multiple lines, each becomes a separate file arg
# May not be intended

# Double quoting unnecessary for single-value commands
echo "$(hostname)"    # Works, but echo (hostname) is simpler
```

## Best Practices

```fish
# Read entire file as single string
set -l full_content "$(cat config.json)"

# Read file as lines (list)
set -l lines (cat config.txt)
for line in $lines
    process $line
end

# Capture command output for logging
set -l timestamp "$(date '+%Y-%m-%d %H:%M:%S')"
echo "[$timestamp] Operation started"

# Pass single filename from command
process "$(find . -name '*.log' | head -1)"

# Build multi-line message
set -l msg "$(cat <<EOF
Multiple
lines
here
EOF
)"

# Safe: always quote when passing to commands expecting single arg
git commit -m "$(cat commit_msg.txt)"

# Unquote when iterating
for file in (fd -e txt)
    echo "Found: $file"
end

# Combine quoted and unquoted in same command
set -l header "$(head -1 data.csv)"    # Single string
set -l all_lines (cat data.csv)        # List of lines

# Nested command substitutions
echo "User: $(stat -c %U "$(find . -name '*.md' | head -1)")"
```

## See Also

- [`cmdsub-parentheses`](cmdsub-parentheses.md) - Command substitution syntax
- [`cmdsub-newline-split`](cmdsub-newline-split.md) - How output splits into lists
- [`var-lists-native`](var-lists-native.md) - Native list handling
