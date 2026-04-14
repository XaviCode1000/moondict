# Modular Configuration with conf.d

**Rule ID**: `conf-conf-d`
**Priority**: LOW
**Category**: Configuration

## What

Use `~/.config/fish/conf.d/*.fish` files for modular configuration that runs automatically on shell startup. Files are executed in alphabetical order.

## Why

Instead of putting everything in `config.fish`, modular configuration files in `conf.d/` provide better organization, easier maintenance, and the ability to enable/disable features by renaming files. Each file runs automatically when fish starts, in alphabetical order.

## Examples

### ✅ Correct
```fish
# ~/.config/fish/conf.d/00-env.fish
# Environment variables
set -gx EDITOR nvim
set -gx VISUAL nvim
set -gx BROWSER firefox
set -gx LANG en_US.UTF-8

# ~/.config/fish/conf.d/10-paths.fish
# PATH modifications
fish_add_path $HOME/.local/bin
fish_add_path $HOME/.cargo/bin
fish_add_path /opt/homebrew/bin

# ~/.config/fish/conf.d/20-aliases.fish
# Abbreviations (fish's superior aliases)
abbr -a g git
abbr -a gs git status
abbr -a gc git commit
abbr -a ll ls -lh

# ~/.config/fish/conf.d/30-prompt.fish
# Prompt configuration
set -g theme_color_scheme tokyonight

# ~/.config/fish/conf.d/40-functions.fish
# Custom functions
function mkcd
    mkdir -p $argv[1]
    and cd $argv[1]
end
```

### ❌ Incorrect
```fish
# Everything in config.fish (monolithic)
# ~/.config/fish/config.fish
set -gx EDITOR nvim
set -gx PATH $PATH:/home/user/.cargo/bin
# ... 200 more lines of mixed config ...
# Hard to maintain and debug

# Using .bashrc patterns
if test -f ~/.bashrc    # Don't source bash files in fish
    source ~/.bashrc
end

# Overwriting PATH instead of appending
set -gx PATH "/new/path:$PATH"    # String manipulation, not list
# Use fish_add_path instead

# Putting everything in one conf.d file
# ~/.config/fish/conf.d/everything.fish
# Still defeats the purpose of modularization
```

## Best Practices

```fish
# Naming convention with prefixes
# 00- - Environment variables
# 10- - PATH modifications
# 20- - Abbreviations and aliases
# 30- - Prompt and UI config
# 40- - Custom functions
# 50- - Plugin configuration
# 90- - User overrides

# Guard against non-interactive shells
if status is-interactive
    # Interactive-only config
    abbr -a g git
end

# Use fish_add_path for safe PATH management
# Automatically avoids duplicates
fish_add_path $HOME/.local/bin
fish_add_path /snap/bin

# Conditional configuration
if command -q docker
    abbr -a d docker
    abbr -a dc docker-compose
end

if command -q git
    # Git-specific config
    abbr -a g git
    abbr -a gs git status
end

# Platform-specific configuration
switch (uname)
    case Linux
        fish_add_path /home/linuxbrew/.linuxbrew/bin
    case Darwin
        fish_add_path /opt/homebrew/bin
end

# Safe: wrap potentially failing commands
if command -q starship
    starship init fish | source
end

# Document each conf.d file
# ~/.config/fish/conf.d/10-paths.fish
# Development tool paths
# Added: 2024-01-15
fish_add_path $HOME/.cargo/bin
fish_add_path $HOME/.local/bin

# List active conf.d files
function list_config
    ls -1 ~/.config/fish/conf.d/*.fish
end
```

## Configuration File Loading Order

```
1. /etc/fish/config.fish (system-wide)
2. ~/.config/fish/config.fish (user)
3. /etc/fish/conf.d/*.fish (system modules, alphabetical)
4. ~/.config/fish/conf.d/*.fish (user modules, alphabetical)
5. /etc/fish/functions/*.fish (system functions)
6. ~/.config/fish/functions/*.fish (user functions)
```

## See Also

- [`conf-config-fish`](conf-config-fish.md) - Main config.fish file
- [`abbr-definition`](abbr-definition.md) - Abbreviation definitions
- [`func-definition`](func-definition.md) - Function definitions
- [`func-autoload`](func-autoload.md) - Function autoloading
