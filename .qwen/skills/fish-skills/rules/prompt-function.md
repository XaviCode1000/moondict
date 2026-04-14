# Prompt via fish_prompt Function

**Rule ID**: `prompt-function`
**Priority**: MEDIUM
**Category**: Prompt Design

## What

Define your shell prompt using the `fish_prompt` function, not by setting a `$PS1` variable like in bash.

## Why

Fish doesn't use prompt variables. Instead, it calls the `fish_prompt` function every time it needs to display the prompt. This allows for dynamic, programmable prompts that can change based on context, directory, git status, and more.

## Examples

### ✅ Correct
```fish
# Simple prompt
function fish_prompt
    echo (prompt_pwd) '> '
end

# Prompt with git branch
function fish_prompt
    set -l cwd (prompt_pwd)
    set -l branch (fish_git_prompt)
    if test -n "$branch"
        echo "$cwd $branch> "
    else
        echo "$cwd> "
    end
end

# Prompt with colors
function fish_prompt
    set_color cyan
    echo -n (whoami)
    set_color normal
    echo -n '@'
    set_color green
    echo -n (hostname)
    set_color normal
    echo -n ':'
    set_color blue
    echo -n (prompt_pwd)
    set_color normal
    echo '> '
end

# Prompt with exit status
function fish_prompt
    set -l last_status $status
    if test $last_status -ne 0
        set_color red
        echo -n "[$last_status] "
    end
    set_color green
    echo -n (prompt_pwd)
    set_color normal
    echo '> '
end

# Minimal prompt
function fish_prompt
    echo '$ '
end
```

### ❌ Incorrect
```fish
# Bash-style PS1 variable - does not work in fish
set PS1 "\u@\h:\w> "    # ERROR: fish doesn't use PS1

# Setting prompt via export
export PS1="> "          # ERROR: has no effect in fish

# Using string replacement to simulate PS1
set -g fish_prompt "..." # ERROR: must be a function
```

## Best Practices

```fish
# Use prompt_pwd for shortened paths
function fish_prompt
    # prompt_pwd respects DIR_LENGTH automatically
    echo (prompt_pwd) '❯ '
end

# Add git status to prompt
function fish_prompt
    set_color blue (prompt_pwd)
    set_color yellow (fish_git_prompt)
    set_color normal '❯ '
end

# Multi-line prompt
function fish_prompt
    set_color cyan
    echo -n (whoami)@(hostname)
    set_color normal
    echo ':' (prompt_pwd)
    set_color green
    echo -n (fish_git_prompt)
    set_color normal
    echo
    echo '> '
end

# Prompt with timestamp
function fish_prompt
    set_color black
    echo -n (date '+%H:%M:%S')
    set_color normal
    echo -n ' '
    set_color blue
    echo -n (prompt_pwd)
    set_color normal
    echo '> '
end

# Safe: handle missing commands gracefully
function fish_prompt
    set_color green
    echo -n (prompt_pwd)
    # fish_git_prompt may not be available
    if functions -q fish_git_prompt
        set_color yellow
        echo -n (fish_git_prompt)
    end
    set_color normal
    echo '> '
end

# Right-side prompt
function fish_right_prompt
    set_color black
    echo -n (date '+%H:%M')
    set_color normal
end
```

## See Also

- [`prompt-color`](prompt-color.md) - Color usage in prompts
- [`func-definition`](func-definition.md) - Function definition syntax
- [`err-status-check`](err-status-check.md) - Checking $status in prompts
