---
name: fish-skills
description: >
  Fish shell scripting guidelines with 78 rules across 13 categories.
  Use when writing, reviewing, or refactoring Fish shell scripts and functions.
  Covers syntax, variables, functions, completions, prompts, and bash migration.
  Invoke with /fish-skills.
  Trigger: fish shell, fish script, config.fish, fish function, fish completion,
  bash to fish migration, .fish file, shell scripting fish
license: MIT
metadata:
  author: gazadev
  version: "1.0.0"
  category: development
  tags: [shell, fish, scripting, automation, cli]
  sources:
    - Fish Shell Official Documentation
    - Fish for Bash Users
    - Fish Interactive Use
    - Fish Language Reference
---

# Fish Shell Best Practices

Comprehensive guide for writing high-quality, idiomatic Fish shell scripts and functions. Contains rules across multiple categories, prioritized by impact to guide LLMs in code generation and refactoring.

## When to Apply

Reference these guidelines when:
- Writing new Fish functions, scripts, or completions
- Configuring `config.fish` or `conf.d/` files
- Creating interactive prompts or key bindings
- Reviewing code for Fish-specific patterns
- Migrating from bash/zsh to Fish
- Optimizing shell performance

## Rule Categories by Priority

| Priority | Category | Impact | Prefix | Rules |
|----------|----------|--------|--------|-------|
| 1 | Variables & Scoping | CRITICAL | `var-` | 12 |
| 2 | Functions | CRITICAL | `func-` | 12 |
| 3 | Syntax & Control Flow | CRITICAL | `syn-` | 12 |
| 4 | String Manipulation | HIGH | `str-` | 10 |
| 5 | Command Substitution | HIGH | `cmdsub-` | 8 |
| 6 | Paths & Files | HIGH | `path-` | 10 |
| 7 | Interactive Features | HIGH | `inter-` | 10 |
| 8 | Completions | MEDIUM | `comp-` | 10 |
| 9 | Prompt Design | MEDIUM | `prompt-` | 8 |
| 10 | Error Handling | MEDIUM | `err-` | 8 |
| 11 | Performance | MEDIUM | `perf-` | 8 |
| 12 | Configuration | LOW | `conf-` | 10 |
| 13 | Anti-patterns | REFERENCE | `anti-` | 12 |

---

## Quick Reference

### 1. Variables & Scoping (CRITICAL)

- [`var-set-syntax`](rules/var-set-syntax.md) - Use `set` for all variable operations, not `VAR=VAL`
- [`var-scope-explicit`](rules/var-scope-explicit.md) - Always specify scope: `-g`, `-l`, `-U`, `-f`
- [`var-export-flag`](rules/var-export-flag.md) - Use `-x`/`-u` flags for exported variables, not separate command
- [`var-lists-native`](rules/var-lists-native.md) - All variables are lists; use list operations naturally
- [`var-no-word-split`](rules/var-no-word-split.md) - No word splitting; quotes around `$var` unnecessary
- [`var-path-suffix`](rules/var-path-suffix.md) - Variables ending in PATH are colon-split automatically
- [`var-status-not-question`](rules/var-status-not-question.md) - Use `$status` not `$?` for exit codes
- [`var-pipestatus-list`](rules/var-pipestatus-list.md) - Use `$pipestatus` for pipeline exit codes
- [`var-fish-pid`](rules/var-fish-pid.md) - Use `$fish_pid` not `$$` for current PID
- [`var-argv-not-numbered`](rules/var-argv-not-numbered.md) - Use `$argv` not `$1`, `$2`, etc.
- [`var-universal-persist`](rules/var-universal-persist.md) - Use `-U` for persistent cross-session variables
- [`var-erase-syntax`](rules/var-erase-syntax.md) - Use `set -e VAR` to erase, not `unset`

### 2. Functions (CRITICAL)

- [`func-definition`](rules/func-definition.md) - Use `function name ... end` syntax, not `name() {}`
- [`func-argv-args`](rules/func-argv-args.md) - Access arguments via `$argv`, not positional parameters
- [`func-autoload`](rules/func-autoload.md) - Save functions in `~/.config/fish/functions/name.fish`
- [`func-alias-wrapper`](rules/func-alias-wrapper.md) - Use `command actual_cmd $argv` to wrap commands
- [`func-event-handler`](rules/func-event-handler.md) - Use `--on-event` for lifecycle hooks
- [`func-var-watch`](rules/func-var-watch.md) - Use `--on-variable` for reactive behavior
- [`func-signal-handler`](rules/func-signal-handler.md) - Use `--on-signal` for signal handling
- [`func-recursive`](rules/func-recursive.md) - Functions can call themselves; no special syntax needed
- [`func-description`](rules/func-description.md) - Add `--description 'text'` to functions
- [`func-save-edit`](rules/func-save-edit.md) - Use `funced` to edit, `funcsave` to persist
- [`func-return-status`](rules/func-return-status.md) - Use `return $status` or `return N`
- [`func-no-subshell`](rules/func-no-subshell.md) - No subshells; use `begin; end` for grouping

### 3. Syntax & Control Flow (CRITICAL)

- [`syn-if-test`](rules/syn-if-test.md) - Use `if test ...` not `if [ ... ]` or `if [[ ... ]]`
- [`syn-and-or-combiner`](rules/syn-and-or-combiner.md) - Use `and`/`or`/`not` combinators
- [`syn-switch-case`](rules/syn-switch-case.md) - Use `switch/case` with wildcards, no fallthrough
- [`syn-for-loop`](rules/syn-for-loop.md) - Use `for x in list ... end` for iteration
- [`syn-while-loop`](rules/syn-while-loop.md) - Use `while condition ... end`
- [`syn-begin-block`](rules/syn-begin-block.md) - Use `begin; ...; end` for grouping, not `( ... )`
- [`syn-no-until`](rules/syn-no-until.md) - Use `while not` or `while !` instead of `until`
- [`syn-semicolon-end`](rules/syn-semicolon-end.md) - Separate commands with `;` or newlines
- [`syn-test-float`](rules/syn-test-float.md) - `test` supports floating point comparisons
- [`syn-test-query`](rules/syn-test-query.md) - Use `set -q var` to check existence
- [`syn-end-block`](rules/syn-end-block.md) - All blocks end with `end` keyword
- [`syn-comment-hash`](rules/syn-comment-hash.md) - Comments start with `#`; no multiline comments

### 4. String Manipulation (HIGH)

- [`string-sub-command`](rules/string-sub-command.md) - Use `string sub` for substring extraction
- [`string-replace`](rules/string-replace.md) - Use `string replace` for pattern replacement
- [`string-split`](rules/string-split.md) - Use `string split` for delimiter-based splitting
- [`string-match`](rules/string-match.md) - Use `string match` with regex or glob patterns
- [`string-join`](rules/string-join.md) - Use `string join` to concatenate with separator
- [`string-length`](rules/string-length.md) - Use `string length` for character/cell width
- [`string-upper-lower`](rules/string-upper-lower.md) - Use `string upper`/`string lower` for case
- [`string-trim`](rules/string-trim.md) - Use `string trim` to remove whitespace
- [`string-repeat`](rules/string-repeat.md) - Use `string repeat` for repetition
- [`string-escape`](rules/string-escape.md) - Use `string escape` for safe quoting

### 5. Command Substitution (HIGH)

- [`cmdsub-parentheses`](rules/cmdsub-parentheses.md) - Use `(command)` or `$(command)` syntax
- [`cmdsub-no-backtick`](rules/cmdsub-no-backtick.md) - No backtick syntax; use parentheses only
- [`cmdsub-newline-split`](rules/cmdsub-newline-split.md) - Splits on newlines only, not whitespace
- [`cmdsub-quote-single`](rules/cmdsub-quote-single.md) - Quote with `"` to keep as single argument
- [`cmdsub-pipe-source`](rules/cmdsub-pipe-source.md) - Pipe into `source` instead of `<(cmd)`
- [`cmdsub-collect`](rules/cmdsub-collect.md) - Use `string collect` to control splitting
- [`cmdsub-status`](rules/cmdsub-status.md) - Check `$status` after command substitution
- [`cmdsub-nested`](rules/cmdsub-nested.md) - Nest substitutions freely: `(cmd1 (cmd2))`

### 6. Paths & Files (HIGH)

- [`path-command`](rules/path-command.md) - Use `path` builtin for path manipulation
- [`path-dirname-basename`](rules/path-dirname-basename.md) - Use `path dirname`/`path basename`
- [`path-extension`](rules/path-extension.md) - Use `path extension` to get file extension
- [`path-change`](rules/path-change.md) - Use `path change` to modify path components
- [`path-filter`](rules/path-filter.md) - Use `path filter` to test existence
- [`wildcard-star`](rules/wildcard-star.md) - Use `*` for single-level globbing
- [`wildcard-recursive`](rules/wildcard-recursive.md) - Use `**` for recursive directory search
- [`wildcard-no-match`](rules/wildcard-no-match.md) - Non-matching globs fail command (not nullglob)
- [`redirect-stderr`](rules/redirect-stderr.md) - Redirect stderr with `2>file`
- [`redirect-both`](rules/redirect-both.md) - Redirect both with `&>file` or `&>>file`

### 7. Interactive Features (HIGH)

- [`autosuggestion-toggle`](rules/autosuggestion-toggle.md) - Toggle with `$fish_autosuggestion_enabled`
- [`abbr-definition`](rules/abbr-definition.md) - Use `abbr -a name expansion` for abbreviations
- [`abbr-regex`](rules/abbr-regex.md) - Use `--regex` and `--function` for dynamic abbreviations
- [`highlight-variables`](rules/highlight-variables.md) - Customize with `fish_color_*` variables
- [`theme-selection`](rules/theme-selection.md) - Use `fish_config theme choose` for themes
- [`history-search`](rules/history-search.md) - Search history with `ctrl-r` or `up`
- [`pager-navigation`](rules/pager-navigation.md) - Navigate completions with arrows, tab, ctrl-s
- [`vi-mode`](rules/vi-mode.md) - Enable with `fish_vi_key_bindings`
- [`key-binding`](rules/key-binding.md) - Use `bind` to customize key bindings
- [`editor-functions`](rules/editor-functions.md) - Command line has copy/paste, search, navigation

### 8. Completions (MEDIUM)

- [`comp-complete-command`](rules/comp-complete-command.md) - Use `complete -c cmd` for command completions
- [`comp-short-long`](rules/comp-short-long.md) - Define `-s` short and `-l` long options
- [`comp-arguments`](rules/comp-arguments.md) - Use `-a` for argument completions
- [`comp-condition`](rules/comp-condition.md) - Use `-n` for conditional completions
- [`comp-description`](rules/comp-description.md) - Use `-d` for completion descriptions
- [`comp-exclusive`](rules/comp-exclusive.md) - Use `-x` for exclusive options
- [`comp-force-files`](rules/comp-force-files.md) - Use `-f` to suppress file completions
- [`comp-load-path`](rules/comp-load-path.md) - Completions in `$fish_complete_path`
- [`comp-save-file`](rules/comp-save-file.md) - Save in `~/.config/fish/completions/cmd.fish`
- [`comp-test`](rules/comp-test.md) - Test with `complete -C "cmd partial"`

### 9. Prompt Design (MEDIUM)

- [`prompt-function`](rules/prompt-function.md) - Define via `fish_prompt` function
- [`prompt-right`](rules/prompt-right.md) - Right prompt via `fish_right_prompt`
- [`prompt-mode`](rules/prompt-mode.md) - Mode indicator via `fish_mode_prompt`
- [`prompt-color`](rules/prompt-color.md) - Use `set_color` for coloring
- [`prompt-pwd`](rules/prompt-pwd.md) - Use `prompt_pwd` for shortened directory
- [`prompt-status`](rules/prompt-status.md) - Display `$status` for non-zero exits
- [`prompt-transient`](rules/prompt-transient.md) - Use `--final-rendering` for transient prompts
- [`prompt-save`](rules/prompt-save.md) - Save with `funcsave fish_prompt`

### 10. Error Handling (MEDIUM)

- [`err-status-check`](rules/err-status-check.md) - Check `$status` after commands
- [`err-combiner-short`](rules/err-combiner-short.md) - Use `cmd1 && cmd2; and echo ok; or echo fail`
- [`err-command-query`](rules/err-command-query.md) - Use `command -sq cmd` to test existence
- [`err-test-file`](rules/err-test-file.md) - Use `test -e`, `test -f`, `test -d` for files
- [`err-glob-empty`](rules/err-glob-empty.md) - Non-matching globs cause command failure
- [`err-redirect-silence`](rules/err-redirect-silence.md) - Silence with `2>/dev/null`
- [`err-try-fallback`](rules/err-try-fallback.md) - Use `cmd1; or cmd2` for fallback
- [`err-no-set-e`](rules/err-no-set-e.md) - No `set -e`; check status explicitly

### 11. Performance (MEDIUM)

- [`perf-no-subshell`](rules/perf-no-subshell.md) - No subshell overhead; `begin/end` is free
- [`perf-list-iteration`](rules/perf-list-iteration.md) - Iterate lists directly: `for x in $list`
- [`perf-string-builtins`](rules/perf-string-builtins.md) - Use `string` builtin over external tools
- [`perf-path-filter`](rules/perf-path-filter.md) - Use `path filter` over `test -e` for batches
- [`perf-count-builtin`](rules/perf-count-builtin.md) - Use `count $list` over `wc -l`
- [`perf-math-float`](rules/perf-math-float.md) - `math` handles floats natively
- [`perf-no-fork-builtin`](rules/perf-no-fork-builtin.md) - Prefer builtins to avoid fork overhead
- [`perf-conf-d-lazy`](rules/perf-conf-d-lazy.md) - `conf.d/` scripts run at startup; keep minimal

### 12. Configuration (LOW)

- [`conf-config-fish`](rules/conf-config-fish.md) - Main config in `~/.config/fish/config.fish`
- [`conf-conf-d`](rules/conf-conf-d.md) - Use `conf.d/` for modular configuration
- [`conf-status-checks`](rules/conf-status-checks.md) - Use `status --is-interactive` and `--is-login`
- [`conf-fish-add-path`](rules/conf-fish-add-path.md) - Use `fish_add_path` for safe PATH addition
- [`conf-universal-vars`](rules/conf-universal-vars.md) - Use `-U` vars for cross-session settings
- [`conf-greeting`](rules/conf-greeting.md) - Customize greeting via `$fish_greeting`
- [`conf-title`](rules/conf-title.md) - Set terminal title via `fish_title` function
- [`conf-delta`](rules/conf-delta.md) - Use `fish_delta` to see customizations
- [`conf-no-profile`](rules/conf-no-profile.md) - No `/etc/profile` reading; fish is standalone
- [`conf-env-inherit`](rules/conf-env-inherit.md) - Inherits environment from parent process

### 13. Anti-patterns (REFERENCE)

- [`anti-var-assign`](rules/anti-var-assign.md) - Don't use `VAR=VAL` to set variables
- [`anti-unwrap-question`](rules/anti-unwrap-question.md) - Don't use `$?`; use `$status`
- [`anti-backtick`](rules/anti-backtick.md) - Don't use backticks for command substitution
- [`anti-word-split`](rules/anti-word-split.md) - Don't quote variables to prevent word splitting
- [`anti-subshell-group`](rules/anti-subshell-group.md) - Don't use `( cmd; cmd )` for grouping
- [`anti-until-loop`](rules/anti-until-loop.md) - Don't look for `until`; use `while not`
- [`anti-heredoc`](rules/anti-heredoc.md) - Don't use heredocs; use `printf` or `echo`
- [`anti-arithmetic`](rules/anti-arithmetic.md) - Don't use `$((...))`; use `math`
- [`anti-stringly-vars`](rules/anti-stringly-vars.md) - Don't use colon-separated strings; use lists
- [`anti-ps1-prompt`](rules/anti-ps1-prompt.md) - Don't set `$PS1`; define `fish_prompt` function
- [`anti-export-separate`](rules/anti-export-separate.md) - Don't use separate `export` command
- [`anti-set-e-exit`](rules/anti-set-e-exit.md) - Don't expect `set -e` behavior; check status

---

## Recommended Fish Configuration

### `~/.config/fish/config.fish`
```fish
# Only run in interactive shells
if status --is-interactive
    # Greeting
    set -g fish_greeting "Welcome to fish!"

    # Editor
    set -gx EDITOR nvim

    # PATH additions
    fish_add_path ~/.local/bin
    fish_add_path ~/go/bin
end

# Run for all shells (interactive + login)
if status --is-login
    # Login-specific configuration
end
```

### `~/.config/fish/conf.d/` Structure
```
~/.config/fish/conf.d/
├── 00-env.fish      # Environment variables
├── 10-paths.fish    # PATH modifications
├── 20-aliases.fish  # Abbreviations and functions
└── 90-final.fish    # Final configuration
```

---

## How to Use

This skill provides rule identifiers for quick reference. When generating or reviewing Fish code:

1. **Check relevant category** based on task type
2. **Apply rules** with matching prefix
3. **Prioritize** CRITICAL > HIGH > MEDIUM > LOW
4. **Read rule files** in `rules/` for detailed examples

### Rule Application by Task

| Task | Primary Categories |
|------|-------------------|
| New function | `func-`, `var-`, `syn-` |
| Script file | `syn-`, `err-`, `cmdsub-` |
| Configuration | `conf-`, `var-`, `perf-` |
| Prompt | `prompt-`, `inter-` |
| Completions | `comp-`, `path-` |
| Interactive use | `inter-`, `abbr-` |
| Code review | `anti-`, `var-` |
| Bash migration | `anti-`, `syn-`, `var-` |

---

## Fish-Specific Concepts

### Variables Are Lists
Every variable in Fish is a list. A "scalar" is just a list with one element.

```fish
set name "single"        # One element
set files *.txt          # Multiple elements
echo $files[1]           # Access by index
echo $files[-1]          # Negative indexing
echo $files[2..4]        # Slicing
```

### No Word Splitting
Unlike bash, Fish does not split variables on whitespace:

```fish
set foo "bar baz"
ls $foo    # Looks for file named "bar baz", not "bar" and "baz"
```

### Scopes
| Flag | Scope | Persistence |
|------|-------|-------------|
| `-l` / `--local` | Current function/block | Until block exits |
| `-g` / `--global` | Current shell session | Until session ends |
| `-U` / `--universal` | All sessions | Persistent across restarts |
| `-f` / `--function` | Function scope | Deprecated, use `--local` |

### Command Separation
```fish
# Same line with semicolons
echo foo; echo bar

# Multiple lines
echo foo
echo bar

# Background job
sleep 5 &
```

---

## 🐟 Fish Shell Optimization for Low-Resource Systems

### Hardware-Aware Configuration

For systems with HDD + 4C + 8GB RAM:

#### Startup Optimization
```fish
# ~/.config/fish/config.fish
# Defer heavy operations to first interactive use
set -g _fish_initialized 0

function _fish_lazy_init --on-event fish_prompt
    if test $_fish_initialized -eq 0
        # Load heavy completions only once
        set -g _fish_initialized 1
    end
end
```

#### History Optimization
```fish
# Limit history file size to reduce HDD I/O
set -g fish_history_max_count 10000
set -g fish_history_max_age 30d
```

#### Abbreviations Over Functions
```fish
# Abbreviations expand on type, no function call overhead
abbr -a gs git status
abbr -a gc git commit
abbr -a gco git checkout
```

---
