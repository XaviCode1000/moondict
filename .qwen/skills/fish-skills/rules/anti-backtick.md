# No Backticks for Command Substitution

**Rule ID**: `anti-backtick`
**Priority**: REFERENCE
**Category**: Anti-patterns

## What

Do not use backticks for command substitution. Backticks do not exist in fish. Use `(command)` or `$(command)` instead.

## Why

Backtick command substitution is a POSIX shell feature that fish intentionally removed due to nesting difficulties, readability problems, and escaping complexity. Fish only supports parentheses-based substitution.

## Examples

### ✅ Correct
```fish
# Parentheses form
set files (ls *.txt)
echo "Today:" (date +%Y-%m-%d)

# Dollar-parentheses form
set files $(ls *.txt)
echo "Today:" $(date +%Y-%m-%d)

# Nested substitution
set owner (stat -c %U (ls -1 *.md | head -1))

# In conditionals
if test (count (fd -e ts)) -gt 0
    echo "Found TypeScript files"
end
```

### ❌ Incorrect
```fish
# Backticks simply do not exist in fish
set files `ls *.txt`
# Fish interprets backticks as literal characters or errors
# depending on context — they do NOT perform substitution

# Escaped backticks also don't work
set files \`ls *.txt\`
# Still not command substitution
```

## Best Practices

```fish
# Migrate from bash: replace all backtick patterns
# Before (bash):
#   FILES=`ls *.txt`
# After (fish):
set files (ls *.txt)

# Before (bash):
#   echo "User: `whoami`"
# After (fish):
echo "User:" (whoami)

# Nested replacements — read innermost first
# Before (bash):
#   DIR=`dirname \`readlink -f file.txt\``
# After (fish):
set dir (dirname (readlink -f file.txt))

# Use $() if migrating from zsh (familiar syntax)
set output $(grep -c error log.txt)
```

## See Also

- [`cmdsub-parentheses`](cmdsub-parentheses.md) - Command substitution syntax
- [`cmdsub-newline-split`](cmdsub-newline-split.md) - How output splits into lists
- [`anti-var-assign`](anti-var-assign.md) - Don't use VAR=VAL syntax
