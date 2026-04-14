# Prompt Color with set_color

**Rule ID**: `prompt-color`
**Priority**: MEDIUM
**Category**: Prompt Design

## What

Use `set_color` to apply colors in shell prompts and output. Supports named colors, hex codes, and 256-color palette indices.

## Why

Fish provides `set_color` as a built-in for terminal colorization, avoiding the need for ANSI escape code sequences. It's more readable, handles terminal capabilities automatically, and supports modern color spaces including true color via hex codes.

## Examples

### ✅ Correct
```fish
# Named colors
set_color red
echo -n "Error"
set_color normal

# Hex color codes (true color)
set_color 5555FF
echo -n "Custom blue"
set_color normal

# 256-color palette
set_color 5    # Blue in 256-color mode
echo -n "Blue text"
set_color normal

# Multiple colors in prompt
function fish_prompt
    set_color cyan
    echo -n (whoami)
    set_color normal
    echo -n '@'
    set_color green
    echo -n (hostname)
    set_color normal
    echo ': ' (prompt_pwd) '> '
end

# Conditional coloring
function fish_prompt
    if test $status -ne 0
        set_color red
    else
        set_color green
    end
    echo -n '❯ '
    set_color normal
end

# Background colors
set_color --background red
echo -n " ERROR "
set_color normal

# Combine foreground and background
set_color yellow --background black
echo -n " Warning "
set_color normal
```

### ❌ Incorrect
```fish
# Using ANSI escape codes directly
echo -e "\033[31mError\033[0m"    # Works but less portable

# Bash prompt escape sequences in fish
set_color '\u'    # ERROR: fish doesn't support bash prompt escapes

# Forgetting to reset colors
set_color red
echo "Error message"
# Color leaks to user's command input
echo "Next command also red"    # Unintended

# Assuming all terminals support true color
set_color '#FF0000'    # May not work on 256-color terminals
```

## Best Practices

```fish
# Always reset to normal
set_color blue
echo -n "Info"
set_color normal    # Always reset!

# Use set_color -o for bold
set_color -o red
echo -n "CRITICAL"
set_color normal

# Use set_color -d for dim
set_color -d blue
echo -n "(debug)"
set_color normal

# Define color constants for themes
set -g theme_color_user cyan
set -g theme_color_host green
set -g theme_color_path blue
set -g theme_color_git yellow
set -g theme_color_normal normal

function fish_prompt
    set_color $theme_color_user
    echo -n (whoami)
    set_color $theme_color_normal
    echo -n '@'
    set_color $theme_color_host
    echo -n (hostname)
    set_color $theme_color_normal
    echo ': ' (prompt_pwd) '> '
end

# Safe: check terminal support
if set_color --print-colors | grep -q 'truecolor'
    set_color 5555FF    # Safe to use hex
else
    set_color blue      # Fallback to named color
end

# Use -b for bold (alias for -o)
set_color -b white
echo -n (prompt_pwd)
set_color normal

# Right prompt with dim colors
function fish_right_prompt
    set_color -d black
    echo -n (date '+%H:%M:%S')
    set_color normal
end
```

## Supported Colors

**Named colors**: black, red, green, yellow, blue, magenta, cyan, white, normal

**Options**: `-o` or `--bold`, `-d` or `--dim`, `-u` or `--underline`, `-r` or `--reverse`, `-b` or `--bold`

**Hex codes**: Any valid 6-digit hex color (e.g., `FF5733`, `5555FF`)

**256-color**: Numbers 0-255

## See Also

- [`prompt-function`](prompt-function.md) - Prompt function definition
- [`func-definition`](func-definition.md) - Function definition syntax
- [`string-replace`](string-replace.md) - For colored output formatting
