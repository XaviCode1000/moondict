# Main Configuration File

**Rule ID**: `conf-config-fish`  
**Priority**: LOW  
**Category**: Configuration

## What

Put main configuration in `~/.config/fish/config.fish`. Use `conf.d/` for modular configuration.

## Why

`config.fish` is read on startup of every shell. It's the central place for configuration.

## Examples

### ✅ Correct
```fish
# ~/.config/fish/config.fish

# Only run in interactive shells
if status --is-interactive
    set -g fish_greeting "Welcome to fish!"
    set -gx EDITOR nvim
end

# Run for all shells (interactive + login)
if status --is-login
    # Login-specific configuration
    set -gx LANG en_US.UTF-8
end
```

### ❌ Incorrect
```fish
# Don't put heavy operations in config.fish
set -l files (find ~/.config -type f)  # Slow startup

# Don't source bash files
source ~/.bashrc  # Won't work

# Don't use bash syntax
export PATH="$HOME/bin:$PATH"  # Use set -gx
```

## Best Practices

```fish
# Guard interactive-only config
if status --is-interactive
    # Abbreviations
    abbr -a gs git status
    
    # Bindings
    bind \cp history-search-backward
    
    # Prompt customization
    fish_config theme choose default
end

# Fast startup - defer heavy operations
function _lazy_load --on-event fish_postexec
    # Load on first command
    functions -e _lazy_load
    # Heavy initialization here
end

# Use conf.d for modular config
# ~/.config/fish/conf.d/
# ├── 00-env.fish
# ├── 10-paths.fish
# └── 20-aliases.fish
```

## See Also

- [`conf-conf-d`](conf-conf-d.md) - Use conf.d for modular configuration
- [`conf-status-checks`](conf-status-checks.md) - Use status checks
