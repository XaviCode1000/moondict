# String Match with Patterns

**Rule ID**: `string match`
**Priority**: HIGH
**Category**: String Manipulation

## What

Use `string match` to test whether a string matches a glob or regex pattern, or to extract matching portions. Use `-r` for regex, `-i` for case-insensitive, and `-q` for quiet/test mode.

## Why

Fish provides `string match` as a unified tool for pattern matching, replacing external tools like `grep`, `test`, and bash's `[[ =~ ]]` syntax. It works natively without spawning processes.

## Examples

### ✅ Correct
```fish
# Test if string matches a glob pattern
if string match '*.txt' $filename
    echo "Text file detected"
end

# Regex match - validate input format
if string match -r '^\d{4}-\d{2}-\d{2}$' $date
    echo "Valid ISO date format"
end

# Quiet mode for conditionals (no output, just exit status)
if string match -qr '^error:' $line
    echo "Found error line"
end

# Extract matched portions
string match -r '(\w+)@(\w+\.\w+)' "email: user@example.com"
# → user@example.com
# → user
# → example.com

# Case-insensitive matching
if string match -qi 'WARNING' $log_line
    echo "Warning found"
end

# Match multiple patterns with glob
string match -r '(error|warning|critical)' $log
# Returns the matching portion

# Validate numeric input
if string match -qr '^\d+$' $input
    set -l number $input
    echo "Processing number: $number"
end

# Extract domain from URL
set -l domain (string match -r '://([^/]+)' $url)[2]
echo $domain    # → example.com
```

### ❌ Incorrect
```fish
# Using grep for simple matching (spawns external process)
echo $line | grep -q '^error:'    # Unnecessary process spawn

# Using test with bash-style regex
test $var =~ 'pattern'            # ERROR: not valid fish syntax

# Using case statement for simple glob
switch $filename
    case '*.txt'
        echo "text file"
end
# Overkill for single pattern - use string match instead

# Manual character checking
if test (string length $input) -gt 0
    # Checking if not empty
end
# Simpler: just test -n $input
```

## Best Practices

```fish
# Validate email format
function is_email --argument candidate
    string match -qr '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' $candidate
end

# Extract version number from string
set -l version (string match -r 'v?(\d+\.\d+\.\d+)' "app v2.1.0")[2]

# Classify log levels
function classify_log --argument line
    if string match -qr '^ERROR' $line
        echo "error"
    else if string match -qr '^WARN' $line
        echo "warning"
    else if string match -qr '^INFO' $line
        echo "info"
    else
        echo "unknown"
    end
end

# Filter array elements
set -l files *.log
set -l error_logs (string match -r 'error.*\.log' $files)

# Safe: handle no match gracefully
set -l result (string match -r 'pattern: (.*)' $input)
if test $status -eq 0
    echo "Found: $result[2]"
else
    echo "No match found"
end

# Parse structured data
set -l kv (string match -r '^([^=]+)=(.*)$' "KEY=value")
if test $status -eq 0
    set -l key $kv[2]
    set -l val $kv[3]
end
```

## See Also

- [`string-replace`](string-replace.md) - Pattern-based string replacement
- [`string-join`](string-join.md) - Join strings with separator
- [`string-split`](string-split.md) - Split strings on delimiter
