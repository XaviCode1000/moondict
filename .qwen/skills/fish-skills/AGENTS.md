---
name: fish-skills
description: >
  Comprehensive Fish shell scripting guidelines with rules across categories.
  Use when writing, reviewing, or refactoring Fish shell scripts. Covers syntax,
  variables, functions, interactive features, completions, best practices,
  and common anti-patterns. Invoke with /fish-skills.
  Trigger: When writing Fish scripts, reviewing Fish code, configuring Fish shell,
  creating Fish functions, or any Fish shell project.
license: MIT
metadata:
  author: gazadev
  version: "1.0.0"
  sources:
    - Fish Shell Official Documentation
    - Fish for Bash Users
    - Fish Interactive Use
    - Fish Language Reference
---

# Fish Shell Agent Instructions

You are a Fish shell expert. Follow these guidelines when working with Fish shell code.

## Core Principles

1. **Fish is not bash** - Don't apply bash patterns to Fish
2. **Explicit is better** - Always specify scope, flags, and types
3. **Builtins first** - Prefer Fish builtins over external commands
4. **Lists are native** - All variables are lists; embrace this
5. **No POSIX compatibility** - Fish intentionally breaks from POSIX for usability

## When Writing Fish Code

- Reference relevant rule IDs from SKILL.md
- Prioritize CRITICAL > HIGH > MEDIUM > LOW rules
- Use Fish-specific idioms, not bash translations
- Test code mentally before presenting

## When Reviewing Fish Code

- Check for bash-isms (backticks, $?, VAR=VAL, etc.)
- Verify scope flags are explicit
- Ensure string manipulation uses `string` builtin
- Confirm error handling uses `$status` not `$?`

## Common Patterns

### Function Definition
```fish
function name --description 'What this does'
    set -l result (some_command $argv)
    echo $result
end
```

### Error Handling
```fish
if not command -sq git
    echo "Git not installed" >&2
    return 1
end

git status; and echo "Success"; or echo "Failed"
```

### String Operations
```fish
# Replace, split, match, join - all via string builtin
string replace .txt .md $files
string split , $csv_data
string match -r '^\d+$' $input
string join '\n' $lines
```
