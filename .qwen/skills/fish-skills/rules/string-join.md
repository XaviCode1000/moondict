# String Join for Concatenation

**Rule ID**: `string-join`
**Priority**: HIGH
**Category**: String Manipulation

## What

Use `string join` to concatenate list elements with a separator. Use an empty string `''` for no separator between elements.

## Why

Fish provides `string join` as a native way to combine list elements with delimiters, replacing bash's IFS manipulation and external `paste` or `tr` commands. It's efficient and doesn't spawn subprocesses.

## Examples

### ✅ Correct
```fish
# Join with newline separator
string join '\n' $lines
# Outputs each element on its own line

# Join with comma (CSV output)
string join , "apple" "banana" "cherry"
# → apple,banana,cherry

# Join with no separator
string join '' "hello" " " "world"
# → hello world

# Join path components
string join / "home" "user" "documents"
# → home/user/documents

# Capture joined result
set csv_line (string join , $fields)
echo $csv_line

# Join with custom separator
string join ' | ' $log_parts
# → part1 | part2 | part3

# Join array from variable
set -l items one two three
string join '-' $items
# → one-two-three

# Join with tab separator
string join \t $columns
```

### ❌ Incorrect
```fish
# Bash IFS manipulation doesn't work in fish
IFS=,; echo "${array[*]}"    # ERROR: bashism

# Using external paste command unnecessarily
printf '%s\n' $items | paste -sd,    # Unnecessary process spawn

# Manual loop for joining (error-prone)
set result ""
for item in $items
    set result "$result,$item"    # Leading comma problem
end

# Using tr for joining
printf '%s' $items | tr '\n' ','    # Trailing newline issues
```

## Best Practices

```fish
# Build CSV lines from fields
function to_csv --argument-list fields
    string join , $fields
end

# Join only if list has elements
if set -q items[1]
    string join ', ' $items
else
    echo "(empty)"
end

# Combine with string split for transformation
string split , "a,b,c" | string join '-'
# → a-b-c

# Format list for display
echo "Items: " (string join ', ' $items)

# Build query strings
set -l params (string join '&' $key_value_pairs)

# Join file paths with null separator (safe for special chars)
string join \0 $files | xargs -0 process

# Safe: handle empty lists gracefully
set -l joined (string join ', ' $items 2>/dev/null)
if test -z "$joined"
    echo "No items"
end

# Join with shell-safe quoting
string join ' ' (string escape $args)

# Create comma-separated IDs for SQL
set sql_ids (string join ',' (string replace -r '^' "'" $ids | string replace -r '$' "'"))
```

## See Also

- [`string-split`](string-split.md) - Split strings on delimiter
- [`string-replace`](string-replace.md) - Pattern-based string replacement
- [`string-match`](string-match.md) - Pattern matching
