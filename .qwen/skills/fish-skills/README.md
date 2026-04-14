# 🐟 Fish Skills - Comprehensive Fish Shell Guidelines

Best practices and coding guidelines for writing high-quality, idiomatic Fish shell scripts and functions.

## Quick Start

This skill provides **78 rules** across **13 categories**, organized by priority:

| Priority | Categories | When to Apply |
|----------|-----------|---------------|
| **CRITICAL** | Variables, Functions, Syntax | Always - core language rules |
| **HIGH** | Strings, Command Substitution, Paths, Interactive | Common tasks |
| **MEDIUM** | Completions, Prompts, Error Handling, Performance | Advanced features |
| **LOW** | Configuration | Setup and maintenance |
| **REFERENCE** | Anti-patterns | Code review, migration |

## Rule Categories

### Core Language (CRITICAL)

- **Variables & Scoping** (`var-`) - `set` command, scopes, lists, no word splitting
- **Functions** (`func-`) - Definition, arguments, autoloading, event handlers
- **Syntax & Control Flow** (`syn-`) - `if test`, `and/or/not`, `begin/end`, loops

### Common Operations (HIGH)

- **String Manipulation** (`str-`) - `string` builtin for replace, split, match, join
- **Command Substitution** (`cmdsub-`) - `(command)` syntax, newline splitting
- **Paths & Files** (`path-`) - `path` builtin, wildcards, redirections
- **Interactive Features** (`inter-`) - Autosuggestions, abbreviations, themes

### Advanced Features (MEDIUM)

- **Completions** (`comp-`) - Programmable completions for commands
- **Prompt Design** (`prompt-`) - Custom prompts with `fish_prompt`
- **Error Handling** (`err-`) - Status checking, combinators, fallbacks
- **Performance** (`perf-`) - Optimization for low-resource systems

### Setup & Review (LOW/REFERENCE)

- **Configuration** (`conf-`) - `config.fish`, `conf.d/`, environment
- **Anti-patterns** (`anti-`) - Common mistakes, bash-isms to avoid

## Usage Examples

### Writing a New Function

```fish
# Apply rules: func-definition, func-argv-args, var-scope-explicit, func-description
function backup_file --description 'Create timestamped backup'
    set -l source $argv[1]  # var-scope-explicit
    set -l timestamp (date +%Y%m%d_%H%M%S)  # cmdsub-parentheses
    
    if not test -e $source  # syn-if-test
        echo "File not found: $source" >&2  # err-redirect-silence
        return 1  # func-return-status
    end
    
    cp $source "$source.backup.$timestamp"
    echo "Backed up: $source"
end
```

### Creating an Abbreviation

```fish
# Apply rules: abbr-definition, conf-config-fish
abbr -a gs git status
abbr -a gc git commit
abbr -a gco git checkout
```

### Writing a Prompt

```fish
# Apply rules: prompt-function, prompt-color, prompt-pwd, prompt-status
function fish_prompt
    set -l last_status $status  # var-status-not-question
    
    set -l stat
    if test $last_status -ne 0  # syn-if-test
        set stat (set_color red)[$last_status](set_color normal)
    end
    
    string join '' -- \
        (set_color green) (prompt_pwd) \  # prompt-pwd
        (set_color normal) \
        $stat \
        '❯ '
end
```

## Migration from Bash

Key differences to remember:

| Bash | Fish | Rule |
|------|------|------|
| `VAR=VAL` | `set VAR VAL` | `var-set-syntax` |
| `$?` | `$status` | `var-status-not-question` |
| `$1, $2` | `$argv[1], $argv[2]` | `var-argv-not-numbered` |
| `` `cmd` `` | `(cmd)` | `cmdsub-parentheses` |
| `[ ]` or `[[ ]]` | `test` | `syn-if-test` |
| `foo() { }` | `function foo ... end` | `func-definition` |
| `until` | `while not` | `syn-no-until` |
| No word splitting | Word splitting disabled | `var-no-word-split` |

## Hardware-Aware Configuration

For low-resource systems (HDD, 4C, 8GB):

```fish
# Defer heavy operations
set -g _fish_initialized 0

function _fish_lazy_init --on-event fish_prompt
    if test $_fish_initialized -eq 0
        set -g _fish_initialized 1
        # Load completions, plugins, etc.
    end
end

# Use abbreviations over functions (no call overhead)
abbr -a gs git status  # Better than function wrapper

# Limit history to reduce I/O
set -g fish_history_max_count 10000
```

## File Structure

```
fish-skills/
├── SKILL.md           # Main guidelines document
├── AGENTS.md          # Agent-specific instructions
├── README.md          # This file
└── rules/             # Individual rule files
    ├── var-*.md       # Variables & Scoping
    ├── func-*.md      # Functions
    ├── syn-*.md       # Syntax & Control Flow
    ├── str-*.md       # String Manipulation
    ├── cmdsub-*.md    # Command Substitution
    ├── path-*.md      # Paths & Files
    ├── inter-*.md     # Interactive Features
    ├── comp-*.md      # Completions
    ├── prompt-*.md    # Prompt Design
    ├── err-*.md       # Error Handling
    ├── perf-*.md      # Performance
    ├── conf-*.md      # Configuration
    └── anti-*.md      # Anti-patterns
```

## How to Use Rules

1. **Find relevant category** based on task type
2. **Read rule file** for detailed examples
3. **Apply rule ID** in code reviews: `❌ Violates var-set-syntax (line 23)`
4. **Cross-reference** related rules via "See Also" sections

## Sources

- [Fish Shell Official Documentation](https://fishshell.com/docs/current/)
- [Fish for Bash Users](fish_for_bash_users.md)
- [Interactive Use](interactive.md)
- [The Fish Language](language.md)

## License

MIT
